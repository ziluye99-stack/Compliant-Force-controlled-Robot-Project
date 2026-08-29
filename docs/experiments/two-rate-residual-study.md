# Two-rate residual force-control study

## Task statement

- Branch: `codex/two-rate-residual-runner`
- Project priorities: compliant interaction, embodied learning, and evidence/reproducibility
- Stage gate: Simulation implementation and contract validation
- Related literature: [`learning-force-control-2003.00628.md`](../literature/notes/learning-force-control-2003.00628.md) and [`related-work-taxonomy.md`](../literature/related-work-taxonomy.md)
- Expected artifact: a reproducible MuJoCo experiment comparing a fast PI loop with bounded lower-rate residual policies
- Current status: runner and contract tests implemented; full matrix not run

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

## Follow-up gates

1. [x] Implement the two-rate runner and unit tests on the existing MuJoCo scene.
2. [x] Run the smallest falsifying CPU smoke test locally.
3. Run the complete matrix only after the local contract passes and a server
   resource-allocation policy is confirmed.
4. Compare with the contact-log schema and replay safety gate before any hardware
   discussion.
