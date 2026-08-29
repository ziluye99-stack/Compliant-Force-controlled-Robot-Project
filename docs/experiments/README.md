# Experiment Records

Create one Markdown record per experiment family. Read
`docs/PROJECT_VISION.md` first, then state the question, hypothesis, independent
variables, controlled variables, safety constraints, success metrics, baseline,
ablations, and artifact run IDs. Link to committed configuration files and
literature notes instead of duplicating parameters.

An experiment record should identify the smallest MuJoCo test that could falsify
the hypothesis. Promote it to hardware only after the safety gate in
`docs/workflow.md` is complete.

## Current Experiment Directory

| Record | Stage/status | Config or command | Evidence boundary |
| --- | --- | --- | --- |
| [`normal-force-baseline.md`](normal-force-baseline.md) | MuJoCo simulation complete | `configs/contact_force.yaml` | Idealized one-dimensional contact; no hardware claim |
| [`tangential-contact.md`](tangential-contact.md) | MuJoCo simulation complete | `configs/tangential_contact.yaml` | Sticking/sliding fixture; no calibrated arm claim |
| [`planar-arm-contact.md`](planar-arm-contact.md) | MuJoCo simulation complete | `configs/planar_arm_contact.yaml` | Platform-neutral two-link arm; no selected robot claim |
| [`dual-contact-force-control.md`](dual-contact-force-control.md) | MuJoCo simulation complete | `configs/dual_contact.yaml` | Simultaneous floor/wall interface test; not humanoid evidence |
| [`two-rate-residual-study.md`](two-rate-residual-study.md) | `simulation-ready` | `configs/two_rate_residual.yaml` | Local CPU matrix; server GPU use remains resource-policy gated |
| [`controller-ablation.md`](controller-ablation.md) | Evaluation complete | `configs/controller_ablation.yaml` | Task-local observation/gain ablation; no sim-to-real claim |
| [`contact-parameter-identification.md`](contact-parameter-identification.md) | Transfer analysis, synthetic only | `src.mujoco_contact_trace` | Real logs and hardware calibration still missing |
| [`contact-loss-recovery.md`](contact-loss-recovery.md) | MuJoCo robustness experiment | `configs/contact_loss_recovery.yaml` | Synthetic disturbance; no sim-to-real or hardware claim |

The directory is an index, not a replacement for the individual records. A
paper or proposal may motivate a row, but its result is promoted only when the
record links the exact config, seed, artifact path, and verification output.
Generated data, checkpoints, videos, and raw logs stay outside Git.
