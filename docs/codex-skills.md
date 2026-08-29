# Codex 科研技能清单

本项目的技能安装在本机 Codex 用户目录中，不写入仓库，也不会自动改变服务器环境。调用技能只需要在 Codex 对话中明确任务；Codex 会按任务类型选择对应技能，并遵守本仓库的 `AGENTS.md` 和 `docs/PROJECT_VISION.md`。

## 已安装并可用

| Skill | 用途 | 典型调用 |
| --- | --- | --- |
| `literature-search` | 跨 OpenAlex、Crossref、Semantic Scholar、arXiv 等公开源发现和去重论文 | “检索 2020 年后机械臂接触力控论文，按顶刊和会议分组” |
| `paper-fulltext-harvest` | 对 DOI 列表批量获取合法 PDF/XML；门户登录仍由用户完成 | “用学校门户下载这些 DOI 的授权全文” |
| `paper-reading` | 对 PDF 做速读、标准研读或深度分析，提取方法、公式、实验和局限 | “深度研读这个 PDF，并映射到 MuJoCo 实验” |
| `related-work-survey` | 按研究轴建立 taxonomy、研究空白和 Related Work 叙事 | “围绕柔顺接触操作做系统综述” |
| `zotero-management` | 管理 Zotero 条目、去重、标签和阅读队列 | “把这篇论文加入 Active Projects/force-control” |
| `mujoco-workbench` | MuJoCo 场景、接触任务和工作台流程路由 | “运行当前 MuJoCo 场景并检查接触状态” |
| `mujoco-scene-authoring` | 编写或修改场景、机器人加载器、相机和任务计划 | “给双接触任务增加一个可复现实验场景” |
| `mujoco-run-debug` | 运行、快照、视频导出和调试 MuJoCo 实验 | “用固定 seed 跑 smoke test 并导出快照” |
| `mujoco-phase-contracts` | 检查阶段契约、状态不变量和可观测证据 | “为这个场景补齐 phase contract” |
| `ros2-engineering-skills` | ROS 2、QoS、tf2、ros2_control、MoveIt 2 和部署诊断 | “在确定 ROS 发行版后审查 ros2_control 接口” |
| `academic-figure-generation` | 从方法和 caption 生成论文级框架图、流程图和系统图 | “根据实验方法生成一张系统框架图” |
| `embodied-ai-paper-writer` | CoRL/RSS/ICRA/IROS 风格的具身智能论文写作与润色 | “把这一段实验结果改成 CoRL 风格” |

## 暂缓项

- `NVIDIA/skills`：官方目录，等确定 Isaac/Omniverse 或 CUDA 专项需求后按需安装。
- `mjlab-skillkit`：只有迁移到 Isaac Lab 时才安装；当前 MuJoCo 主线不需要。
- Zotero、Tavily、W&B 等外部服务：技能已具备，但未配置账户、密钥或自动上传。

技能不会替代证据边界：公开索引只用于发现，正式全文必须来自学校门户、出版社或合法开放获取来源。门户密码、Cookie、验证码和私钥不得发送给 Codex。PDF 放在 `/mnt/research-data/literature/pdfs/`，仓库只保存结构化笔记、来源和哈希。

## 推荐使用顺序

```text
literature-search -> paper-reading -> related-work-survey
-> docs/proposals/ -> MuJoCo skills -> evaluation -> academic-figure-generation
-> embodied-ai-paper-writer
```

开始新的代码分支时，在请求中写明：先阅读 `docs/PROJECT_VISION.md`，分支名、stage gate、验证命令和预期 artifact。这样技能调用和分支门禁会落在同一条可复现链路上。

