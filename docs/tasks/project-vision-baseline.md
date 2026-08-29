# Task: Promote the project vision and workflow baseline

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/project-vision-baseline`
- Project priority: Evidence and reproducibility
- Stage gate: Platform and evidence baseline
- Expected artifact: the shared vision, literature policy, Git/Codex guide,
  server safety workflow, and their local verification checks available from
  `main`
- Dependencies: none

## Objective

Make the project charter and its entry rules available on the default branch so
every future task starts from the same MuJoCo-first research loop. Keep
experiment-specific results and pending Chinese full-text work on their focused
branches.

## Acceptance criteria

- [ ] `docs/PROJECT_VISION.md` states the north-star goal, stage gates, and
  branch rule.
- [ ] Chinese overview, literature source policy, portal handoff, Git/Codex
  guide, and shared-server safety policy are linked from the project entry
  points.
- [ ] Local checks validate branch-task and literature-source contracts.
- [ ] No credentials, private keys, PDFs, checkpoints, or generated artifacts
  are added to Git.

## Verification

```bash
git diff --check
bash scripts/preflight.sh local
python -m pytest -q
```

## Completion note

- Git commit:
- Test output:
- Artifact path: none; this is a documentation and validation baseline
- Known limitations: server GPU training remains gated because no scheduler or
  approved reservation policy is available.
