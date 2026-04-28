#!/usr/bin/env python3
"""
verify_pr.py — PR-as-Payment 自动验证脚本

在 GitHub Actions 中运行，验证买家提交的 PR 是否包含有效的 ETH 付款。
验证通过后自动评论下载链接并合并 PR。

Usage:
    python3 verify_pr.py <pr_number>

Environment:
    GITHUB_TOKEN       — GitHub API token (secrets.GITHUB_TOKEN)
    ETHERSCAN_API_KEY  — Etherscan API key (secrets.ETHERSCAN_API_KEY)
    GITHUB_REPOSITORY  — owner/repo (自动由 GH Actions 设置)
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
import base64

# ============================================================
# Config (from local product_config.json)
# ============================================================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "dylong254197-tech/ai-creator-dashboard")

GITHUB_API = f"https://api.github.com/repos/{REPO}"

# ============================================================
# GitHub API helpers
# ============================================================
def gh_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "verify-pr-script/1.0"
    }


def gh_get(path):
    url = f"{GITHUB_API}/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers=gh_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def gh_post(path, data):
    url = f"{GITHUB_API}/{path.lstrip('/')}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=gh_headers(), method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def gh_patch(path, data):
    url = f"{GITHUB_API}/{path.lstrip('/')}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=gh_headers(), method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def gh_put(path, data):
    url = f"{GITHUB_API}/{path.lstrip('/')}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=gh_headers(), method="PUT")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def add_pr_comment(pr_number, body):
    return gh_post(f"issues/{pr_number}/comments", {"body": body})


def add_pr_labels(pr_number, labels):
    return gh_post(f"issues/{pr_number}/labels", {"labels": labels})


def remove_pr_label(pr_number, label):
    try:
        req = urllib.request.Request(
            f"{GITHUB_API}/issues/{pr_number}/labels/{urllib.parse.quote(label)}",
            headers=gh_headers(),
            method="DELETE"
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 404  # label already gone, fine
        raise


def merge_pr(pr_number):
    return gh_put(f"pulls/{pr_number}/merge", {
        "merge_method": "squash",
        "commit_title": f"✅ [Auto-delivery] PR #{pr_number}"
    })


# ============================================================
# Product config loader
# ============================================================
def load_config():
    """Load product_config.json from local file (relative to script path)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "..", "product_config.json")
    config_path = os.path.normpath(config_path)
    with open(config_path, "r") as f:
        return json.loads(f.read())


# ============================================================
# PR body parser
# ============================================================
def parse_pr_body(body):
    """
    从PR正文中提取字段。支持灵活的格式匹配。
    返回 dict 或 None （解析失败）。
    """
    if not body:
        return None

    result = {}

    # Product name - support markdown list format: "- **名称**: value" or "名称：value"
    m = re.search(r'(?i)(?:-\s+\*{0,2})?产品名称(?:\*{0,2})\s*[：:]\s*(.+?)(?:\n|$)', body)
    if m:
        candidate = m.group(1).strip().strip('*').strip()
        # Reject if it looks like a markdown heading or section separator
        if not candidate.startswith('#') and not candidate.startswith('---') and len(candidate) > 0:
            result["product_name"] = candidate

    # Payment hash (0x + 64 hex, accept longer too and trim)
    m = re.search(r'(?i)(?:-\s+\*{0,2})?付款哈希(?:\*{0,2})\s*[：:]\s*(0x[a-fA-F0-9]{64,})', body)
    if m:
        result["tx_hash"] = m.group(1).strip()[:66]  # trim to 0x+64

    # Wallet address (0x + 40 hex) - support markdown list
    m = re.search(r'(?i)(?:-\s+\*{0,2})?(?:我的)?钱包地址(?:\*{0,2})\s*[：:]\s*(0x[a-fA-F0-9]{40})', body)
    if m:
        result["wallet_address"] = m.group(1).strip().lower()

    # Amount
    m = re.search(r'(?i)付款金额\s*[：:]\s*([\d.]+)\s*ETH', body)
    if m:
        result["amount_eth"] = m.group(1).strip()

    # Payment timestamp (optional)
    m = re.search(r'(?i)付款时间戳\s*[：:]\s*(.+?)(?:\n|$)', body)
    if m:
        result["timestamp"] = m.group(1).strip()

    # Check required fields
    if "product_name" not in result or "tx_hash" not in result or "wallet_address" not in result:
        return None

    return result


# ============================================================
# Etherscan API
# ============================================================
def call_etherscan(action, module="proxy", **params):
    """Call Etherscan API V2. Uses chainid=1 for Ethereum mainnet."""
    query_parts = [
        f"module={module}",
        f"action={action}",
        "chainid=1",
    ] + [f"{k}={v}" for k, v in params.items()]
    if ETHERSCAN_API_KEY:
        query_parts.append(f"apikey={ETHERSCAN_API_KEY}")
    url = "https://api.etherscan.io/v2/api?" + "&".join(query_parts)
    req = urllib.request.Request(url, headers={"User-Agent": "verify-pr/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def verify_transaction(tx_hash, expected_to, expected_from, min_wei):
    """
    验证交易的核心逻辑。
    返回 (is_valid: bool, details: list[str])
    """
    details = []

    # Step 1: Lookup transaction by hash
    tx_data = call_etherscan("eth_getTransactionByHash", txhash=tx_hash)
    if "error" in tx_data and "result" not in tx_data:
        if tx_data.get("error", ""):
            return False, [f"❌ Etherscan API 错误: {tx_data['error']}"]
        return False, [f"❌ 交易哈希未找到"]

    result = tx_data.get("result")
    if not result or result is None:
        return False, [f"❌ 交易哈希不存在或未确认"]

    if isinstance(result, dict) and result.get("blockNumber") is None:
        return False, [f"❌ 交易尚未被打包确认（pending），请稍后再试"]

    # Step 2: Check 'to' address
    tx_to = result.get("to", "").lower()
    if tx_to != expected_to.lower():
        return False, [
            f"❌ 收款地址不匹配",
            f"   交易收款方: {tx_to}",
            f"   预期收款方: {expected_to.lower()}"
        ]

    # Step 3: Check 'from' address matches PR's declared wallet
    tx_from = result.get("from", "").lower()
    if tx_from != expected_from.lower():
        return False, [
            f"❌ 钱包地址与交易发起方不匹配（防伪验证）",
            f"   交易发起方: {tx_from}",
            f"   PR声明地址: {expected_from.lower()}",
            f"   请确保你的钱包地址填写的是发起这笔交易的地址"
        ]

    # Step 4: Check value >= min_wei
    tx_value = int(result.get("value", "0"), 16) if isinstance(result.get("value"), str) and result["value"].startswith("0x") else int(result.get("value", 0))
    if tx_value < min_wei:
        return False, [
            f"❌ 转账金额不足",
            f"   交易金额: {tx_value} wei ({tx_value / 10**18:.6f} ETH)",
            f"   最低要求: {min_wei} wei ({min_wei / 10**18:.6f} ETH)"
        ]

    # All checks passed
    tx_value_eth = tx_value / 10**18
    return True, [
        f"✅ 支付已确认！",
        f"   - 交易哈希: {tx_hash}",
        f"   - 转账金额: {tx_value_eth:.6f} ETH",
        f"   - 交易发起方: {tx_from}",
        f"   - 区块确认: ✓",
    ]


# ============================================================
# Delivery URL builder
# ============================================================
def build_delivery_url(config, product_id):
    """Build the raw download URL from private repo."""
    base = config.get("delivery_base_url", "")
    product_config = None
    for p in config.get("products", []):
        if p.get("id") == product_id:
            product_config = p
            break
    if not product_config:
        return None
    delivery_file = product_config.get("delivery_file", "")
    return f"{base}/{product_id}/{delivery_file}"


# ============================================================
# Main
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: verify_pr.py <pr_number>")
        sys.exit(1)

    pr_number = int(sys.argv[1])

    # Load config
    try:
        config = load_config()
        print(f"Config loaded: {len(config.get('products', []))} product(s)")
    except Exception as e:
        comment = f"❌ 无法加载产品配置: {e}\n\n请稍后再试或联系管理员。"
        add_pr_comment(pr_number, comment)
        print(f"ERROR: Config load failed: {e}")
        sys.exit(1)

    # Get PR details
    try:
        pr = gh_get(f"pulls/{pr_number}")
        pr_body = pr.get("body", "")
        pr_title = pr.get("title", "")
        pr_author = pr.get("user", {}).get("login", "unknown")
        print(f"PR #{pr_number}: {pr_title} by @{pr_author}")
    except Exception as e:
        add_pr_comment(pr_number, f"❌ 无法读取 PR #{pr_number}: {e}")
        print(f"ERROR: PR fetch failed: {e}")
        sys.exit(1)

    # Parse PR body
    parsed = parse_pr_body(pr_body)
    if not parsed:
        comment = (
            "❌ **无法解析PR正文，缺少必填字段**\n\n"
            "请确保包含以下字段：\n"
            "- **产品名称**: 从产品列表中选择\n"
            "- **付款哈希**: 0x开头66字符的交易哈希\n"
            "- **钱包地址**: 发起交易的以太坊地址\n\n"
            "请关闭此PR，按照模板重新提交。"
        )
        add_pr_comment(pr_number, comment)
        add_pr_labels(pr_number, ["payment-pending"])
        print(f"PARSE FAILED: missing required fields in PR body")
        sys.exit(0)

    product_name = parsed["product_name"]
    tx_hash = parsed["tx_hash"].lower()
    wallet_address = parsed["wallet_address"].lower()

    print(f"Parsed: product={product_name}, tx={tx_hash[:20]}..., wallet={wallet_address[:10]}...")

    # Match product
    matched_product = None
    for p in config.get("products", []):
        if p.get("name", "").lower() == product_name.lower() or \
           p.get("id", "").lower() == product_name.lower():
            matched_product = p
            break
    
    # Fuzzy match
    if not matched_product:
        for p in config.get("products", []):
            if product_name.lower() in p.get("name", "").lower() or \
               p.get("id", "").lower() in product_name.lower():
                matched_product = p
                break

    if not matched_product:
        available = ", ".join([f'"{p["name"]}"' for p in config.get("products", [])])
        comment = (
            f"❌ **产品 \"{product_name}\" 未找到**\n\n"
            f"当前可购买产品: {available}\n\n"
            f"请确认产品名称，关闭此PR后重新提交。"
        )
        add_pr_comment(pr_number, comment)
        add_pr_labels(pr_number, ["payment-pending"])
        print(f"PRODUCT NOT FOUND: {product_name}")
        sys.exit(0)

    # ============================================================
    # Test mode: if config has test_config, use it for verification
    # This allows running a real end-to-end test with a known tx hash
    # without needing a real payment to the production wallet.
    # ============================================================
    test_config = config.get("test_config")
    is_test_mode = "[TEST]" in pr_title.upper()
    
    if is_test_mode and test_config:
        print(f"TEST MODE: using test_config for verification")
        # Override verification parameters with test values
        tx_hash = test_config.get("test_tx_hash", tx_hash).lower()
        expected_to = test_config.get("wallet_address", expected_to).lower()
        expected_from = test_config.get("test_from", expected_from).lower()
        min_wei = test_config.get("price_wei", min_wei)
        wallet_address = expected_from  # Use test from address as declared wallet
        product_id = "ai-creator-dashboard"  # Force product
        print(f"  TEST: tx_hash={tx_hash[:20]}..., to={expected_to[:10]}..., from={expected_from[:10]}..., min_wei={min_wei}")
    else:
        product_id = matched_product["id"]
        min_wei = matched_product["price_wei"]
        expected_to = config["wallet_address"]
        expected_from = wallet_address

    print(f"Matched product: {matched_product['name']} ({product_id}), min_wei={min_wei}")

    # Verify transaction
    is_valid, details = verify_transaction(tx_hash, expected_to, expected_from, min_wei)

    if is_valid:
        delivery_url = build_delivery_url(config, product_id)
        if not delivery_url:
            comment = (
                "✅ **支付已确认**，但交付文件配置异常。\n\n"
                "请联系管理员手动交付。"
            )
            add_pr_comment(pr_number, comment)
            print(f"WARNING: delivery_url not built for product_id={product_id}")
            sys.exit(0)

        comment = (
            "### ✅ **支付验证通过！**\n\n"
            + "\n".join(details) +
            f"\n\n### 📥 下载链接\n"
            f"请下载 [Notion模板文件]({delivery_url}) 并导入到你的 Notion 工作区。\n\n"
            f"### 📖 导入指南\n"
            f"1. 下载以上zip文件\n"
            f"2. 在 Notion 中点击 `Settings & Members` → `Import` → `Upload`\n"
            f"3. 选择下载的zip文件\n"
            f"4. 按照 `README.md` 中的说明创建数据库\n\n"
            f"---\n"
            f"*感谢你的购买！如有问题请回复此PR或联系 @HoHug_bot*"
        )
        add_pr_comment(pr_number, comment)
        add_pr_labels(pr_number, ["delivered"])
        # Remove payment-pending label
        remove_pr_label(pr_number, "payment-pending")

        # Auto-merge the PR as delivery record
        try:
            merge_result = merge_pr(pr_number)
            print(f"PR merged: {merge_result.get('merged', False)}")
        except Exception as e:
            print(f"PR merge failed (non-critical): {e}")

        print(f"✅ DELIVERY COMPLETE for PR #{pr_number}")
    else:
        comment = (
            "### ❌ **支付验证失败**\n\n"
            + "\n".join(details) +
            f"\n\n### 下一步\n"
            f"1. 请检查你填入的信息是否正确\n"
            f"2. 确认已向收款地址 `{expected_to}` 转账\n"
            f"3. 确认填写的钱包地址是发起交易的地址\n"
            f"4. 关闭此PR，修正信息后重新提交"
        )
        add_pr_comment(pr_number, comment)
        add_pr_labels(pr_number, ["payment-pending"])
        print(f"❌ VERIFICATION FAILED for PR #{pr_number}")
        print(f"  Reasons: {details}")


if __name__ == "__main__":
    # urllib.parse is needed for label quoting in remove_pr_label
    import urllib.parse
    main()
