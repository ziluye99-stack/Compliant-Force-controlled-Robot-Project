# Paper Note: contact-survey-104224

## Bibliographic record

- Title: A Survey of Robot Manipulation in Contact
- Authors: Markku Suomalainen; Yiannis Karayiannidis; Ville Kyrki
- Venue and year: Robotics and Autonomous Systems, 2022 (arXiv:2112.01942v3)
- DOI: 10.1016/j.robot.2022.104224
- Publisher URL: https://doi.org/10.1016/j.robot.2022.104224
- Preprint or code URL: https://arxiv.org/abs/2112.01942v3
- Discovery source and access date: OpenAlex; Crossref; Semantic Scholar; 2026-08-29
- Full-text access route (publisher, school portal, repository, or preprint): arXiv author manuscript v3; publisher DOI cross-check
- Full-text file and SHA-256: `/mnt/research-data/literature/pdfs/contact-survey-104224.pdf`; `f31948cc21d9da3cb0c3570ef1d6214be000c48a37a31839c4f30b8cbe5922a2`
- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): preprint

## Translation and terminology

- Abstract translation: 本综述讨论机器人执行需要持续或变化环境接触的操作任务。这类任务要求机器人显式或隐式地控制接触力，或利用接触来降低不确定性。文章按接触任务、控制方式、技能表示以及规划/学习方法组织现有工作，覆盖装配、打磨、推挤、工具使用和服务任务。
- Important terms and preferred Chinese/English wording: `manipulation in contact` 译为“接触操作”；`direct force control` 译为“直接力控制”；`hybrid force/position control` 译为“混合力/位置控制”；`parallel force/position control` 译为“并行力/位置控制”；`impedance control` 译为“阻抗控制”；`admittance control` 译为“导纳控制”；`contact state` 译为“接触状态”；`exception strategy` 译为“异常/失败恢复策略”。本项目统一使用“力/力矩传感器（F/T sensor）”和“接触力跟踪”。
- Sentences or equations needing a second pass: Table 2 的投影矩阵符号依赖表面法向量，不能直接套用于双接触或全身任务；论文的分类综述不提供统一的跨论文数值汇总。

## Technical digest

- Problem and claimed gap: 接触不是单纯的碰撞约束，而是可用于定位、对齐和完成任务的交互信号。综述的目标是整理接触任务、低层控制、技能表示和规划/学习之间的关系，而不是提出单一新控制器。
- Method and key equations: 对非冗余机器人，混合力/位置控制使用表面法向量 `n` 构造法向投影 `N = n n^T` 和切向投影 `Q = I - n n^T`，将力误差和位置误差分配到不同子空间。阻抗控制的核心关系为 `M(p_ddot - p_d_ddot) + K_D(p_dot - p_d_dot) + K_P(p - p_d) = -f`。导纳控制则将测得外力输入质量-阻尼-弹簧滤波器，产生供内层运动控制器使用的参考状态。
- Sensors, observations, actions, and controller interface: 直接/混合力控通常需要高频力反馈，PI 是常见选择，因为力测量噪声使微分项不可靠。观测可来自腕部 F/T 传感器、关节力矩/电流估计或触觉；动作可以是关节力矩、速度、末端位姿、力设定值或阻抗/导纳参数。传感器位置、法向量、坐标系和内外环频率必须明确。
- Simulation platform and task details: 文章覆盖插入、拧螺丝、擦拭、打磨、推挤、开门、工具使用等接触任务。讨论 RL 时明确提到 MuJoCo、RLBench、Meta-World、SAPIEN 和 ReForm；MuJoCo 适合安全探索和大规模数据，但仿真接触与真实接触不同。
- Dataset or demonstrations: 规划方法使用接触状态、几何/CAD 或力阈值；LfD 使用人工示范、DMP 和力/阻抗轨迹；RL 通过仿真交互或示范初始化。综述没有提供可直接下载的统一数据集。
- Training procedure and compute: 该文是分类综述，不报告统一训练预算、硬件或算力；不同论文的训练/规划设置不可直接横向比较。
- Reproduction-critical constants and missing details: 复现单篇方法仍需查原论文的增益、采样率、滤波、接触参数、限幅和失败判据。综述指出许多工作缺少异常策略、动力学随机化和完整现实差距验证。

## Experimental design analysis

- Baselines and whether comparisons are fair: 综述按方法家族归类，没有统一基线或重新实现，因此不能据此声称某一控制器优于另一控制器。它建议把简单力控/阻抗控制作为可解释基线，再比较规划、LfD 和 RL。
- Metrics and statistical treatment: 各被引工作使用任务成功、力误差、接触状态、轨迹误差、执行时间或异常恢复等指标，但综述不做统一统计检验。对本项目，必须单独报告 true-force RMSE、峰值力、穿透量、接触丢失率和安全门触发。
- Ablations and what they establish: 综述没有统一消融；分类本身支持一个设计选择：分别测试轨迹、力设定值和阻抗/导纳参数的学习接口，而不把它们混为一个动作空间。
- Real-robot evidence and sim-to-real procedure: 文章汇总了大量真实机器人任务，但没有共同的 sim-to-real 协议。RL 部分指出系统辨识、观测噪声和动力学随机化可减小现实差距，同时强调闭环能力必须由真实物理实验验证。
- Failure cases and missing controls: 变形物体、摩擦和刚度不确定性、接触异常、卡死、狭小间隙和非典型恢复仍是薄弱环节；很多工作只报告成功案例，缺少失败率、恢复时间、传感器偏差和安全边界。
- Evidence locations (section/table/figure/equation): Sections 2--2.4 分类接触任务；Section 3.1 和 Table 2 比较直接/混合/并行力控；Sections 3.2--3.3 给出阻抗和导纳定义；Sections 4--5 讨论技能表示、规划、RL 和 LfD；Section 5.2 讨论仿真、MuJoCo、系统辨识和 domain randomization；Section 6 总结变形物体、异常策略、现实差距和模拟器改进方向。

## Assessment

- Strengths: 覆盖面广且结构清楚；把低层控制、技能表示和规划/学习串成层级流程；明确区分直接力控、阻抗和导纳；指出接触可用于定位而不只是需要避免的碰撞。
- Weaknesses and hidden assumptions: 作为综述，它没有统一实验协议或元分析；Table 2 的简单模型假设非冗余、已知表面法向量，难以直接覆盖双接触和人形全身动力学；对中文研究和硬件安全报告覆盖有限。
- Reproducibility: what is available and what is missing: 术语、控制结构和代表性方程可复核，且 DOI/arXiv 版本可取得；但单篇论文的参数、数据和代码需要逐篇追溯，不能由综述复现统一 benchmark。
- Relevance to the project vision: 直接支持 MuJoCo-first、先透明快环再加学习层的路线；同时要求把接触模式、传感器、控制频率、异常恢复和现实差距作为实验变量，而不是只报告任务成功率。
- Candidate extension or research gap: 综述揭示了“学习何种低层接口”与“如何保持安全和跨动力学泛化”之间缺少受控比较。本项目的两速率残差矩阵正是一个窄而可证伪的补充，但结果只能作为 MuJoCo 任务局部证据。

## Follow-up experiment in MuJoCo

在现有一维接触夹具上保持 PI 快环和安全限幅不变，比较“轨迹命令残差”“力控增益残差”和“联合残差”在摩擦、接触刚度、测量噪声、执行器延迟四类留出条件下的 true-force RMSE、穿透、峰值力、接触丢失率和安全门触发。再增加一个接触丢失/恢复阶段，验证综述指出的异常策略缺口。

## Actions

- [ ] Add metadata to the literature index/Zotero
- [x] Save the PDF outside Git
- [ ] Reproduce the smallest reported result
- [ ] Create or update a project config
- [ ] Link this note from an experiment record
