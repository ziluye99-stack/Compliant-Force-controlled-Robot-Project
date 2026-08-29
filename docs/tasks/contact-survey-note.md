# Task: Contact-manipulation survey note

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/contact-survey-note`
- Project priority: Evidence and reproducibility; compliant interaction
- Stage gate: Literature
- Expected artifact: structured survey note and one MuJoCo follow-up mapping
- Related literature notes: `docs/literature/related-work-taxonomy.md`, `docs/literature/paper-note-template.md`
- Dependencies or blockers: An authorized publisher or university-portal PDF for DOI `10.1016/j.robot.2022.104224`

## Objective

Determine whether the contact-manipulation survey supports a concrete MuJoCo
experiment by extracting its taxonomy, contact assumptions, interfaces,
baselines, metrics, and reported failure modes. The note must distinguish
claims supported by the survey from claims that require primary papers.

## Inputs and outputs

- Inputs: `/mnt/research-data/literature/pdfs/contact-survey-104224.pdf`, DOI,
  stable publisher or portal URL, access date, and SHA-256
- Expected code/configuration/documentation artifacts:
  `docs/literature/notes/contact-survey-104224.md` and an update to the related-
  work taxonomy if a classification changes
- Expected experiment run IDs or figures: none; propose at least one falsifiable
  MuJoCo follow-up and map its variables to an existing config

## Acceptance criteria

- [ ] `docs/PROJECT_VISION.md` was read immediately before branch work
- [ ] PDF provenance and SHA-256 are recorded; no portal credentials are stored
- [ ] Translation, terminology, methods, interfaces, baselines, metrics,
  limitations, and reproducibility details are filled in
- [ ] At least one survey observation becomes a falsifiable MuJoCo test
- [ ] `metadata-only` is not used as full-text evidence

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python scripts/check-paper-notes.py \
  --require-full-text --verify-files
```

## Completion note

- Git commit:
- Test output:
- Artifact path:
- Known limitations: The survey cannot replace primary-paper verification or
  measured hardware specifications.
- Follow-up task: `codex/chinese-force-control-notes` or a focused MuJoCo test
