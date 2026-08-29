# Related-work taxonomy: compliant force control for embodied robots

This is a positioning document, not a claim that the listed areas have been
surveyed exhaustively. Every row must be backed by a paper note before it is
used in a paper or a design decision. The first completed note is linked in the
last column; the other rows are the next reading queue.

## Comparison dimensions

The project compares methods along six dimensions: (1) control interface,
(2) contact observations, (3) what is learned or adapted, (4) task and
embodiment, (5) simulator-to-hardware evidence, and (6) safety and evaluation
coverage. A method that reports only task success is not considered sufficient
evidence for force-control transfer.

| Family | Control interface | Typical observations | Learned/adapted quantity | Typical evidence | Open issue for this project |
| --- | --- | --- | --- | --- | --- |
| Classical force/position control | Task-space or joint-space force/position loop | Force/torque, pose, velocity | Fixed gains, selection matrix, impedance | Analytical stability and controlled contact tests | Robust tuning under friction, delay, and sensor mismatch |
| Admittance/impedance adaptation | Position or torque interface with compliant dynamics | Force/torque, motion error, sometimes tactile | Stiffness, damping, inertia, scheduling | Contact tasks and assembly benchmarks | Separating trajectory adaptation from compliance adaptation |
| RL with a force-control action space | Usually position-controlled arm plus an inner controller | Pose error, velocity, filtered force | Trajectory and/or controller gains | Simulation plus selected real tasks | Fair baselines, safety gates, hyperparameter sensitivity |
| Residual policy over a known controller | Existing PI/admittance outer or inner loop | Controller error, force, velocity, integral state | Bounded correction | Offline or simulated robustness studies | Held-out contact scenes and calibrated mismatch |
| Contact-rich manipulation learning | Position, velocity, or torque depending on robot | Vision, force, tactile, proprioception | Motion, contact mode, skill parameters | Peg-in-hole, insertion, pushing, grasping | Force metrics and failure reporting are often incomplete |
| Sim-to-real transfer | Any of the above | Randomized or calibrated observations | Dynamics randomization, adaptation, replay | Real robot after simulation training | Measured parameter identification and identical metrics |
| Humanoid whole-body/multi-contact control | Whole-body torque, momentum, or distributed task control | Tactile, contact state, IMU, joint state | Contact schedule, task priorities, compliance | Multi-contact locomotion/manipulation | Preserve a reusable end-effector contract without vendor coupling |
| Chinese robotics literature (queue) | To be classified per paper | To be classified per paper | To be classified per paper | CNKI/万方 and university portal records | Translate terminology and compare reporting standards fairly |

## Evidence currently available

The completed RA-L paper, *Learning Force Control for Contact-rich Manipulation
Tasks with Rigid Position-controlled Robots*, belongs primarily to the RL with a
force-control action space family. It combines SAC with a conventional parallel
position/force or admittance controller, runs a slow policy over a fast force
controller, and adds IK, joint-velocity, and force-limit checks. Its result
supports studying a bounded learning layer around a transparent controller. The
paper also exposes unresolved issues: hand-tuned gain ranges, known goal pose,
incomplete hardware details, reactive force-limit handling, and no held-out
friction or delay evaluation. See
[`learning-force-control-2003.00628.md`](notes/learning-force-control-2003.00628.md).

The current project already supplies simulation evidence for the residual-policy,
friction-contact, planar-arm, and controller-ablation rows. Those results remain
task-local MuJoCo evidence. They must not be summarized as real-robot or
sim-to-real evidence until calibration and replay gates are complete.

## Reading and classification queue

The next papers are selected to cover complementary axes rather than to collect
citations randomly:

1. *A survey of robot manipulation in contact* for contact modes, sensing, and
   evaluation taxonomy.
2. *Force Sensorless Admittance Control With Neural Learning for Robots With
   Actuator Saturation* for adaptive control under actuator limits.
3. *A Unified Parametric Representation for Robotic Compliant Skills With
   Adaptation of Impedance and Force* for reusable skill interfaces.
4. *Crossing the Reality Gap* for a transfer-variable and evaluation checklist.
5. *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on
   Distributed Tactile Sensors* for the humanoid/multi-contact axis.
6. At least three Chinese-language CNKI/万方 papers on mechanical-arm force
   control and humanoid compliance, selected through the university portal and
   recorded with database identifiers.

Each paper enters this table only after a note records its full-text source,
translation, method interface, baselines, metrics, limitations, and a proposed
MuJoCo test. Metadata-only candidates remain in the dated search log.

## Candidate gap and falsifiable question

Across the completed note and the current MuJoCo scaffold, a concrete gap is a
controlled comparison of what a slow learned residual should modify while a fast
force loop preserves safety. The proposed question is:

> Can a bounded residual running at a lower policy rate reduce force error on
> held-out contact dynamics without increasing penetration, peak force, or
> safety-gate activations relative to the same PI controller alone?

This question is narrow enough to falsify and does not claim that a MuJoCo result
transfers to a robot. Its design is recorded in
[`two-rate-residual-study.md`](../experiments/two-rate-residual-study.md).
