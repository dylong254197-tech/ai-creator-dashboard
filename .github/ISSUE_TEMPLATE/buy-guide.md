---
name: 🛒 购买产品
about: 查看产品列表、价格，以及如何使用 PR 下单购买的完整流程
title: ''
labels: ''
assignees: ''
---

# 🛒 如何购买

## 📦 当前可购买产品

| 产品 | 价格 | 说明 |
|------|------|------|
| AI Creator Efficiency Dashboard | **$9 (0.003 ETH)** | 面向AI创作者的Notion全能指挥中心，4个互联数据库，17个预建视图 |

> 更多产品见 [product_config.json](../blob/main/product_config.json)

## 💳 付款地址

```
0x2cb55e288c404daf69d4cacbeadd9ae3aba25ffb
```

使用任意以太坊钱包（MetaMask、Rabby 等）向此地址转账对应金额。

## 📋 购买步骤

### 第1步：付款
向以上地址转账对应 ETH，确保 gas 足够让交易确认。

### 第2步：创建 PR
1. 点击仓库右上角 **Fork**（如未 Fork）
2. 切换到你的 Fork 仓库
3. 点击 **Pull Requests** → **New Pull Request**
4. 在模板下拉框中选择 **Buy Product**
5. 填写以下信息：

```
产品名称：AI Creator Efficiency Dashboard
付款哈希：0x...（交易哈希，66字符）
我的钱包地址：0x...（你发起交易的地址）
```

### 第3步：等待自动验证
提交 PR 后，系统会自动：
1. ✅ 在以太坊链上验证交易哈希
2. ✅ 比对转账金额和收款地址
3. ✅ 验证通过 → Bot 在 PR 评论中回复下载链接
4. ✅ PR 自动合并并标记为已交付

> 验证通常 1-5 分钟完成。

## ⚠️ 注意事项

- 付款哈希必须是 `0x` 开头的 66 字符十六进制字符串
- 钱包地址必须填写**发起这笔交易**的地址（系统会与链上比对）
- 不要使用他人的交易哈希（地址不匹配会导致验证失败）
- 如遇问题请在此 Issue 中留言

## 🆘 帮助

**如何获取交易哈希？** 在 MetaMask 或 etherscan.io 中找到你的转账记录，复制交易哈希（0x开头，66字符）。
