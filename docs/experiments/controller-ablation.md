# Controller and observation ablation

This experiment advances the embodied-learning and reproducibility priorities
at the evaluation gate. It asks whether the residual policy depends on the
full observation contract, whether dynamics randomization helps, and whether
controller gains change the comparison.

The matrix fixes the MuJoCo task, noise, target-force range, and evaluation
seeds. It varies three observations (`full`, `force_error_only`, `no_integral`),
nominal versus randomized training dynamics, and nominal versus low-integral
PI gains. Each row reports baseline and residual force metrics for three seeds.

Run locally with:

```bash
./.mamba-env/bin/python -m src.controller_ablation \
  --train-episodes 6 --train-steps 250 --eval-steps 400 \
  --output artifacts/controller-ablation/results.json
```

The output is ignored by Git and should be archived after review. A lower
force RMSE is not sufficient by itself: compare penetration, contact, control
limits, and seed variance before selecting an observation or gain variant.

The recorded CPU smoke matrix (36 rows, three evaluation seeds) gives a mean
force RMSE of 0.462 N for `force_error_only` with nominal gains, versus 0.466 N
for its PI baseline. The low-integral gain variant is much worse (about 1.56 N
RMSE) for every observation. These are task-local results, not sim-to-real or
hardware claims.
