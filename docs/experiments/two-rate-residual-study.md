# Two-rate residual force-control study

## Task statement

- Branch: `codex/two-rate-residual-runner`
- Project priorities: compliant interaction, embodied learning, and evidence/reproducibility
- Stage gate: Simulation implementation and contract validation
- Related literature: [`learning-force-control-2003.00628.md`](../literature/notes/learning-force-control-2003.00628.md), [`residual-learning-dmp-2008.07682.md`](../literature/notes/residual-learning-dmp-2008.07682.md), and [`related-work-taxonomy.md`](../literature/related-work-taxonomy.md)
- Expected artifact: a reproducible MuJoCo experiment comparing a fast PI loop with bounded lower-rate residual policies
- Current status: runner, contract tests, and the complete local CPU matrix are
  implemented and reviewed; server-side GPU execution remains scheduler-gated

## Question and hypothesis

Question: Does a residual policy running at 20 Hz over a 500 Hz-equivalent PI
force loop improve held-out contact-force tracking while preserving safety?

Hypothesis: A residual that modifies the controller command or controller gains
at the slow rate will reduce true-force RMSE on held-out friction, stiffness,
sensor-noise, and actuator-delay settings. It must not increase maximum
penetration, peak force, torque/action-limit violations, or contact-loss rate
relative to PI-only.

## Experimental matrix

| Factor | Values | Rationale |
| --- | --- | --- |
| Controller | PI-only; trajectory residual; gain residual; joint residual | Attribute improvement to the learned interface |
| Fast control rate | 500 Hz equivalent (`dt=0.002 s`) | Preserve contact safety loop |
| Residual rate | 20 Hz equivalent (apply for 25 fast steps) | Test the two-rate design from the literature |
| Training dynamics | Nominal; randomized friction/stiffness/noise/delay | Separate interpolation from robustness |
| Held-out dynamics | At least two unseen combinations | Test transfer beyond training distribution |
| Target force | Train range 3--7 N; held-out 4 and 6 N | Prevent a single-target claim |
| Seeds | 101, 202, 303 | Report mean and per-seed variance |

All variants use identical initial states, episode lengths, target sampling,
random seeds, contact geometry, force limits, and data split. Training rows are
split by complete episode, never by adjacent timestep.

## Observation and action contract

The fast PI controller receives measured normal force, target force, velocity,
and its bounded integral state. The slow residual observes the existing feature
vector `[force_error, velocity, integral_error, base_control, target_force]` and
holds its output for 25 fast steps. The residual output is clipped before it is
added to the PI command; the final command is clipped again to the force limit.

The four controller variants are defined as follows:

- `pi_only`: no learned output.
- `trajectory_residual`: residual changes the bounded force command only.
- `gain_residual`: residual changes bounded `kp` and `ki` offsets; the fast PI
  loop computes the resulting command.
- `joint_residual`: learns both command and gain offsets under one output bound.

No variant may issue a hardware command. The simulator gate rejects invalid,
non-finite, out-of-range, or unsafe commands before stepping.

## Metrics and acceptance criteria

Report per seed and aggregate mean/std for:

- true and measured force RMSE and tail absolute error;
- maximum penetration, peak contact force, and contact-loss rate;
- maximum command and torque magnitude, limit violations, and safety-gate activations;
- recovery time after a held-out dynamics change;
- training/test episode counts and any discarded rows.

The hypothesis is supported only if the selected residual has lower mean
held-out true-force RMSE than PI-only, its 95% bootstrap interval is reported,
and it does not worsen any predeclared safety metric beyond the configured
tolerance. Otherwise the result is a negative or inconclusive result.

## Reproducibility and safety

Use [`configs/two_rate_residual.yaml`](../../configs/two_rate_residual.yaml) and
expand the evaluation matrix with:

```bash
./.mamba-env/bin/python -m src.two_rate_matrix --config configs/two_rate_residual.yaml --dry-run
```

The matrix runner writes a manifest, config copy, and incremental results under
the configured artifact root. Use `--max-cases 1` with short step overrides for
a local smoke run before scaling.
Every run must record the Git commit, config copy, Python dependency snapshot,
seed, artifact path, and (when a scheduler exists) job ID. Store outputs under
`artifacts/<run-id>` and keep large files outside Git. This design does not
authorize server training without an approved scheduler or explicit lab
reservation, and it does not authorize real-robot commands.

## Smallest falsifying run

Before a full matrix, run one seed with a short training set and evaluation
steps for PI-only and `joint_residual`. The run is useful only if it verifies
the two-rate hold behavior, command bounds, deterministic reset, and metric
logging. A failure of any of these contracts blocks scaling the matrix.

The runner and a shorter CPU smoke test are implemented in
`src/two_rate_residual.py` and `tests/test_two_rate_residual.py`. The smoke
configuration used two training episodes, 20 steps per episode, 40 evaluation
steps, and a five-fast-step residual hold. It completed with contacts observed,
maximum penetration below the configured limit, zero safety-gate activations,
and deterministic repeated output. The short `joint_residual` comparison had
PI-only true-force RMSE about 2.946 N versus residual RMSE about 2.978 N; this
is an under-trained interface check and must not be interpreted as evidence
against the hypothesis.

The same contract was rechecked on commit `8dda563` with seed `101` and the
command below. The runner produced 40 dataset rows split 20/20 by episode and
zero safety-gate activations. PI-only versus `joint_residual` true-force RMSE
was `2.9338` versus `2.9100` N, with maximum penetration `0.454` versus
`0.432` mm. Both variants had a `0.4` contact-loss rate in this deliberately
short window, so the result is a contract/logging check only and does not
support the hypothesis.

```bash
./.mamba-env/bin/python -m src.two_rate_residual \
  --variant joint_residual --episodes 2 --steps 20 --eval-steps 40 \
  --residual-period-fast-steps 5 --seed 101 --output /tmp/two-rate-smoke.json
```

## Formal matrix result

The complete Cartesian matrix was rerun on the current implementation and
completed 384/384 cases locally on 2026-08-29. The artifact directory is
`artifacts/two-rate-residual/matrix-full-20260829-r3/`; its manifest records Git
commit `296b67667177569ff1ed3e376bd0d531b0a9ff7a` and the locked package
snapshot. Each variant has 96 cases (two target forces, three seeds, two
friction values, two stiffness values, two noise levels, and two delays).

| Variant | True-force RMSE (N) | Paired delta vs PI (N) | Bootstrap 95% CI for delta (N) | Mean max penetration (m) | Safety gates |
| --- | ---: | ---: | --- | ---: | ---: |
| PI-only | 1.26684 | -- | -- | 0.0005303 | 0 |
| trajectory residual | 1.26965 | +0.00281 | [+0.00088, +0.00475] | 0.0005167 | 0 |
| gain residual | 1.27229 | +0.00545 | [+0.00304, +0.00796] | 0.0005278 | 0 |
| joint residual | 1.26554 | -0.00130 | [-0.00188, -0.00077] | 0.0005247 | 0 |

The joint residual is slightly better than PI-only on this task-local matrix,
while the other residual interfaces are slightly worse. All variants stayed
below the 0.001 m penetration limit and had zero safety-gate activations. The
effect is small, so this is evidence for a narrow follow-up rather than a
general force-control or sim-to-real claim. The summary was generated with
`src/analyze_two_rate_matrix.py` using 2,000 bootstrap replicates; per-case
results and checksums remain in the ignored artifact directory. Reproduce the
summary with:

```bash
./.mamba-env/bin/python -m src.analyze_two_rate_matrix \
  artifacts/two-rate-residual/matrix-full-20260829-r3/results.json \
  --output artifacts/two-rate-residual/matrix-full-20260829-r3/summary.json \
  --replicates 2000 --seed 0
```

Render the dependency-free SVG figure from that summary with:

```bash
./.mamba-env/bin/python -m src.plot_matrix_summary \
  artifacts/two-rate-residual/matrix-full-20260829-r3/summary.json \
  --output artifacts/two-rate-residual/matrix-full-20260829-r3/matrix-summary.svg
```

The generated figure stays alongside the ignored run artifacts and is not
tracked by Git.

The exact controller equations, residual decoding, target construction, metric
definitions, and config/interface traceability are recorded in
[`two-rate-residual-equations.md`](two-rate-residual-equations.md).

## Follow-up gates

1. [x] Implement the two-rate runner and unit tests on the existing MuJoCo scene.
2. [x] Run the smallest falsifying CPU smoke test locally.
3. [x] Run and review the complete three-seed matrix locally as a CPU
   reproducibility/statistics check. A server GPU rerun is still blocked until
   the lab provides Slurm or an explicit reservation policy.
4. Compare with the contact-log schema and replay safety gate before any hardware
   discussion.
