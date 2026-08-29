# Task: Chinese force-control literature notes

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/chinese-force-control-notes`
- Project priority: Evidence and reproducibility; compliant interaction
- Stage gate: Literature
- Expected artifact: three structured Chinese-paper notes and a terminology map
- Related literature notes: `docs/literature/README.md`, `docs/literature/portal-intake.md`, `docs/literature/related-work-taxonomy.md`
- Dependencies or blockers: Three authorized CNKI/万方 full texts selected
  through the university portal

## Objective

Build a terminology-aligned comparison of three Chinese papers covering
admittance control, impedance or hybrid position-force control, and humanoid
whole-body or multi-contact control. Identify one measurable gap that can be
tested in MuJoCo without claiming that Chinese metadata alone is evidence.

## Inputs and outputs

- Inputs: Three PDFs in `/mnt/research-data/literature/pdfs/`, each with its
  CNKI/万方 identifier, official URL, access date, and SHA-256
- Expected code/configuration/documentation artifacts: one structured note per
  paper under `docs/literature/notes/`, plus a terminology and comparison-table
  update in `docs/literature/related-work-taxonomy.md`
- Expected experiment run IDs or figures: none; produce a proposed MuJoCo
  experiment record only after the notes identify a falsifiable gap

## Acceptance criteria

- [ ] `docs/PROJECT_VISION.md` was read immediately before branch work
- [ ] Each paper has a verified full-text source and matching SHA-256
- [ ] Chinese abstract/method/experiment content is translated with key terms
  mapped consistently to the project vocabulary
- [ ] Strengths, weaknesses, assumptions, baselines, metrics, and failure cases
  are recorded separately for all three papers
- [ ] At least one conclusion is explicitly marked metadata-only or unsupported
  when the PDF does not provide sufficient evidence

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python scripts/check-paper-notes.py \
  --require-full-text --verify-files
./.mamba-env/bin/python scripts/check-literature-sources.py
```

## Completion note

- Git commit:
- Test output:
- Artifact path:
- Known limitations: Selection must be made through the authorized portal;
  Codex must not receive passwords, cookies, or one-time codes.
- Follow-up task: Review the proposal and map the gap to a MuJoCo config
