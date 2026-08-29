# Paper Note: variable-compliance-peg-in-hole-2020

## Bibliographic record

- Title: Variable Compliance Control for Robotic Peg-in-Hole Assembly: A Deep-Reinforcement-Learning Approach
- Authors: Cristian C. Beltran-Hernandez; Damien Petit; Ixchel G. Ramirez-Alpizar; Kensuke Harada
- Venue and year: Applied Sciences, 2020, 10, 6923
- DOI: 10.3390/app10196923
- Publisher URL: https://doi.org/10.3390/app10196923
- Preprint or code URL: not supplied
- Discovery source and access date: OpenAlex; Crossref; 2026-08-30
- Full-text access route (publisher, school portal, repository, or preprint): MDPI open access PDF (mdpi-res.com)
- Full-text file and SHA-256: `/mnt/research-data/literature/pdfs/variable-compliance-peg-in-hole-2020.pdf`; `a62ce99a979a2abe96a0fd9168fd785bdd4f4fc3cdb7fadec8c072e51117aa03`
- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): full-text

## Translation and terminology

- Abstract translation: 工业机器人在现代制造业中发挥着重要作用，但在非结构化环境中安全地完成复杂、高精度装配仍然困难。本文针对目标孔位存在不确定性的插入任务，提出一种基于离策略、无模型强化学习的方法，并结合迁移学习和域随机化提升训练速度与泛化能力。该方法面向带腕部六轴力/力矩传感器的位置控制机器人，同时学习名义运动轨迹和分阶段的柔顺控制增益。作者在多种接触丰富的插入环境中进行了仿真和真实机器人评估。
- Important terms and preferred Chinese/English wording: variable compliance control / 可变柔顺控制; peg-in-hole assembly / 插杆入孔装配; parallel position-force control / 并行位置-力控制; force-torque (F/T) sensor / 六轴力/力矩传感器; selection matrix / 选择矩阵; domain randomization / 域随机化; residual reinforcement learning / 残差强化学习; target-pose uncertainty / 目标位姿不确定性; search phase / 搜索阶段; insertion phase / 插入阶段.
- Sentences or equations needing a second pass: The paper defines the pose orientation as a 4D unit quaternion but later reports 24 policy actions; 7 pose-subgoal values plus 18 controller parameters would suggest 25 values. The exact action parameterization and quaternion handling need source-code or supplementary verification.

## Technical digest

- Problem and claimed gap: The target pose of a peg-in-hole task is uncertain, while common industrial arms are position-controlled and therefore need active compliance to avoid large contact forces. The paper targets a policy that can adjust both motion and compliance online instead of manually tuning force gains for each task. It assumes the peg is firmly grasped, insertion is parallel to the gripper axis, and an estimated target pose or reference trajectory is available.
- Method and key equations: The architecture has a 500 Hz-equivalent inner parallel position-force loop and a 20 Hz SAC policy. With force error `F_e = F_g - F_ext`, the commanded Cartesian pose is described as `x_c = S(K_p^x x_e + K_d^x xdot_e) + a_x + (I-S)(K_p^f F_e + K_i^f integral(F_e dt))`. `S=diag(s_1,...,s_6)` distributes position and force control by direction. The policy controls position proportional gains, force proportional gains, and the six selection values; derivative gains are derived for critical damping and force integral gains are set empirically to 1% of the force proportional gains. A residual formulation adds the learned position correction to the nominal/reference and force responses.
- Sensors, observations, actions, and controller interface: Observations combine end-effector pose error to the predicted target, end-effector velocity, desired insertion force, previous action, and the last 12 low-pass-filtered six-axis F/T readings. Proprioception is encoded by two fully connected layers; the F/T history is encoded by a temporal convolutional network; features are concatenated before action prediction. The policy emits a Cartesian pose/subgoal component and bounded compliance-controller parameters. Gain values are mapped from `[-1,1]` into baseline-centered ranges `[P_base-P_range, P_base+P_range]`. The paper's text states 18 controllable controller parameters and Figure 7 labels 24 total policy actions, while the stated 4D quaternion pose makes the total dimension ambiguous.
- Simulation platform and task details: Training uses Gazebo 9 on a cuboid peg-in-hole task with randomized initial and goal poses. Randomized conditions include initial pose, goal-pose prediction error, surface stiffness, and desired insertion force. The reported stiffness range is `7.0e-4` to `1.0e-5` in the Gazebo ODE `kp` parameter (the ordering and physical interpretation need checking). The real platform is a Universal Robots UR3e with a wrist F/T sensor and Robotiq Hand-e gripper; the peg and board have 1.0 mm clearance in the principal test.
- Dataset or demonstrations: No fixed offline dataset is used. SAC learns from online environment interaction with a replay buffer and distributed prioritized experience replay. A reference trajectory or estimated target pose can provide prior information, but the main experiments do not require a demonstration dataset.
- Training procedure and compute: The policy is trained for 500,000 simulated steps, reported as about 5 hours on an Intel i9-9900K and RTX 2080 SUPER. After transfer, the policy is refined on the real robot for 15,000 steps (3% of the simulation budget), reported as about 20 minutes. The implementation is based on the TF2RL TensorFlow 2.0 repository; exact seeds, network widths beyond the 32-dimensional intermediate features, optimizer settings, replay sizes, and update ratios are not fully specified.
- Reproduction-critical constants and missing details: Inner/outer rates are 500/20 Hz; success is end-effector position error below 1 mm; force-limit violation `F_ext > F_max` ends an episode and receives a penalty; test episodes generally use 20 random initial positions. Critical missing or ambiguous items include exact force filter cutoff and sensor calibration, full gain ranges and `F_max`, action dimension/quaternion normalization, reward weights, SAC hyperparameters and seeds, Gazebo contact/friction parameters, and whether all reported trials were independent across randomization conditions.

## Experimental design analysis

- Baselines and whether comparisons are fair: The main comparison is learning from scratch on the real robot, direct sim-to-real, and sim-to-real followed by real-robot refinement. The same task and 20-trial protocol are used for the headline comparison, but the refinement condition receives additional real data, so it is not a zero-shot transfer comparison. The controller architecture and policy inputs are also ablated. There is no classical fixed-gain force controller reported as a complete quantitative baseline across all novel tasks.
- Metrics and statistical treatment: Primary reported outcomes are success rate, average time steps, average time, and learning curves. Table 2 reports 20 trials: scratch 100% / 109.6 steps / 5.48 s, direct sim-to-real 95% / 75.3 / 3.77 s, and sim-to-real plus refinement 100% / 65.6 / 3.28 s. Novel-task success ranges from 55% to 80%. No confidence intervals, standard deviations, hypothesis tests, force RMSE, peak-force distributions, penetration, contact-loss counts, or per-seed statistics are reported.
- Ablations and what they establish: TCN input processing reaches a successful policy at roughly 25,000 simulation steps versus roughly 40,000 for a two-layer fully connected policy in the shown run. Removing previous action hurts convergence substantially; removing desired insertion force also reduces learning performance. These ablations support temporal haptic history and action context, but they do not isolate the effect of the variable-compliance action space from the network architecture.
- Real-robot evidence and sim-to-real procedure: The UR3e experiments include a 3D-printed cuboid peg, variable goal-pose error, high/medium/low stiffness fixtures, and unseen tasks such as a ring, electrical outlet, LAN port, and USB. Domain randomization covers initial/goal pose, predicted-pose error, surface stiffness, and desired force. Real-robot refinement is needed because contact friction and dynamics are difficult to simulate; therefore the strongest result is a short sim-to-real-plus-adaptation pipeline rather than a pure transfer guarantee.
- Failure cases and missing controls: Performance degrades for complex LAN-port geometry and when a peg corner catches on a surface crevice; large force alone cannot recover such cases. Orientation error at 5 degrees is particularly difficult for scratch and direct-transfer policies. Missing controls include matched compute/data budgets for every baseline, repeated independent seeds, explicit force/penetration safety traces, sensor-noise and latency sweeps, and a no-learning parallel controller with the same gain range.
- Evidence locations (section/table/figure/equation): System and rates: Sections 2.1-2.2 and Figure 2; observation history and TCN: Section 2.2.2 and Equation (1), Figure 3; controller: Section 2.2.3, Equation (2), Figure 4; reward and force-limit termination: Section 2.3, Equations (3)-(4); residual and randomization: Sections 2.4.1-2.4.2, Equation (5); randomization ranges: Table 1; headline comparison: Table 2 and Figure 7; pose/stiffness/novel-task generalization: Tables 3-5 and Figures 8-9; ablations: Figures 10-12; limitations: Section 4.

## Assessment

- Strengths: The two-rate interface is directly relevant to a safe learned layer over a fast force loop. The paper exposes the control interface, uses a real wrist F/T sensor, randomizes several transfer variables, tests unseen insertion geometries, and includes explicit force-limit termination. The comparison between simulation pretraining and short real refinement gives a useful data-efficiency reference.
- Weaknesses and hidden assumptions: The core test assumes a known true goal pose, a firmly held peg, insertion aligned with the gripper axis, and a single robot/controller stack. The force-gain range remains manually selected, and the reward's force term does not establish closed-loop stability. Success rate can hide unsafe transients and slow or failed recovery. The paper uses Gazebo rather than MuJoCo, reports limited statistical treatment, and leaves several implementation details unavailable. The action-dimension inconsistency is a concrete reproduction risk.
- Reproducibility: what is available and what is missing: The paper gives the loop rates, robot family, sensor type, task assumptions, randomization categories/ranges, high-level SAC/TCN structure, trial counts, and major outcomes. It does not provide enough information to reproduce the exact policy: seeds, full network and optimizer configuration, reward weights, filter/calibration details, force limits, gain bounds, contact parameters, action encoding, and complete code/data provenance are missing from the PDF.
- Relevance to the project vision: This is a strong design reference for the project's MuJoCo-first two-rate residual proposal, but its evidence should be classified as open-access full-text design and transfer evidence, not as proof of a safe sim-to-real method. It motivates retaining force history, previous action, desired force, bounded gain mappings, and explicit failure metrics while replacing Gazebo with MuJoCo and adding held-out mismatch tests.
- Candidate extension or research gap: A controlled study of whether a slow policy should modify trajectory, compliance gains, or both under measured contact mismatch remains open. The project can add a safety-preserving residual envelope and identical simulation/real evaluation, then test whether gain adaptation improves held-out force error without increasing peak force, penetration, or contact-loss recovery failures.

## Follow-up experiment in MuJoCo

Implement a platform-neutral peg-in-hole/contact fixture with a 500 Hz PI or
parallel position-force loop and a 20 Hz outer policy. Compare (A) fixed-gain
PI, (B) bounded residual pose correction, (C) bounded gain/selection adaptation,
and (D) full pose-plus-gain policy. Randomize initial/goal pose, contact
stiffness/friction, force-sensor bias/noise/filter delay, actuator delay, and
desired force during training; hold out combinations and geometries for
evaluation. Log force RMSE and tail error, peak force, penetration, contact
loss/recovery time, command-limit violations, safety-gate activations, success,
and time-to-completion over seeds 101/202/303. Do not add real-robot commands
until the calibration and replay gates in the project vision pass.

## Actions

- [ ] Add metadata to the literature index/Zotero (Zotero account is not configured)
- [x] Save the PDF outside Git
- [ ] Reproduce the smallest reported result
- [ ] Create or update a project config
- [x] Link this note from the two-rate residual proposal and related-work taxonomy
