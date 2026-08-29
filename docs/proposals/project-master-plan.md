# 总方案：MuJoCo 优先的接触力控与具身机器人研究链路

## 状态与边界

- Status: `draft`
- Project priorities: compliant interaction, embodied learning, simulation-to-real transfer, evidence and reproducibility
- Stage gate advanced: Question and experiment design
- Simulator decision: MuJoCo is the primary simulator for the first implementation phase.
- Hardware decision: no robot, F/T sensor, controller, or ROS distribution is selected; hardware commands remain disabled.
- Review trigger: update this proposal after the first MuJoCo benchmark, the authorized Chinese full-text intake, and platform selection.

这份 proposal 是项目的总拆分，不替代具体实验记录。每个子任务必须先阅读
`docs/PROJECT_VISION.md`，建立 `docs/tasks/<branch>.md`，并留下可复现的
配置、验证命令和失败结果。

## 总研究问题

在接触动力学、摩擦、传感器噪声和执行器延迟发生变化时，如何让具身机器人
保持可解释、可约束且可迁移的接触力控？第一阶段只验证一个可证伪的
平台无关问题：

> 在 MuJoCo 平面二连杆接触任务中，20 Hz 的有界残差策略叠加在 500 Hz
> 等效的 PI 力控环上，能否降低留出动力学条件下的真实法向力 RMSE，且不
> 增加穿透、峰值接触力、接触丢失或命令限幅违规？

最小否证结果是：在固定 seed、相同初始状态和相同安全限值下，PI-only 与
一个残差接口完成短时对照；若残差没有降低 RMSE，或任一预注册安全指标
恶化，则保留为负结果/不确定结果，不继续扩大训练或声称迁移有效。

## 文献证据门

正式设计证据按以下顺序核验：Web of Science/SCI 对应的正式出版物，
IEEE T-RO/RA-L/T-ASE/T-MECH、IJRR、Automatica，RSS/CoRL/ICRA/IROS，
Nature/Nature Machine Intelligence/Science/Science Robotics，以及 CNKI/万方。
SCI 是索引，不等于全文。

OpenAlex、Crossref、Semantic Scholar 和 arXiv 只用于候选发现、DOI 核验、
版本去重和引用链；GitHub 代码只作为实现线索。受限全文由用户通过学校门户
App 下载到 `/mnt/research-data/literature/pdfs/`，再交给 Codex 做全文提取、
翻译、公式解释、优缺点、实验设计和不足分析。每篇进入 proposal 的论文都
需要 DOI/数据库编号、正式 URL、发现源、全文源、访问日期、PDF 路径和
SHA-256；否则标记为 `metadata-only`，不能支撑性能或研究空白结论。

## 首个 MuJoCo 基准

### 场景和接口

- 场景：零重力平面二连杆、球形 TCP、摩擦平面；MuJoCo timestep `0.002 s`。
- 快速控制：PI + 速度阻尼，等效 500 Hz；广义力和穿透限值在控制器前后都检查。
- 学习层：20 Hz 更新，输出保持 25 个快速步；先比较 `pi_only` 和一个
  `joint_residual`，再扩展 trajectory/gain residual。
- 观测：法向/切向接触力、目标力、广义速度、积分误差和当前基线控制量；
  所有单位使用 SI，shape 由 `configs/platform_neutral_interface.yaml` 冻结。
- 动作：有界广义力，范围 `[-30, 30] N`；非有限或越界动作采用
  `hold_last_safe_command`，绝不进入硬件接口。

### 变量、控制和指标

| 维度 | 训练/控制值 | 留出或对照 | 目的 |
| --- | --- | --- | --- |
| 控制器 | PI-only；joint residual | 同一初始状态和 seed | 判断残差增益是否真实 |
| 目标法向力 | `3--7 N` | `4 N`、`6 N` | 避免单目标结论 |
| 摩擦/刚度 | 训练区间内随机化 | 区间外或组合外 | 检查动力学外推 |
| 传感器噪声/延迟 | 配置化随机化 | 未见噪声和延迟 | 检查观测与命令鲁棒性 |
| seed | `101, 202, 303` | 按 episode 划分 | 报告方差而非单次最好值 |
| 接触负载 | 法向；法向+切向 | `0` 和 `1 N` 切向对照 | 暴露摩擦耦合 |

主要指标为真实接触力 RMSE 和尾段绝对误差；同时报告测量力 RMSE、最大
穿透、峰值接触力、接触丢失率、命令/力矩限幅违规、安全门激活次数和恢复
时间。所有失败 episode 保留在 `results.json`，不因失败而删除。

## 阶段拆分与退出条件

| 阶段 | 主要产物 | 进入条件 | 退出条件 |
| --- | --- | --- | --- |
| 1. 愿景/文献 | 搜索日志、全文笔记、gap statement | 项目愿景已读 | 至少一条可被实验否证的 gap |
| 2. 系统设计 | 平台/传感器记录、接口 YAML、参数证据表 | 任务和指标固定 | 单位、shape、限值和安全边界可审查 |
| 3. MuJoCo 基线 | 场景、PI 控制器、固定 seed smoke | 系统接口通过 | 接触、力指标、确定性和限值测试通过 |
| 4. 数据/训练 | 数据 schema、episode split、基线 checkpoint | 基线可重复 | 训练/验证/测试无泄漏，环境锁定 |
| 5. 留出评测 | 多 seed、消融、失败矩阵、统计区间 | 训练配置提交 | 结果由同一评测代码生成 |
| 6. Sim-to-real | 实测噪声/摩擦/延迟、MuJoCo 标定、离线 replay | 真实平台资料齐全 | 实测参数映射和回放门通过 |
| 7. 监督真机 | 电机禁用、低速低增益、watchdog、E-stop、回滚 | 操作员签字 | 受限命令下可停止、可回滚、可复现 |
| 8. 论文/发布 | 图表、公式、配置、manifest、限制和负结果 | 评测/安全门通过 | 第三方可按 commit 重建关键结果 |

## 分支依赖

```text
literature-intake
      -> first-mujoco-contact-baseline
      -> two-rate-residual-training
      -> heldout-evaluation-and-ablations
platform-and-sensor-freeze
      -> mujoco-calibration
      -> offline-replay
      -> supervised-hardware
evaluation + replay -> paper-figures-and-release
```

分支只处理一个产物。服务器上的仿真、训练和批量评测只能在用户目录运行；
当前共享工作站没有已验证 Slurm，因此在实验室提供调度器或明确预约规则前，
不得直接占用 GPU 做长任务。笔记本负责编辑、轻量 MuJoCo、测试、可视化和
未来的监督式真机调试；大型 artifacts、PDF、checkpoint、视频和日志归档到
`/mnt/research-data`，源代码和配置只通过 GitHub 同步。

## 当前决策与待输入

- 已决定：先使用 MuJoCo 平台无关接触基准；先做透明 PI，再做有界残差。
- 已决定：所有结果记录 seed、Git commit、环境锁、配置、资源信息和 artifact 路径。
- 待输入：三篇通过学校门户取得的中文全文（导纳、阻抗/混合位置力、人形多接触）。
- 待输入：第一台机器人、F/T 传感器、固件、控制模式、通信频率、限位、watchdog 和 E-stop。
- 禁止外推：平台无关 MuJoCo 指标不能直接声称真实机械臂或人形机器人有效。
