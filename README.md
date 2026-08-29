# Compliant Force-Controlled Robot Project

Reproducible research scaffold for compliant force-control experiments. The first implementation stage provides experiment metadata, simulator-ready configuration, Slurm-safe job submission, and verified artifact synchronization. It intentionally does not assume a robot model, force sensor, controller, or training algorithm.

## Workspace roles

| Location | Role |
| --- | --- |
| Laptop | Code editing, lightweight MuJoCo validation, visualization, and future supervised hardware debugging |
| `research-gpu` | Slurm-submitted simulation, training, evaluation, and large artifact generation |
| `/mnt/research-data` | Local archival destination for validated result copies |
| GitHub | Source, configs, documentation, and small text metrics only |

## Quick start

1. Create the local environment with `micromamba create -y -p .mamba-env -f environment.yml` and `.mamba-env/bin/pip install -e .[dev]`, or create the server environment from `environment.yml`.
2. Run `.mamba-env/bin/python -m src.experiment --config configs/sim.yaml --dry-run`.
3. Run `bash scripts/preflight.sh local` before local validation.
4. After server access is authorized, run `bash scripts/preflight.sh server`.
5. Set the required Slurm variables and submit with `bash scripts/submit-slurm.sh train`.
6. Archive finished results with `bash scripts/sync-results.sh --dry-run <run-id>` before an actual sync.

If `bash scripts/preflight.sh server` reports `slurm=unavailable`, the host has
visible GPUs but no Slurm client or scheduler configuration. Do not start
training directly on that shared host; obtain the lab's scheduler node or an
explicit resource-sharing policy first.

The current host inventory is recorded in
[`docs/server-inventory.md`](docs/server-inventory.md). It has two RTX 5090
GPUs and usable CUDA-enabled PyTorch environments, but no Slurm, ROS 2, Gazebo,
container runtime, or system CUDA Toolkit. A short GPU smoke test is permitted
for validation; long-running jobs require an approved scheduler or reservation
procedure.

## Experiment contract

Each run has a unique `run_id`, a YAML configuration, and a server-side artifact directory. The run manifest records a random seed, Git revision, dependency snapshot, Slurm job ID, and result path. Generated artifacts never enter Git.

The end-to-end design, simulation, evaluation, archive, and supervised hardware
gates are documented in [`docs/workflow.md`](docs/workflow.md). The baseline
server dependency snapshot is kept in `environment.lock.txt`; regenerate it
with `scripts/setup-server-env.sh` after an intentional environment change.

The current platform-neutral dual-contact MuJoCo fixture is documented in
[`docs/experiments/dual-contact-force-control.md`](docs/experiments/dual-contact-force-control.md).

The versioned platform-neutral system interface is in
[`configs/platform_neutral_interface.yaml`](configs/platform_neutral_interface.yaml);
its required fields and hardware gate are described in
[`docs/system-interface-template.md`](docs/system-interface-template.md).

The project north star and branch-entry rule are in
[`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md). The literature source map,
portal-access rules, and paper note template are in
[`docs/literature/README.md`](docs/literature/README.md).
中文总览、阶段门禁、服务器分工和常用 Codex 请求见
[`docs/科研总览.md`](docs/科研总览.md)。
The concrete school-portal download and Codex handoff checklist is in
[`docs/literature/portal-intake.md`](docs/literature/portal-intake.md).

Git、GitHub、分支和 Codex 终端的操作步骤见
[`docs/git-codex.md`](docs/git-codex.md)。

已安装科研技能、用途、典型调用和暂缓项见
[`docs/codex-skills.md`](docs/codex-skills.md)。

The staged research backlog is in [`docs/roadmap.md`](docs/roadmap.md); use
[`docs/tasks/task-template.md`](docs/tasks/task-template.md) for each focused
branch and [`docs/literature/search-log-template.md`](docs/literature/search-log-template.md)
for a reproducible search session.

## Server policy

The project uses only the `gbu` user space on the shared server. Jobs must request their resources through Slurm. The scripts refuse to submit without explicit account, partition, GPU, CPU, memory, and time settings.
