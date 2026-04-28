#!/usr/bin/env python3
"""
generate_weekly_report.py — 自动生成每周技能进化报告

从git log和hermes memory中收集本周的真实变更，
生成markdown报告并发布到 ai-creator-dashboard 仓库。

Usage:
    python3 generate_weekly_report.py [--output-dir ./reports]
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

REPO_PATH = os.path.expanduser("~/digital-products/ai-creator-dashboard-template")
if not os.path.exists(REPO_PATH):
    # Fallback: use cwd if running inside repo
    REPO_PATH = "."

MEMORY_FILE = os.path.expanduser("~/.hermes/.hermes_state.json")
SKILL_DIR = os.path.expanduser("~/.hermes/skills")

def run_git_log(days=7):
    """Get git commits from the last N days."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--stat"],
            capture_output=True, text=True, cwd=REPO_PATH, timeout=30
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def get_skill_changes():
    """Detect recently modified skills."""
    changes = []
    for root, dirs, files in os.walk(SKILL_DIR):
        for f in files:
            if f == "SKILL.md":
                path = os.path.join(root, f)
                mtime = os.path.getmtime(path)
                mod_date = datetime.fromtimestamp(mtime)
                if mod_date > datetime.now() - timedelta(days=7):
                    skill_name = os.path.basename(os.path.dirname(path))
                    parent = os.path.basename(os.path.dirname(os.path.dirname(path)))
                    changes.append({
                        "name": skill_name,
                        "category": parent,
                        "modified": mod_date.strftime("%Y-%m-%d")
                    })
    return changes

def get_system_stats():
    """Get basic stats about the system."""
    skills = sum(len(files) for _, _, files in os.walk(SKILL_DIR) if "SKILL.md" in files)
    skill_categories = len([d for d in os.listdir(SKILL_DIR) if os.path.isdir(os.path.join(SKILL_DIR, d))])
    
    return {
        "total_skills": skills,
        "skill_categories": skill_categories,
        "report_date": datetime.now().strftime("%Y-%m-%d"),
    }

def generate_report():
    git_log = run_git_log()
    skill_changes = get_skill_changes()
    stats = get_system_stats()
    
    report = []
    report.append("# 红皇每周技能进化报告")
    report.append("")
    report.append(f"> 报告周期: {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} → {stats['report_date']}")
    report.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Section 1: 技能变更
    report.append("## 🧠 技能库变更")
    report.append("")
    if skill_changes:
        report.append(f"本周有 **{len(skill_changes)}** 个技能文件被修改：")
        report.append("")
        report.append("| 技能 | 分类 | 修改日期 |")
        report.append("|------|------|----------|")
        for c in sorted(skill_changes, key=lambda x: x["modified"], reverse=True):
            report.append(f"| {c['name']} | {c['category']} | {c['modified']} |")
    else:
        report.append("本周无技能文件变更。")
    report.append("")
    report.append(f"**当前状态**: 共 {stats['total_skills']} 个技能，分布于 {stats['skill_categories']} 个分类。")
    report.append("")
    
    # Section 2: 代码提交
    report.append("## 📦 本周代码提交")
    report.append("")
    report.append("```")
    if git_log and "Error" not in git_log:
        report.append(git_log.strip())
    else:
        report.append("(无法获取git日志)")
    report.append("```")
    report.append("")
    
    # Section 3: 能力状态
    report.append("## 📊 能力层级状态")
    report.append("")
    report.append("| 层级 | 状态 | 说明 |")
    report.append("|------|------|------|")
    report.append("| L1 | ✅ | 基础工具链：终端/文件/网络/浏览器 |")
    report.append("| L2 | ✅ | 认知框架：规划/审计/执行/反思 |")
    report.append("| L3 | ✅ | 工作流引擎：四角色Agent闭环 |")
    report.append("| L4 | ⚠️ | 自主决策：需要持续验证 |")
    report.append("| L5 | ❌ | 多Agent联邦调度 |")
    report.append("")
    
    # Section 4: 产品状态
    report.append("## 🛒 产品状态")
    report.append("")
    report.append("- **AI Creator Efficiency Dashboard** — $9 (0.003 ETH)")
    report.append("- **部署**: GitHub Pages + PR自动验证")
    report.append("- **购买渠道**: GitHub PR / 网页")
    report.append("- **验证**: Etherscan API V2 + 地址比对防伪")
    report.append("")
    
    # Section 5: 下周计划
    report.append("## 🔮 下周计划")
    report.append("")
    report.append("_此部分由创造者填写_")
    report.append("")
    
    report.append("---")
    report.append(f"*红皇 · 自动生成于 {stats['report_date']}*")
    
    return "\n".join(report)

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    report = generate_report()
    
    filename = f"weekly-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w") as f:
        f.write(report)
    
    print(f"Report generated: {filepath}")
    print(f"Size: {len(report)} chars")
    return filepath

if __name__ == "__main__":
    main()
