# Public metadata discovery refresh: force control and humanoid contact

This is a discovery log, not a completed literature review. Every candidate
below remains `metadata-only` until the final publication is verified and read
through a publisher or the authorized university portal.

## Search session

- Date: 2026-08-30 (Asia/Shanghai)
- Repository tool: `scripts/literature-query.py`
- Public sources queried: OpenAlex Works API and Crossref Works API
- Filters: publication year >= 2020, maximum 12 records per query, DOI/title
  deduplication
- Transient outputs: `/tmp/lit-force-20260830.json`,
  `/tmp/lit-humanoid-20260830.json`, `/tmp/lit-cn-force-20260830.json`
- Source errors: none reported by the tool

## Query matrix and selected candidates

| Axis | Exact query | Selected candidate | Venue/year and DOI | Evidence status |
| --- | --- | --- | --- | --- |
| Arm contact force learning | `robot manipulator contact force control learning` | Unified Method for Task-Space Motion/Force/Impedance Control of Manipulator With Unknown Contact Reaction Strategy | IEEE RA-L, 2022; `10.1109/LRA.2021.3139675` | Metadata-only; portal verification required |
| Arm contact force learning | same query | Image-Based Time-Varying Contact Force Control of Aerial Manipulator Using Robust Impedance Filter | IEEE RA-L, 2024; `10.1109/LRA.2024.3382963` | Metadata-only; portal verification required |
| Humanoid multi-contact | `humanoid whole-body multi-contact force control` | Dynamic Complementarity Conditions and Whole-Body Trajectory Optimization for Humanoid Robot Locomotion | IEEE T-RO, 2022; `10.1109/TRO.2022.3183785` | Metadata-only; portal verification required |
| Humanoid multi-contact | same query | Constraint-consistent task-oriented whole-body robot formulation | IJRR, 2022; `10.1177/02783649221120029` | Metadata-only; portal verification required |
| Humanoid sensing/contact | same query | A soft thumb-sized vision-based sensor with accurate all-round force perception | Nature Machine Intelligence, 2022; `10.1038/s42256-021-00439-3` | Metadata-only; portal verification required |
| Chinese force control | `机械臂 导纳控制 力传感器` | Neural Network Adaptive Force Tracking Admittance Control for Spinning Yarn Piecing Robot | Journal of Mechanical Engineering, 2023; `10.3901/jme.2023.11.221` | Metadata-only; CNKI/万方 record and PDF required |

## Interpretation and limits

The English pass returned relevant top-venue candidates for task-space force
control, humanoid contact dynamics, and tactile/force sensing. The Chinese
public-index pass was low precision and mixed in unrelated sensing papers;
therefore it is only a terminology probe. The three Chinese axes remain to be
searched directly in CNKI/万方 by title, keyword, and abstract fields through
the school portal.

No abstract, DOI record, or public-index ranking is treated as evidence for a
method claim, baseline, equation, or performance number. The next action for
each retained candidate is: verify the final venue/version in the portal,
download the authorized PDF to `/mnt/research-data/literature/pdfs/`, record its
SHA-256, then create a structured note with `scripts/create-paper-note.py`.

## Reproduction commands

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator contact force control learning" \
  --year-from 2020 --limit 12 --output /tmp/lit-force-20260830.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole-body multi-contact force control" \
  --year-from 2020 --limit 12 --output /tmp/lit-humanoid-20260830.json
./.mamba-env/bin/python scripts/literature-query.py \
  "机械臂 导纳控制 力传感器" \
  --year-from 2020 --limit 12 --output /tmp/lit-cn-force-20260830.json
```
