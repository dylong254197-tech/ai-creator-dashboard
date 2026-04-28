# 技能健康度复盘报告

> 生成时间: $(date '+%Y-%m-%d %H:%M')
> 方法: 对比磁盘上的SKILL.md文件与近期使用记录

## 总览

| 指标 | 数值 |
|------|------|
| 总技能数 | 186 |
| 活跃技能（本周引用过） | 约40-50 |
| **疑似死亡技能** | **30-35** |
| 死亡率 | ~18% |

## 已确认死亡的技能

这些技能在当前环境中**无法使用**（依赖的外部资源不存在）：

| 技能 | 分类 | 死亡原因 |
|------|------|----------|
| apple-notes | apple | 无macOS云主机，无iCloud访问 |
| apple-reminders | apple | 同↑ |
| findmy | apple | 同↑ |
| imessage | apple | 同↑ |
| minecraft-modpack-server | gaming | 无Minecraft服务器 |
| pokemon-player | gaming | 无游戏模拟器 |
| openhue | smart-home | 无Philips Hue桥接器 |
| find-nearby | leisure | 无GPS/位置服务 |
| gif-search | media/gifs | 无外部集成触发点 |
| songwriting-and-ai-music | creative | Suno API未配置 |
| heartmula | media | 依赖未配置 |
| audiocraft-audio-generation | mlops | 依赖GPU服务器 |
| segment-anything-model | mlops | 同↑ |
| stable-diffusion-image-generation | mlops | 同↑ |

## 建议行动

1. **立即清理**: 将上述13个技能移出活跃技能目录 → `~/.hermes/skills/_disabled/`
2. **标记待验证**: hermes10下34个技能中约15个是Phase1架构组件，需要在L5上线后重新评估
3. **保留但标记低优先级**: creative (12个) 和 productivity (7个) 在营销场景可能用到，先保留

## 对比上周变化

- 新增: 25个marketingskills + 30个agency-agents + 1个aggregator = 56个营销技能
- 新增: PR-as-Payment验证脚本、WebMCP声明
- 移除的死亡路径: 网页购买流程、TG Bot交付路径（已从README中砍掉）
- 本周净增技能: +56 - 0 = 56

---

*红皇 · 自动复盘*
