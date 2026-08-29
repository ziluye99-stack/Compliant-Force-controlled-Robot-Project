# Learning Force Control for Contact-rich Manipulation Tasks with Rigid Position-controlled Robots

## Bibliographic record

- Title: Learning Force Control for Contact-rich Manipulation Tasks with Rigid Position-controlled Robots
- Authors: Cristian C. Beltran-Hernandez, Damien Petit, Ixchel G. Ramirez-Alpizar, Takayuki Nishi, Shinichi Kikuchi, Takamitsu Matsubara, Kensuke Harada
- Venue and year: IEEE Robotics and Automation Letters, 2020
- DOI: [10.1109/LRA.2020.3010739](https://doi.org/10.1109/LRA.2020.3010739)
- Publisher URL: [IEEE Xplore](https://ieeexplore.ieee.org/document/9144504)
- Preprint or code URL: [arXiv:2003.00628](https://arxiv.org/abs/2003.00628)
- Discovery source and access date: OpenAlex metadata; public arXiv PDF; 2026-08-29
- Full-text file and SHA-256: `/mnt/research-data/literature/pdfs/learning-force-control-2003.00628.pdf`; `06ead9f87a59b17359e6877c9fe86ece7f1393bc615da61ee59daa4cb67ca48d`
- Evidence status: Full text read from the arXiv version. Publisher metadata and venue were cross-checked; no school-portal copy was needed.

## Translation and terminology

### Abstract translation

强化学习已经在多种操作任务中取得成功，但在真实机器人上仍不普遍，尤其是刚性位置控制机械臂，因为需要避免损坏机器人和环境的鲁棒控制，并且通常需要人工持续监督。本文提出一种将强化学习与传统力控结合的框架，并在位置控制机器人上实现两类力控：改进的并行位置/力控制和导纳控制。作者比较了两种控制方案作为强化学习动作空间时的表现，并提出故障安全机制，使刚性机械臂能够较少人工监督地进行学习。方法在 Gazebo 仿真和 UR3 e-series 真实机械臂上验证。

### Preferred terminology

| English | Chinese used in this project |
| --- | --- |
| rigid position-controlled robot | 刚性位置控制机器人 |
| parallel position/force control | 并行位置/力控制 |
| admittance control | 导纳控制 |
| force/torque sensor | 力/力矩传感器 |
| contact-rich manipulation | 接触丰富操作 |
| fail-safe mechanism | 故障安全机制 |
| selection matrix | 选择矩阵 |

## Technical digest

### Problem and claimed gap

Most industrial manipulators expose position commands rather than joint torque
commands. Directly learning low-level actions can therefore create large contact
forces. The paper learns both a task-space motion trajectory and time-varying
force-controller parameters while retaining a conventional force-control layer.
The claimed gap is safe low-level learning for contact-rich tasks on a rigid,
position-controlled arm.

### Method and key equations

The policy observes end-effector pose error, end-effector velocity, and filtered
external force. It outputs `a = [a_x, a_p]`, where `a_x` is a six-dimensional
position/orientation trajectory command and `a_p` adjusts force-controller
parameters. A nominal P-controller supplies a goal-directed trajectory; the
learned trajectory and force controller modify it before inverse kinematics
produces joint position commands.

For parallel position/force control, the task-space command is:

```text
u = S(Kpx xe + Kdx xdot_e) + ax
    + (I - S)(Kpf Fext + Kif integral(Fext dt))
```

`S = diag(s_1, ..., s_6)` allocates each direction between position and force
control. Only `Kpx` and `Kpf` are learned directly; `Kdx` is computed for a
critically damped relation and `Kif` is set to 1% of `Kpf` in the experiments.
The agent action is mapped from `[-1, 1]` into a hand-tuned range around a base
parameter value. The reduced parallel action `P-14` controls six pose values,
one proportional position gain, one proportional force gain, and six selection
values.

The task-space admittance model is:

```text
Fext = md xddot + bd xdot + kd x
X(s) / F(s) = (1 / md) / (s^2 + 2 zeta wn s + wn^2)
```

In the reduced `A-13pd` variant, the policy controls six position PD gains and
six stiffness values; inertia is fixed, damping is derived from a damping ratio,
and the remaining gains are computed. The RL algorithm is Soft Actor-Critic
(SAC), implemented with TF2RL. The policy runs at 20 Hz while the force
controller runs at up to 500 Hz.

### Safety mechanism

Before sending each position command, the system checks that an IK solution
exists and that the implied joint velocity is below a limit. A force limit is
checked reactively; exceeding it terminates the episode. Invalid commands are
not executed and the robot holds its current state. The reward includes a
positive completion term and a negative safety-violation term. This is a safety
layer around the learned policy, not a proof of collision-free behavior.

### Sensors, observations, actions, and interface

- Robot: Universal Robots UR3 e-series, position-controlled.
- End effector: Robotiq Hand-e gripper and an end-effector F/T sensor.
- Observation: pose error `xe`, end-effector velocity `xdot`, filtered external force `Fext`.
- Action: task-space pose trajectory `a_x` plus bounded controller parameters `a_p`.
- Low-level path: task-space controller -> IK -> desired joint configuration -> robot position command.
- Simulator: Gazebo 9. Real-robot control frequency is reported as up to 500 Hz; policy frequency is 20 Hz.

### Reward

The common reward combines normalized pose error, action magnitude, contact
force magnitude, a time penalty, and a terminal term. Completion receives `+200`,
and safety violation receives `-10`. The paper does not provide enough
information in the text extraction to reconstruct every reward weight `w_i`, so
the reward is not directly reproducible from this note alone.

## Experimental design analysis

### Simulation

The action-space study uses a cube insertion task with a 1 mm hole clearance and
identical initial conditions across models. Eight variants are compared: four
parallel controllers (`P-9`, `P-14`, `P-19`, `P-24`) and four admittance
controllers (`A-8`, `A-13`, `A-13pd`, `A-18`). Each model trains for 50,000
steps with at most 150 steps per episode; each session is repeated three times.
The reported qualitative result is that `P-14` and `A-13pd` provide the best
trade-off between action-space complexity and learning speed. Penalizing safety
violations accelerates learning and reduces collisions. The collision table
reports, for example, 121 versus 206 average collisions for `P-14` with versus
without the penalty, and 300 versus 462 for `A-13pd`.

### Real-robot validation

The authors train the best simulation candidates on two assembly tasks: a
metallic ring into a bolt with 0.2 mm clearance, and a metallic peg into a pulley
with 0.05 mm clearance. Each real task uses 20,000 steps, two training sessions,
and episodes of at most 200 steps. The paper reports successful learning and
fewer collisions for `A-13pd` than `P-14` on the peg task (4 versus 26 average
collisions per session), but the figures and text do not provide a complete
table of force tracking error, success confidence intervals, or all hardware
limits.

### Baseline fairness

The same insertion initial conditions are used for the simulated action-space
comparison, and the reward function is held constant across variants. However,
the controller families have different parameterizations and hand-tuned base
and range values. The paper compares learning curves and collision counts but
does not report a common statistical test, confidence interval, or equal
hyperparameter-search budget. The real-robot comparison transfers only the best
simulation candidates, so it is not a full cross-method hardware benchmark.

### What the ablation establishes

The action-space comparison supports a practical claim: reducing the number of
learned controller parameters can improve sample efficiency without removing
all useful compliance adaptation. The safety-reward comparison supports adding
an explicit penalty and command gate during exploration. It does not isolate
whether the improvement comes from the reward, early termination, command hold,
or another implementation detail.

## Assessment

### Strengths

- Addresses a real deployment constraint: many industrial arms expose position,
  not torque, control.
- Preserves a conventional force-control layer and bounds the learned action.
- Uses both simulation and real assembly tasks on the same robot family.
- Exposes the trade-off between controller action-space dimension and learning
  performance.
- Treats IK failure, velocity limits, and force limits as runtime events.

### Weaknesses and hidden assumptions

- Requires a known goal end-effector pose; perception-to-contact is not solved.
- Controller base/range hyperparameters are empirically selected and are
  reported as a major sensitivity. This weakens transfer claims.
- The real hardware details needed for replication (sensor model/calibration,
  exact UR controller mode, limits, filtering constants, and timing behavior)
  are incomplete.
- Force-limit handling is reactive after a violation, while the learned action
  can still be explored near the limit.
- Results are task- and robot-specific; no held-out object, surface stiffness,
  friction, delay, or calibration mismatch study is reported.
- The learned policy controls pose and controller parameters jointly, making it
  difficult to attribute gains to force adaptation versus trajectory search.
- Collision count is a useful safety signal but is not a substitute for force
  error, penetration, peak impulse, or damage-risk measurements.

### Reproducibility assessment

The paper specifies the main controller equations, frequencies, action variants,
episode lengths, task clearances, and broad hardware setup. It does not provide
all reward weights, random seeds, full simulator assets, filtering and contact
parameters, exact safety thresholds, or a public implementation in the paper
record reviewed here. Reproducing the exact numbers therefore requires the
authors' code or additional portal supplementary material.

### Relevance to the project vision

This paper strongly supports keeping a transparent force-control baseline and a
bounded learning residual. Its two-rate architecture (slow policy, fast safety
controller), explicit command validation, and separation of task trajectory from
contact regulation are useful interfaces for our MuJoCo-first scaffold. Its
Gazebo and UR3-specific implementation is evidence for design choices, not a
reason to change our current simulator or claim sim-to-real transfer.

## Follow-up experiment in MuJoCo

Implement a platform-neutral two-rate comparison using the existing planar-arm
contact scene:

1. Keep the Jacobian-transpose PI force controller as the fast 500 Hz-equivalent
   baseline and run a bounded residual policy at a slower rate.
2. Compare PI-only, trajectory residual only, gain residual only, and the joint
   residual under the same initial states, force targets, and three seeds.
3. Evaluate nominal and held-out friction, contact stiffness, sensor bias/noise,
   and command delay. Log force RMSE, peak force, penetration, contact loss,
   torque limit violations, and recovery time, not only success.
4. Add proactive action and velocity gates before stepping the simulator, and
   report gate activations separately from failures.

This is a falsifiable extension of the paper: the residual should reduce force
error on held-out dynamics without increasing penetration, peak force, or gate
activations relative to PI. It must not be presented as hardware evidence until
the robot and sensor calibration gates in `docs/roadmap.md` are complete.

## Actions

- [x] Add bibliographic metadata and source provenance
- [x] Save the public PDF outside Git and record its SHA-256
- [x] Extract observations, actions, controller interface, safety gate, and experiments
- [ ] Reproduce the smallest reported insertion result (requires Gazebo/assets or author code)
- [x] Create a MuJoCo follow-up experiment specification
- [x] Link this note from a related-work taxonomy and a new experiment record
