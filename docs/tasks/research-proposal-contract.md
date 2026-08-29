# Task: research proposal contract

Read `docs/PROJECT_VISION.md` immediately before this task.

## Scope

- Branch: `codex/research-proposal-contract`
- Project priority: evidence and reproducibility, compliant interaction, and embodied learning
- Stage gate: literature evidence to experiment design
- Related literature notes: `docs/literature/notes/learning-force-control-2003.00628.md`, `docs/literature/notes/multi-contact-whole-body-force-control-2024.md`, and `docs/literature/related-work-taxonomy.md`
- Dependencies or blockers: authorized survey/CNKI full text and a selected robot/sensor platform are still required before hardware claims

## Objective

Create a reviewable proposal layer between literature notes and individual
experiment records. The proposal must state one falsifiable question, map
evidence to design choices, decompose the work into focused branches, and make
the go/no-go conditions explicit.

## Inputs and outputs

- Inputs: the project vision, verified paper notes, the platform-neutral MuJoCo interface, and the existing two-rate residual study
- Expected artifacts: `docs/proposals/README.md`, `docs/proposals/template.md`, and `docs/proposals/two-rate-residual-contact.md`
- Expected verification: proposal links resolve and the repository test/preflight suite remains green

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A falsifiable question, baseline, variables, metrics, and safety boundary are recorded
- [x] Literature evidence and evidence gaps are separated
- [x] Follow-up branches have explicit dependencies and smallest verification commands
- [x] No hardware command path is enabled

## Verification

```bash
bash scripts/preflight.sh local
./.mamba-env/bin/python -m pytest -q
```

## Completion note

- Git commit: pending
- Test output: pending
- Artifact path: committed proposal documents; experiment outputs remain under ignored `artifacts/`
- Known limitations: the proposal is platform-neutral until the robot and sensor are selected
- Follow-up task: obtain authorized contact-manipulation and Chinese full texts, then review this proposal
