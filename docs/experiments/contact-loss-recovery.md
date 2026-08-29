# Contact Loss and Recovery

## Question and hypothesis

Can a bounded PI force loop recover a target normal force after a short,
repeatable outward disturbance causes contact loss without exceeding force,
penetration, or command limits?

The hypothesis is that the transparent fast loop will regain contact under the
synthetic fixture, while the explicit loss and recovery metrics expose when a
controller merely produces a high peak force or never re-establishes contact.

## MuJoCo fixture and disturbance

- Scene: the one-dimensional normal-contact fixture from
  `src/contact_force_baseline.py`.
- Target force: 5 N.
- Timestep: 0.002 s (500 Hz equivalent).
- Disturbance: add a 0.2 m/s outward velocity at step 300; this is a synthetic
  state disturbance and is not a hardware command.
- Loss threshold: force <= 0.05 N.
- Recovery: force >= 90% of target for five consecutive steps.

The committed configuration is `configs/contact_loss_recovery.yaml`. The run
records the first loss and recovery steps, loss duration, recovery time, peak
post-disturbance force, penetration, command/force limit violations, and safety
gate activations. A run with no detected loss is not counted as a recovery
result; a loss without a qualifying hold period is an explicit failure.

## Reproducibility and acceptance

```bash
./.mamba-env/bin/python -m src.contact_loss_recovery
./.mamba-env/bin/python -m src.contact_loss_recovery \
  --steps 900 --disturbance-step 300 --separation-impulse 0.2
./.mamba-env/bin/python -m pytest -q tests/test_contact_loss_recovery.py
```

The baseline acceptance run must detect both loss and recovery, have zero
command/force-limit violations and zero safety-gate activations, and report a
finite recovery time. The result is a task-local MuJoCo robustness statement;
it is not evidence of sim-to-real transfer or a real robot safety guarantee.

A larger 1.0 m/s impulse is an intentional negative control for this PI
baseline: it should expose the current integral-windup failure through the
force-limit and safety-gate metrics. It must remain in the report as a failed
condition rather than being filtered out.

## Follow-up matrix

Repeat over impulse magnitude, force target, damping, actuator delay, sensor
noise, and controller gains. Keep the disturbance step and episode seed in the
run manifest, report runs that fail to recover, and compare all variants with
the same loss/recovery thresholds. Promote to hardware only after measured
limits, calibrated sensor data, offline replay, watchdog, E-stop, and operator
sign-off satisfy the project vision gates.
