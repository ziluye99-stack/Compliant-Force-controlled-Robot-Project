# Contact Loss Recovery Robustness Matrix

## Question and hypothesis

How does the bounded MuJoCo PI force loop degrade when contact-loss recovery is
tested across measured-proxy mismatch variables rather than one nominal case?
The hypothesis is that small noise, damping changes, and short command delays
preserve safe recovery, while larger separation impulses or combined mismatch
conditions expose explicit recovery or safety failures.

## Matrix contract

The runner is `src/contact_loss_recovery_matrix.py` and the committed matrix is
`configs/contact_loss_recovery_matrix.yaml`. It evaluates the Cartesian product
of:

- outward separation impulse: 0.2, 0.5, 1.0 m/s;
- force sensor noise standard deviation: 0.0, 0.1 N;
- damping scale: 0.5, 1.0, 2.0;
- actuator command delay: 0, 2 simulation steps (0.002 s per step).

All cases use the same seed and disturbance step so differences can be
attributed to the listed axis. The recovery criterion remains at least 90% of
the target force for five consecutive steps. `safe_recovery` additionally
requires zero command-limit, force-limit, and safety-gate violations.

## Reproduction

```bash
./.mamba-env/bin/python -m src.contact_loss_recovery_matrix \
  --steps 1200 --disturbance-step 300 \
  --output /tmp/contact-loss-recovery-matrix.json
```

The JSON uses `contact-loss-recovery-matrix/v1`, includes every case and the
aggregate safe/failure counts, and intentionally retains failed cases. It is a
simulation robustness result only; sensor noise and damping are proxies until
the selected robot supplies measured logs.

## Evidence boundary and follow-up

The matrix does not establish sim-to-real transfer or a hardware safety
guarantee. After a robot and force sensor are selected, replace the proxy axes
with measured uncertainty ranges, calibrate the MuJoCo parameters, and replay
real contact logs offline before any supervised hardware test.
