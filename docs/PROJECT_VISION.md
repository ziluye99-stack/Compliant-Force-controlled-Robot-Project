# Project Vision and Research Charter

This document is the project north star. Read it before creating a branch,
starting a new experiment, changing the simulator, or asking Codex to implement
a substantial task. A branch task is successful only when it moves this charter
forward and leaves evidence that can be reproduced.

## North-star goal

Build safe, measurable, and transferable compliant-force-control capabilities
for embodied robots. The project should connect mechanics, sensing, control,
learning, and deployment into one evidence-driven loop:

```text
research question -> experiment design -> MuJoCo simulation -> data/training
-> offline evaluation -> supervised real-robot validation -> paper-quality evidence
```

The long-term target is not a single robot or model. It is a reusable method
that explains when contact-aware policies work, why they fail, and how to move
from simulation to a real arm or humanoid platform without hiding safety limits.

## Research priorities

1. **Compliant interaction:** force/torque-aware control, contact stability,
   disturbance rejection, and graceful behavior under model mismatch.
2. **Embodied learning:** policies that use physically meaningful observations,
   demonstrations or interaction data, and explicit action/constraint spaces.
3. **Simulation-to-real transfer:** MuJoCo-first task definitions, randomized
   but measured dynamics, calibration, replay, and bounded real-world adaptation.
4. **Evidence and reproducibility:** fair baselines, ablations, multiple seeds,
   logged failure cases, versioned configs, and archived artifacts.
5. **Transfer to larger embodiments:** retain interfaces that can later support
   humanoid whole-body contact tasks without prematurely coupling to one vendor.

## Working principles

- Start from a falsifiable question and a measurable success criterion.
- Keep the smallest test that can disprove the current hypothesis.
- Treat MuJoCo as the primary simulation platform until an explicit decision
  changes it; document any Isaac/Gazebo migration separately.
- Separate mechanics, sensor calibration, controller safety, and policy learning
  so failures can be localized.
- Never enable a real robot command without a written limit, watchdog, emergency
  stop, operator, and rollback procedure.
- Prefer a simple baseline that is fully understood over an opaque model with
  incomplete comparisons.

## Stage gates

An experiment advances only after the previous gate has evidence:

| Gate | Required evidence |
| --- | --- |
| Question | Hypothesis, variables, baseline, metrics, and safety constraints |
| Simulation | MuJoCo scene, observation/action contract, fixed seeds, smoke tests |
| Training | Locked environment, config, resource allocation, checkpoints, metrics |
| Evaluation | Baselines, ablations, multiple seeds, failure analysis |
| Hardware | Calibration, replay, low-gain test, limits, watchdog, operator sign-off |
| Publication | Archived artifacts, scripts, figures, equations, and honest limitations |

## Branch rule

Before starting a branch, read this file and write a short task statement that
names the relevant priority, stage gate, expected artifact, and verification
command. Keep one branch focused on one experiment or infrastructure change.
Do not mix robot-driver work with model claims or paper edits in the same branch.

## Current scope

The current implementation phase is a platform-neutral MuJoCo scaffold with
server-side reproducibility and local archival. Robot model, force sensor,
controller, ROS 2 distribution, and real-hardware protocol remain explicit
inputs for later branches.
