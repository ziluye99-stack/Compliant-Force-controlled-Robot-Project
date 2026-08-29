# Research Proposal Workflow

A proposal is the reviewable bridge between literature evidence and an
individual experiment. It prevents a promising paper or idea from turning into
untracked implementation work.

## Required contents

Every proposal should contain:

1. A single falsifiable research question and a bounded hypothesis.
2. The evidence that motivates the question, with full-text provenance kept
   separate from discovery metadata.
3. A baseline, independent variables, controls, metrics, seeds, and an explicit
   safety boundary.
4. A system/interface decision record stating what is platform-neutral and what
   must wait for a robot or sensor selection.
5. A decomposition into focused branches, each with dependencies, an artifact,
   and the smallest verification command.
6. Go/no-go rules for moving from literature to simulation, training, transfer,
   and supervised hardware.

Start from [`template.md`](template.md). The project-level decomposition is
[`project-master-plan.md`](project-master-plan.md); the current platform-neutral
experiment example is [`two-rate-residual-contact.md`](two-rate-residual-contact.md).

## Review order

Review proposals in this order:

```text
vision -> verified literature -> question/gap -> system contract
-> smallest MuJoCo test -> data/training -> held-out evaluation
-> calibration/replay -> supervised hardware -> paper/release
```

A proposal may define future hardware work, but it must not enable hardware
commands before the robot, sensor, limits, watchdog, emergency stop, operator,
and rollback procedure are documented.

## Status vocabulary

- `draft`: structure and hypothesis exist, but required evidence or platform
  inputs are missing.
- `simulation-ready`: the platform-neutral or selected-system interface and
  smallest falsifying MuJoCo test pass.
- `transfer-ready`: measured parameters, uncertainty, offline replay, and
  identical evaluation code have passed.
- `hardware-ready`: the supervised safety checklist has an operator sign-off.

Do not promote a proposal based on a metadata-only paper or a task-local
simulation result.
