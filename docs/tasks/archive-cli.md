# Task: Explicit archive artifact root

Read `docs/PROJECT_VISION.md` before filling this task.

## Scope

- Branch: `codex/archive-cli`
- Project priority: Evidence and reproducibility
- Stage gate: Evaluation and archive
- Related literature notes: None
- Dependencies or blockers: Research drive mounted at `/mnt/research-data`; SSH alias `research-gpu`

## Objective

Make result archiving reproducible for runs produced in branch-specific server
worktrees by allowing the remote artifact root to be supplied on the command
line, with the CLI value taking precedence over `REMOTE_ARTIFACT_ROOT`, and
run the same branch/evidence/MuJoCo checks automatically in Pull Requests.

## Inputs and outputs

- Inputs: A run ID and a server artifact root.
- Expected artifact: Updated `scripts/sync-results.sh`, workflow usage, focused test, and `.github/workflows/ci.yml`.
- Expected experiment run IDs or figures: Dry-run preview for the archived two-rate server smoke.

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
git diff --check
bash scripts/sync-results.sh --dry-run \
  --remote-artifact-root /home/gbu/research/Compliant-Force-controlled-Robot-Project/artifacts/two-rate-residual \
  two-rate-server-smoke-20260830
```

## Completion note

- Git commit: `635062a Make archive artifact root explicit`
- Test output: `bash scripts/preflight.sh local`; `83 passed`; archive dry-run exit 0
- Artifact path: `/mnt/research-data/Compliant-Force-controlled-Robot-Project/two-rate-server-smoke-20260830/`
- Known limitations: The command still requires the research drive to be mounted and an accessible SSH source.
- Follow-up task: Add scheduler-specific archive metadata once the lab provides an approved scheduler.
