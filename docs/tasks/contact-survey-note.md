# Task: Contact-manipulation survey note

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/contact-survey-note`
- Project priority: Evidence and reproducibility; compliant interaction
- Stage gate: Literature
- Expected artifact: structured survey note and one MuJoCo follow-up mapping
- Related literature notes: `docs/literature/related-work-taxonomy.md`, `docs/literature/paper-note-template.md`
- Dependencies or blockers: The publisher/portal PDF is still pending; a legal arXiv v3 preprint is available for the structured note

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
- [x] PDF provenance and SHA-256 are recorded; no portal credentials are stored
- [x] Translation, terminology, methods, interfaces, baselines, metrics,
  limitations, and reproducibility details are filled in
- [x] At least one survey observation becomes a falsifiable MuJoCo test
- [x] `metadata-only` is not used as full-text evidence

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python scripts/check-paper-notes.py \
  --require-full-text --verify-files
```

## Completion note

- Git commit: `a4a83f1`
- Test output: `4/4` paper notes valid with verified hashes; local test suite passed
- Artifact path: `/mnt/research-data/literature/pdfs/contact-survey-104224.pdf`
- Known limitations: This note is based on the legal arXiv v3 preprint; it
  cannot replace publisher/portal version verification, primary-paper details,
  or measured hardware specifications.
- Follow-up task: `codex/chinese-force-control-notes` or a focused MuJoCo test
