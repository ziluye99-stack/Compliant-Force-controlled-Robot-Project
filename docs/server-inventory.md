# Shared Server Inventory

Inventory date: 2026-08-29

## Host

- SSH alias: `research-gpu`
- Account: `gbu`
- OS: Ubuntu 24.04.4 LTS
- Kernel: `7.0.0-30-generic`
- Project path: `/home/gbu/research/Compliant-Force-controlled-Robot-Project`
- Branch worktrees: `/home/gbu/research/worktrees/codex-<task-name>`

## GPUs and CUDA

The host has two NVIDIA GeForce RTX 5090 GPUs, each with 32607 MiB of memory.
The installed NVIDIA driver is `580.178.04`, and `nvidia-smi` reports CUDA
compatibility version `13.0`.

This is a driver compatibility report, not proof that the CUDA Toolkit is
installed. There is currently no `nvcc` and no `/usr/local/cuda*` toolkit tree.
PyTorch wheels in the existing environments bundle the CUDA runtime they need,
so they can use the GPUs without a system-wide toolkit.

## Existing user environments

| Environment | Python | PyTorch | CUDA | GPUs |
| --- | --- | --- | --- | --- |
| `/home/gbu/miniconda3/envs/pytorch` | 3.13.12 | 2.11.0+cu130 | 13.0 | 2 |
| `/home/gbu/miniforge3/envs/lerobot_rm65` | 3.12.13 | 2.13.0+cu130 | 13.0 | 2 |
| `/home/gbu/miniforge3/envs/compliant-force-robot` | 3.11.16 | no PyTorch yet | n/a | n/a |

The project environment contains MuJoCo, NumPy, PyYAML, and pytest. Existing
environments were inspected but not modified.

## Verified branch execution

On 2026-08-29, the GitHub branch `codex/research-proposal-contract` was fetched
into `/home/gbu/research/worktrees/codex-research-proposal-contract` without
changing the main checkout. The worktree is currently clean at commit
`5bf3e8e`. With
`/home/gbu/miniforge3/envs/compliant-force-robot/bin/python`, the current
commit passed `src.experiment --config configs/sim.yaml --dry-run` and a
100-step `src.mujoco_smoke` run. The dry-run recorded MuJoCo 3.12.0, Python
3.11.16, the platform-neutral interface, and no Slurm job ID.

## Other software found

The following commands are not currently available in the user environment:
`ros2`, `colcon`, `gazebo`, `gz`, `docker`, `podman`, `apptainer`, and `nvcc`.

Existing user projects include LeRobot (`/home/gbu/lerobot`), RealMan-related
files (`/home/gbu/realman65`), and PIDNN (`/home/gbu/PIDNN`). No files in those
projects were changed by this inventory.

## Scheduler decision

`sinfo`, `squeue`, `sbatch`, `srun`, `slurmctld`, and `slurmd` are absent, and
there is no user-visible Slurm configuration. This is therefore a shared GPU
workstation with no verified scheduler, not a Slurm compute node.

Do not install a standalone Slurm node on this machine. A useful Slurm setup
requires an approved controller, Munge authentication, node and partition
configuration, accounting policy, and administrator coordination. Installing
only `slurmd` locally would not provide safe multi-user scheduling and could
interfere with the workstation. Until the lab supplies those details, use only
short, explicitly coordinated checks; do not launch long training jobs here.

## Low-impact GPU smoke test

This test uses GPU 1 for a small tensor operation and releases it immediately:

```bash
ssh research-gpu 'CUDA_VISIBLE_DEVICES=1 /home/gbu/miniconda3/envs/pytorch/bin/python -c "import torch; x=torch.arange(1024,device=\"cuda\",dtype=torch.float32); print(torch.cuda.get_device_name(0), float((x*x).sum()))"'
```

Always inspect `nvidia-smi` first and never terminate processes owned by other
users. GPU visibility is not a resource reservation.
