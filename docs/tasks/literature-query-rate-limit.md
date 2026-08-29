# Task: literature query rate-limit handling

Read `docs/PROJECT_VISION.md` immediately before this task.

## Scope

- Branch: `codex/literature-query-rate-limit`
- Project priority: evidence and reproducibility
- Stage gate: literature evidence
- Related literature notes: `docs/literature/README.md`, `docs/literature/search-log-2026-08-29.md`
- Dependencies or blockers: publisher and CNKI/万方 full text still require the university portal

## Objective

Make public OpenAlex/Crossref discovery runs more reproducible when a source
returns HTTP 429, without bypassing access controls or treating metadata as
full-text evidence.

## Expected artifact

- Bounded HTTP 429 retry behavior in `scripts/literature-query.py`
- Unit tests covering retry, exhaustion, and disabled retry
- A documented command-line control for retry behavior

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] Retry is limited to HTTP 429 and has a bounded delay
- [x] Non-429 errors remain visible to the caller
- [x] Result records retain the metadata-only evidence boundary
- [x] No portal credentials, PDFs, or publisher access controls are touched

## Verification

```bash
./.mamba-env/bin/python -m pytest -q tests/test_literature_query.py
./.mamba-env/bin/python scripts/literature-query.py --help
```

## Completion note

- Git commit:
- Test output:
- Artifact path: none; query JSON remains transient outside Git
- Known limitations: a source can still remain unavailable after the bounded retry
- Follow-up task: obtain selected full texts through the authorized university portal
