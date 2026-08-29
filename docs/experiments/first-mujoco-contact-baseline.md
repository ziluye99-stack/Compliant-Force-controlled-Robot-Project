# First MuJoCo Contact-Force Baseline

## Question

Can a bounded PI controller track a constant normal contact force in a
deterministic MuJoCo fixture while respecting the platform-neutral penetration
and total-force safety limits?

## Reproduction

- Config: `configs/contact_force.yaml`
- Runner: `src/contact_force_experiment.py`
- Seed: 42
- Smoke command:

```bash
.mamba-env/bin/python -m src.contact_force_experiment \
  --config configs/contact_force.yaml --run-id first-baseline-smoke --steps 200 --seed 42
```

The run directory records the resolved config, Git commit, package snapshot,
seed, Slurm job ID (or null for local execution), and metrics. Generated files
stay under ignored `artifacts/contact-force-baseline/`.

## Recorded smoke runs

The following runs were generated from commit `4d2487e1ebd6595c963eb87dd80b275fad5f3647`:

| Run | Tail mean force | True-force RMSE | Measured-force RMSE | Max penetration | Contact |
| --- | ---: | ---: | ---: | ---: | --- |
| `first-baseline-20260830` | 4.999973 N | 0.000033 N | 0.000033 N | 0.612 mm | yes |
| `first-robust-20260830` | 5.025145 N | 0.082893 N | 0.215802 N | 0.482 mm | yes |

Artifacts:

- `artifacts/contact-force-baseline/first-baseline-20260830/`
- `artifacts/contact-force-baseline/first-robust-20260830/`

The robust result is a diagnostic comparison, not a claim of transfer: noise
and command-path mismatch visibly degrade tracking while the geometric safety
proxy remains below the 1 mm contract limit.

## Baseline and comparison

The baseline is the transparent PI plus velocity-damping controller in
`src/contact_force_baseline.py`. The first comparison is
`configs/contact_force_robust.yaml`, which adds controlled force noise,
damping/gain mismatch, friction, and command delay. This establishes a
reproducible controller sanity check before a learning residual is evaluated.

## Metrics and safety

Report tail force RMSE, measured-force RMSE, force variation, maximum control,
maximum penetration, and whether contact was observed. The platform-neutral
contract caps penetration at 1 mm and total contact force at 40 N; this task
remains simulation-only and never enables hardware commands.

## Interpretation boundary

Passing this fixture does not establish sim-to-real transfer or suitability for
a particular arm. Those claims require a selected robot, calibrated force/
torque sensor, identified dynamics, offline replay, watchdog, emergency stop,
operator, and supervised low-gain hardware evidence.
