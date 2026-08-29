# Task: Public metadata discovery refresh

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/literature-discovery-20260830`
- Project priority: Evidence and reproducibility
- Stage gate: Literature
- Related policy: `configs/literature_sources.yaml`

## Objective

Refresh the candidate queue for compliant arm force control, humanoid
multi-contact control, and Chinese force-control terminology using only public
metadata discovery. The result must preserve the boundary between discovery
records and authorized full-text evidence.

## Expected artifact and evidence

- `docs/literature/search-log-2026-08-30.md`
- Updated portal queue with DOI and venue candidates
- No claim promoted without a publisher or authorized university-portal PDF

## Verification

```bash
./.mamba-env/bin/python scripts/check-literature-sources.py
./.mamba-env/bin/python scripts/check-paper-notes.py
```

The public query JSON remains transient under `/tmp`; PDFs and portal exports
remain on `/mnt/research-data` and outside Git.
