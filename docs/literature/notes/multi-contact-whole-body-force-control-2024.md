# Paper Note: Multi-Contact Whole-Body Force Control for Position-Controlled Robots

## Bibliographic record

- Title: Multi-Contact Whole-Body Force Control for Position-Controlled Robots
- Authors: Quentin Rouxel, Serena Ivaldi, Jean-Baptiste Mouret
- Venue and year: IEEE Robotics and Automation Letters, 2024, 9(6), 5639--5646
- DOI: [10.1109/LRA.2024.3396094](https://doi.org/10.1109/LRA.2024.3396094)
- Publisher URL: [IEEE Xplore DOI landing page](https://doi.org/10.1109/LRA.2024.3396094)
- Preprint or code URL: [HAL record and PDF](https://hal.science/hal-04362547v5); [SEIKO project page](https://hucebot.github.io/seiko_controller_website/)
- Discovery source and access date: Crossref/OpenAlex metadata; HAL open-access PDF; 2026-08-29
- Full-text access route: CC-BY HAL repository PDF and supplementary material
- Full-text file and SHA-256: `/mnt/research-data/literature/pdfs/multi-contact-whole-body-force-control-2024.pdf`; `4ce71c106a580cc80f68f69670189466bb09f6085585a6b9f479ba5f4ee9735e`
- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): accepted-manuscript

## Translation and terminology

### Abstract translation

许多人形和多足机器人采用位置控制而不是力矩控制，这使得直接控制接触力变得困难，也限制了通过将手放在墙面或扶手上建立多重接触来增强平衡的能力。本文提出 SEIKO（Sequential Equilibrium Inverse Kinematic Optimization）流程，利用显式柔性模型，在传统位置控制机器人上间接控制接触力。SEIKO 从笛卡尔指令生成全身重定向，并通过两个实时求解的二次规划统一处理导纳控制。作者在全尺寸 Talos 人形机器人上验证了推墙、远距离伸手、爬楼梯和斜面踩踏等多接触任务。

### Preferred terminology

| English | Chinese used in this project |
| --- | --- |
| multi-contact whole-body force control | 多接触全身力控制 |
| position-controlled robot | 位置控制机器人 |
| joint flexibility | 关节柔性 |
| contact wrench | 接触力/力矩（接触扳手） |
| sequential equilibrium inverse kinematic optimization (SEIKO) | 顺序平衡逆运动学优化 |
| retargeting | 全身重定向 |
| contact switching | 接触切换 |
| quasi-static assumption | 准静态假设 |

## Technical digest

### Problem and claimed gap

Torque-controlled whole-body inverse dynamics can regulate contact wrenches but
is sensitive to robot-model and calibration errors. Position-controlled robots
are easier to deploy but have no direct force command. The paper's gap is a
whole-body, constraint-aware way to exploit unavoidable joint/structural
flexibility so that position commands indirectly regulate redundant contact
wrenches. Unlike independent end-effector admittance, the method accounts for
posture changes, equilibrium, torque limits, friction, and contact transitions.

### Method and key equations

Under a quasi-static model, whole-body equilibrium is

```text
g(q) = S tau + J(q)^T lambda.
```

Each joint is modeled as a spring, with flexible torque

```text
tau_flex = K (theta_cmd - theta_flex).
```

The derivative of the equilibrium and flexibility equations gives a linear
relationship between command changes and flexible posture/contact-wrench
changes. SEIKO solves two QPs at each step:

1. **Retargeting QP:** chooses a feasible desired posture, contact wrenches,
   and torques from operator Cartesian commands. It enforces equilibrium,
   fixed enabled contacts, joint limits, torque limits, contact-wrench cones,
   and bounded rates of posture/wrench changes.
2. **Controller QP:** computes flexible posture and wrench changes so that
   measured wrenches follow the desired change while keeping disabled-effector
   poses, joint commands, and dynamically adapted torque limits feasible.

The measured-wrench feedback law is

```text
Delta lambda_effort = Delta lambda_d
    + Kp (lambda_d - lambda_read_tilde) - Kd lambda_dot_read.
```

A complementary filter combines predicted flexible-wrench change with the
measured wrench; the measured wrench velocity is low-pass filtered at 10 Hz.
The controller runs at 500 Hz and interpolates joint positions at 2 kHz.

### Sensors, observations, actions, and interface

- Robot: PAL Robotics Talos, 1.75 m, 32 DoF nominally; 25 joints used in the
  reported implementation after removing head and forearm joints.
- Actuation: all joints in stiff position-controlled mode; no direct torque
  command is assumed.
- Sensors: foot force/torque sensors, joint torque estimates, and a pelvis IMU
  gyroscope for oscillation measurements.
- Inputs: operator 6-DoF Cartesian pose/velocity commands, explicit contact
  state switches, and optional normal-force pushing targets.
- Outputs: feasible whole-body position commands and desired contact wrenches.
- Software: C++, RBDL/Pinocchio analytical derivatives, QuadProg QP solver.

### Safety and contact constraints

The formulation constrains unilateral normal force, friction-pyramid tangential
force, center-of-pressure bounds, torsional limits, joint positions, joint
torques, and rates of change. A contact switch ramps wrench and posture changes
through explicit rate bounds. Torque-limit adaptation uses hysteresis to avoid
integrator wind-up. These are optimization constraints and monitoring rules,
not a substitute for an independent emergency stop or hardware watchdog.

## Experimental design analysis

### Real-robot experiments

The authors evaluate Talos in a wall-pushing task, contact switching, whole-body
damping, and far-reaching with an unmodeled 9 kg hand load. Five controlled and
five uncontrolled pushing trials compare desired and measured hand/foot forces.
Contact switching starts with both feet and the right hand in contact, removes
the right foot, and re-establishes it. Short torso pushes (10--12 per trial)
compare damping gains `Kd = 0, 0.01, 0.05`; the deployed setting is `Kd = 0.02`.
The full controller keeps the robot stable with added mass, but high speed and
large loads still violate the quasi-static assumptions.

The paper reports median computation times of 0.50 ms for retargeting and
0.40 ms for the controller (maxima 0.56 and 0.43 ms). The measured Talos mass
was 99.7 kg versus 93.4 kg in the URDF, providing a useful model-error test.

### MuJoCo robustness study

The Talos model performs ten double-support reach-and-return sequences for
hand speeds of 2, 10, 20, 30, and 40 cm/s and added hand masses of 0, 2, 5,
10, and 12 kg. Three conditions are compared: open-loop retargeting, SEIKO
force control without torque-limit constraints, and the full controller. The
full controller gives the highest success counts near the feasibility boundary,
but success falls for fast motions and heavy loads. The authors explicitly
note that MuJoCo's soft contacts produce more flexibility than Gazebo and the
real Talos, so simulator results are robustness evidence rather than calibrated
sim-to-real evidence.

### Baseline fairness and statistical treatment

The comparisons use matched task grids and repeated trials, and the paper shows
success counts, force traces, oscillation deciles, and computation times. It
does not provide confidence intervals for all success ratios, a common random
seed protocol for simulation, or a broad quantitative force-tracking table.
The baseline effector-admittance comparison is in supplementary material and
omits two feedback effects from the referenced method. These choices make the
mechanistic comparison useful but limit claims about general superiority.

## Assessment

### Strengths

- Directly addresses the deployment reality of position-controlled humanoids.
- Unifies force distribution, posture adaptation, contact switching, and
  feasibility constraints in one optimization interface.
- Uses both hardware experiments and a clearly described MuJoCo robustness grid.
- Exposes computation time, model-mass mismatch, contact stability conditions,
  and failure cases instead of reporting only successful demonstrations.

### Weaknesses and hidden assumptions

- The quasi-static assumption limits dynamic locomotion and fast contact.
- Contact states and sequencing are supplied externally; the method does not
  solve contact planning or perception.
- The flexibility model uses position-control gains imported from Gazebo and is
  not identified on the real Talos. The authors acknowledge this mismatch.
- Results are mostly teleoperated and task-specific; no learning component is
  evaluated, and no held-out randomized parameter benchmark is reported.
- Force sensors, torque estimates, and operator procedures are described only
  at the level needed for the paper, not as a complete replication package.
- Constraint feasibility is not an independent safety certificate; hardware
  watchdog, E-stop, and operator exclusion procedures remain necessary.

### Relevance to the project vision

This paper supports retaining a platform-neutral contact-wrench interface and
explicit safety constraints while moving from a two-link arm to humanoid whole-
body tasks. Its main transferable idea is to model the position-to-force
relationship through flexibility and solve constrained corrections, while its
unmodeled flexibility and MuJoCo/Gazebo discrepancy motivate calibrated,
held-out transfer tests in this project.

## Follow-up experiment in MuJoCo

1. Add a planar two-link contact scene with two simultaneous contacts and a
   low-dimensional joint-flexibility model (`tau = K(theta_cmd-theta_flex)`).
2. Compare independent end-effector admittance, a constrained whole-body QP,
   and the current fast PI plus bounded residual interface under identical
   contact states and targets.
3. Sweep friction, stiffness, joint damping, contact switching time, and model
   mass error; hold out at least one combined regime for evaluation.
4. Log wrench RMSE, contact-wrench-cone violations, torque-limit ratio,
   contact-switch settling time, penetration, contact loss, and solver time.
5. Treat a solver infeasibility or safety-gate activation as a first-class
   failure. Do not claim humanoid transfer until a selected platform's sensors,
   joint limits, calibration, watchdog, and replay procedure are documented.

## Actions

- [x] Add bibliographic metadata, open-access provenance, and PDF SHA-256
- [x] Translate the abstract and lock project terminology
- [x] Extract the flexibility model, QP interfaces, constraints, and rates
- [x] Analyze real-robot and MuJoCo experiment design and limitations
- [x] Define a MuJoCo follow-up experiment
- [ ] Reproduce the Talos benchmark (requires the authors' assets/code and a compatible model)
- [ ] Add metadata to Zotero after the user's library workflow is authorized
