# Task: Public literature source adapters

Read `docs/PROJECT_VISION.md` immediately before filling this task.

## Scope

- Branch: `codex/literature-public-sources`
- Project priority: Evidence and reproducibility
- Stage gate: Literature
- Related policy: `configs/literature_sources.yaml`, `docs/literature/README.md`
- Dependencies or blockers: WoS/SCI, CNKI/万方, and publisher full text still require the university portal or an authorized publisher route

## Objective

Make the repository discovery command match the documented public-source
workflow by querying OpenAlex, Crossref, Semantic Scholar, and arXiv while
retaining a strict `metadata-only` boundary until an official or authorized
full text is verified.

## Expected artifact

- `scripts/literature-query.py` source adapters and `--sources` selector
- Unit tests for source normalization, parsing, filtering, and source selection
- Updated literature workflow documentation

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined: OpenAlex/Crossref metadata versus Semantic Scholar/arXiv discovery enrichment
- [x] Fixed query, source list, and evidence status are recorded
- [x] Failure behavior is documented; source errors are isolated and no portal access is attempted

## Verification

```bash
.mamba-env/bin/python -m pytest -q tests/test_literature_query.py
.mamba-env/bin/python scripts/literature-query.py --help
.mamba-env/bin/python scripts/check-literature-sources.py
```

## Completion note

- Git commit: pending
- Test output: pending
- Artifact path: transient discovery JSON under `/tmp`; no PDF or credential enters Git
- Known limitations: Public adapters do not replace WoS/SCI indexing or CNKI/万方 full-text verification
- Follow-up task: Select and download one authorized paper for each Chinese research axis
