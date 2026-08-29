# Paper Note: residual-learning-dmp-2008.07682

## Bibliographic record

- Title: Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation
- Authors: Todor Davchev; Kevin Sebastian Luck; Michael Burke; Franziska Meier; Stefan Schaal; Subramanian Ramamoorthy
- Venue and year: IEEE Robotics and Automation Letters, 2022
- DOI: 10.1109/LRA.2022.3150024
- Publisher URL: https://doi.org/10.1109/LRA.2022.3150024
- Preprint or code URL: https://arxiv.org/abs/2008.07682
- Discovery source and access date: OpenAlex; Crossref; 2026-08-29
- Full-text access route (publisher, school portal, repository, or preprint): arXiv public preprint (version 5)
- Full-text file and SHA-256: `/mnt/research-data/literature/pdfs/residual-learning-dmp-2008.07682.pdf`; `5fa3052910e8f140cde854663cc0d0929c91044b9b223d3fbda14f815a22f6cd`
- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): preprint

## Translation and terminology

- Abstract translation: 接触和摩擦丰富的插入任务很难仅靠示范得到稳定策略。作者提出 residual Learning from Demonstration (rLfD)，将示范学习得到的动态运动基元 (DMP) 作为基策略，再用模型无关强化学习学习任务空间残差。结果表明，直接作用于末端完整位姿的残差能提升插入成功率、泛化能力和跨几何/摩擦条件的少样本适应，同时保持较温和的关节运动。方法在 MuJoCo/Robosuite 仿真和 Franka Panda 实机上的 peg、gear、RJ-45 插入任务中评估。
- Important terms and preferred Chinese/English wording: `demonstration` 示范；`dynamic movement primitive (DMP)` 动态运动基元；`residual policy` 残差策略；`task-space correction` 任务空间修正；`full-pose residual` 完整位姿残差；`insertion` 插入；`jiggling exploration` 局部抖动探索；`few-shot transfer` 少样本迁移。
- Sentences or equations needing a second pass: 四元数残差的符号和奖励权重需结合原 PDF/作者代码复核；文本提取对公式下标存在排版噪声。

## Technical digest

- Problem and claimed gap: DMP 能快速复现示范，但在接触插入中对微小初始位姿、倾斜、摩擦和几何变化敏感；已有参数空间或耦合项适配没有回答“残差应作用于 DMP 的哪一层”，也难覆盖完整位姿。论文比较 forcing-term、coupling-term、平移任务空间和完整位姿残差。
- Method and key equations: DMP 基策略由示范轨迹离线拟合，平移策略使用位置/速度，姿态策略使用四元数/角速度。残差策略输出末端速度修正，最终命令为 DMP 命令与残差的组合，并送入阻抗控制器。DMP 形式为 `y_dot = (alpha_v (beta_v (g-x) - tau y) + f_omega + C_t) / tau^2`；探索噪声可注入 forcing term、phase-modulated coupling term 或直接注入任务空间。姿态残差在四元数/轴角表示中组合，避免欧拉角奇异。
- Sensors, observations, actions, and controller interface: 示范通过 HTC Vive tracker 采集；仿真/实机策略使用本体状态和 DMP 状态，残差动作是末端线速度/角速度修正。DMP 100 Hz，残差策略 10 Hz，最终命令由 500 Hz 实时阻抗控制器执行。论文未给出足以复现实机传感器标定、滤波和全部限幅的完整接口。
- Simulation platform and task details: 使用 MuJoCo/Robosuite，Franka Panda 7-DoF。任务为 peg、gear 和 RJ-45 插入；peg 有 easy/hard 初始偏差与孔间隙设置，gear 和 RJ-45 还测试姿态偏差。每回合最长 10 s，基策略执行约 3.9 s 后启用残差。
- Dataset or demonstrations: 每项任务使用一条成功示范构建 DMP；仿真初始位姿在示范附近采样，实机测试使用均匀采样的位姿/方向偏差。原始轨迹和完整数据集不在论文仓库中。
- Training procedure and compute: 比较 SAC 与 PPO 的模型无关残差策略；网络为全连接 ReLU（SAC 配置和每次迭代更新数在方法段给出），采用稀疏成功奖励。完整训练约 500 episodes；跨任务迁移只需 3 次更新、约 60 episodes/15 分钟。确切 batch、学习率、随机种子、硬件和停止准则未完整报告。
- Reproduction-critical constants and missing details: 关键频率为 100/10/500 Hz，回合上限 10 s，残差在基策略执行 3.9 s 后启用；表 IV/VI/V 给出主要成功率、迁移和速度。缺少完整奖励权重、随机种子、接触参数、控制器增益、动作边界、传感器噪声/延迟、实机安全阈值及可复用资产。

## Experimental design analysis

- Baselines and whether comparisons are fair: 无修正 DMP、线性残差、随机残差、平移 PPO、完整位姿 PPO/SAC、hybrid switching 和纯模型无关策略。任务、初始采样和回合长度基本一致，但不同策略的网络/探索预算和动作表示不同，不能视为完全等预算比较。
- Metrics and statistical treatment: 主要指标是插入成功率、平均执行时间和总广义力；表格给出均值 ± 误差，但未明确所有置信区间/统计检验和失败分类。当前项目应补充真实力 RMSE、峰值力、穿透、接触丢失和安全门触发次数。
- Ablations and what they establish: 平移、forcing/coupling、随机及完整位姿残差的对比说明任务空间、完整位姿非线性残差更适合接触插入；PPO/PPO 在表 IV 平均成功率 86.9%，优于无修正 DMP 的 31.4%。这证明接口选择的重要性，不证明对所有机器人或接触任务普适。
- Real-robot evidence and sim-to-real procedure: 在 Franka Panda 上执行 peg、gear、RJ-45；实机表面约 1 度倾斜，完整位姿残差对未见起始偏差更稳健。跨任务从 gear/RJ-45 迁移时，约 60 episodes 达到接近完整 500-episode 训练的效果。论文没有提供可复用的标定报告、统一仿真/实机指标或硬件安全审计，因此不能直接作为本项目真机安全证据。
- Failure cases and missing controls: DMP 对偏差和摩擦敏感；平移-only 无法处理姿态要求，随机残差可能增加脆弱插头受力；作者指出力大小优化、接触序列和参数化仍待研究。缺少 held-out 摩擦/刚度/延迟网格、力传感器误差、主动限力和系统化失败复盘。
- Evidence locations (section/table/figure/equation): Fig. 1 为两速率架构；Eq. (1) 为 DMP/探索注入；Fig. 2 为探索位置；Table I/II/III 为 peg 适配比较；Table IV 为完整位姿成功率；Table V 为速度；Table VI 为跨任务迁移；Section III-D/IV 为训练与实验细节；Section V 为局限和结论。

## Assessment

- Strengths: 将示范先验与低频 RL 残差结合，降低探索成本；完整位姿任务空间接口覆盖接触插入中的姿态误差；同时报告仿真、实机、速度和迁移结果。
- Weaknesses and hidden assumptions: 需要可靠示范、已知目标和合适阻抗控制器；接触状态主要由本体/任务状态隐含表示；安全处理和力优化不完整；成功率提升可能依赖任务几何、倾斜和手工调参。
- Reproducibility: what is available and what is missing: 公开预印本、公式、频率、任务和主要结果可用；完整代码、资产、奖励、种子、控制器参数、传感器标定和安全阈值缺失，精确复现受限。
- Relevance to the project vision: 直接支持“快速透明力控环 + 慢速有界学习层”的 MuJoCo-first 研究接口，但不改变当前 platform-neutral 约束，也不提供具体机械臂真机部署授权。
- Candidate extension or research gap: 系统回答“残差修改轨迹、增益还是关节命令”对未见接触动力学的影响，并用相同评估代码连接离线真机 replay；重点检验力误差下降是否伴随安全指标不恶化。

## Follow-up experiment in MuJoCo

在现有接触场景固定 PI 快环，比较 PI-only、trajectory/gain/joint residual；残差低频运行并保持动作边界，训练/测试按 episode 隔离，加入 held-out 摩擦、刚度、噪声和延迟，记录力 RMSE、穿透、峰值力、接触丢失和安全门。该实验只验证可证伪的仿真接口，不构成具体机械臂真机证据。

## Actions

- [ ] Add metadata to the literature index/Zotero
- [x] Save the PDF outside Git
- [ ] Reproduce the smallest reported result
- [ ] Create or update a project config
- [x] Link this note from an experiment record
