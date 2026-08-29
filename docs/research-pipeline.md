# End-to-End Research Pipeline

This is the operating procedure for the project. The default simulation
platform is MuJoCo. The laptop is the control, editing, visualization, and
supervised hardware-validation endpoint; `research-gpu` is the compute
endpoint; `/mnt/research-data` is the local archive. The pipeline is:

```text
vision -> literature evidence -> research gap -> experiment contract
-> task decomposition -> MuJoCo implementation -> data/training
-> evaluation/ablation -> supervised hardware validation -> paper/release
```

Every stage produces a small, reviewable artifact. A later stage cannot hide a
missing safety or reproducibility requirement from an earlier stage.

## 0. Start from the project charter

Before creating a branch or starting a substantial task:

1. Read `docs/PROJECT_VISION.md`.
2. Create a focused branch named `codex/<topic>`.
3. Fill `docs/tasks/task-template.md` with the relevant priority, stage gate,
   expected artifact, and verification command.
4. Keep one branch focused on one experiment, infrastructure change, or paper
   artifact. Do not mix robot-driver changes with model claims.

The branch is ready to merge only when its acceptance criteria and verification
command have evidence in the completion note.

## 1. Literature discovery and full-text access

### Source hierarchy

Use at least one discovery source and one authoritative publication source for
important claims. SCI is an indexing/retrieval route, not a venue by itself.

| Purpose | Sources to prioritize | Typical use |
| --- | --- | --- |
| Broad metadata and citation graph | Semantic Scholar, OpenAlex, Crossref | DOI, authors, references, citation chaining |
| Latest methods | arXiv and official author/project pages | Recent preprints and supplementary code |
| Robotics top venues | RSS, CoRL, ICRA, IROS, RA-L, IEEE Xplore, T-RO, IJRR, T-ASE, T-Mech, Automatica | Primary robotics and control evidence |
| High-impact science | Nature, Science, Science Robotics, Nature Machine Intelligence | Cross-disciplinary and high-impact results |
| Chinese research | 中国知网（CNKI）, 万方, 学校图书馆 discovery portal | Chinese literature and subscribed full text |
| Implementations | Official GitHub, Papers with Code, project pages | Reproduction inputs; record commit/tag and license |

The `literature-search` skill uses Semantic Scholar and arXiv first, then
metadata services and citation chaining. It cannot inherit the login session
of the school's portal. For access-controlled papers, use the university app
or its browser handoff yourself:

1. Search with both English and Chinese terms.
2. Open the publisher or CNKI result through the authenticated school portal.
3. Download the final paper PDF and supplementary material when permitted.
4. Store the files outside Git, preferably under
   `/mnt/research-data/literature/pdfs/<project>/`.
5. Record DOI, publisher URL, venue, year, access date, and SHA-256 in the
   paper note. Never store portal passwords, cookies, or session exports.

Do not bypass paywalls, scrape access controls, or redistribute subscribed
content. If only a preprint is available, label it as a preprint and retain the
publisher record when one exists.

### Search protocol

Start with a question and add dimensions in this order: embodiment, contact
mode, sensing, controller or learning method, simulator, and metric. Search in
both languages, for example:

```text
"force control" robotic manipulation contact stability
"sim-to-real" compliant manipulation force torque sensor
具身智能 机械臂 力控 接触稳定性
人形机器人 全身柔顺控制 接触 学习
```

For each search session, complete `docs/literature/search-log-template.md`:
record the query, date, filters, source, kept/discarded reason, and candidate
gap. Deduplicate by DOI, then normalized title and author/year. Separate
peer-reviewed papers, preprints, theses, benchmarks, and non-peer-reviewed
posts.

## 2. Read, translate, and assess papers

Create one note from `docs/literature/paper-note-template.md` for every paper
that informs a design or claim. The note must contain:

- a faithful abstract and key-passage translation with a terminology table;
- the problem, assumptions, method, equations, observations, actions, sensors,
  simulator, data, training compute, and controller interface;
- baseline fairness, metrics, statistical treatment, ablations, real-robot
  procedure, and failure cases;
- strengths, weaknesses, hidden assumptions, reproducibility gaps, and a
  smallest MuJoCo follow-up experiment.

Translation is for understanding, not for silently replacing the original
claim. Preserve equation symbols, units, sign conventions, and uncertainty;
flag any passage that needs a second pass. A literature matrix should compare
task, embodiment, contact mode, sensor, controller, policy, simulator, data,
metrics, real-robot evidence, and limitations across papers.

## 3. Turn evidence into a proposal

Before writing code, write an experiment record under `docs/experiments/` that
states one falsifiable hypothesis, independent and controlled variables,
baseline, metrics, expected failure signature, and safety constraints. Link the
literature notes that motivate the gap.

Split a complex proposal into vertical slices:

1. deterministic MuJoCo scene and observation/action contract;
2. transparent non-learning controller;
3. data collection and validation split;
4. first learning baseline;
5. robustness, ablation, and sim-to-real evaluation;
6. hardware replay and supervised validation;
7. figures, equations, paper text, and release artifacts.

Each slice gets its own branch and acceptance command. A failed slice is kept
as evidence and does not get hidden by changing the metric after the run.

## 4. Implement and validate in MuJoCo

MuJoCo is the primary simulator until a documented platform decision changes
it. Implement the smallest scene that can falsify the hypothesis, then lock:

- model and contact parameters;
- observation and action spaces, units, frames, and control rate;
- reset procedure, random seed, and termination/safety conditions;
- force, penetration, stability, task-success, and compute metrics.

Run unit tests and a short deterministic smoke test locally. Only after the
local contract is valid should the same Git revision and config move to the
server. Dynamics randomization, sensor noise, actuator delay, friction, and
contact variation are controlled factors, not unexplained tuning.

Mechanical design is treated as an interface: record CAD revision, mass and
inertia assumptions, joint limits, compliance elements, sensor mounting, and
calibration data. Keep CAD and raw measurement files outside Git when large,
but link their immutable revision or checksum from the experiment note.

## 5. Collect data and train models

Define the data schema before collection: timestamp, episode/run ID, state and
frame conventions, observations, actions, force/torque measurements, contact
labels, termination reason, and calibration/version metadata. Store raw data on
the server or research drive, not in Git.

Use disjoint train/validation/test splits by episode, scene, object, or subject
as appropriate; document leakage checks. Train a transparent baseline first,
with locked environment, config, seed, Git commit, dependency snapshot,
checkpoint path, and metrics. Then add one model component at a time and run
ablations over observations, randomization, controller gains, and data scale.

All long simulation/training jobs must use the lab's approved scheduler or
reservation procedure. This shared server currently has no verified Slurm
service, so do not occupy GPUs directly until that policy is supplied.

## 6. Evaluate, transfer, and validate hardware

Evaluation uses identical metric code for simulation and real data. Report
multiple seeds, confidence intervals or per-seed values, baseline comparisons,
ablation results, and failure cases. Before hardware commands:

- identify robot, firmware, communication path, force/torque sensor, frames,
  calibration, rates, limits, watchdog, emergency stop, safe pose, operator,
  and exclusion zone;
- replay recorded trajectories offline;
- test motors disabled, then low-speed and low-gain under a human operator;
- keep a rollback model and an independent stop path.

No robot-specific driver or autonomous deployment branch is valid without this
information and sign-off.

## 7. Produce paper-quality evidence

Generate plots and tables from logged, versioned data. Record the script,
config, seed, units, confidence treatment, and source run IDs for every figure.
Derive equations from the implemented conventions and cross-check dimensions,
frames, and signs. The paper package includes method, experiment protocol,
baselines, ablations, failures, limitations, reproducibility notes, and an
artifact manifest.

## Storage and ownership

- GitHub: source, configs, docs, small text metrics, and reproducibility scripts.
- Server user directory: environments, active runs, checkpoints, videos, and
  large logs.
- `/mnt/research-data`: verified archive copies and downloaded literature PDFs.
- Laptop: editing, lightweight tests, visualization, and supervised debugging.

Before copying results, run `bash scripts/sync-results.sh --dry-run <run-id>`;
then use the resumable checksum-verified sync and retain the manifest.
