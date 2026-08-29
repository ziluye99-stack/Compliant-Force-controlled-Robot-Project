# Seed search: contact-rich force control and humanoid contact

This is a discovery log, not a completed literature review. Candidate papers
must be opened through a publisher, preprint, or school-portal copy and then
receive a paper note before they support a design claim.

## Search record

- Date: 2026-08-29 (Asia/Shanghai)
- Primary discovery API: OpenAlex Works API
- DOI/venue cross-check: Crossref Works API
- Queries: `robot force control manipulation`; `humanoid whole body contact control`; `sim-to-real force control robot`
- Filter: publication date from 2019 or 2020 depending on query, type `article`, sorted by API relevance
- Deduplication key: DOI, then normalized title
- Access result: public arXiv PDF downloaded for the RA-L force-learning paper;
  remaining candidates are metadata-only or require the school portal
- Limitation: Semantic Scholar returned HTTP 429 during this run; CNKI and subscription publishers require the school's portal session

## Follow-up access check

- Date: 2026-08-29 (Asia/Shanghai)
- Metadata/provenance: OpenAlex and Unpaywall both report the survey as a
  hybrid open-access article with a CC-BY license and list the Aalto repository
  copy plus the ScienceDirect PDF endpoint.
- Retrieval result: direct requests to both listed PDF endpoints returned HTTP
  403 from this environment. No access control was bypassed and no PDF was
  treated as obtained.
- Next authorized action: open the Aalto/ScienceDirect record through the
  university library portal, download the publisher or accepted-manuscript PDF,
  and provide its local path for the structured note.

## Candidates for reading

| Candidate | Venue/year | DOI | Why it enters the queue | Status |
| --- | --- | --- | --- | --- |
| Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots | IEEE RA-L, 2020 | [10.1109/LRA.2020.3010739](https://doi.org/10.1109/LRA.2020.3010739); [arXiv:2003.00628](https://arxiv.org/abs/2003.00628) | Direct force-learning baseline for contact-rich manipulation | Full text read; [structured note](notes/learning-force-control-2003.00628.md) |
| A survey of robot manipulation in contact | Robotics and Autonomous Systems, 2022 | [10.1016/j.robot.2022.104224](https://doi.org/10.1016/j.robot.2022.104224); [repository copy](https://research.aalto.fi/files/87131047/1_s2.0_S0921889022001312_main.pdf) | Taxonomy and evaluation dimensions for contact tasks | Metadata only |
| Force Sensorless Admittance Control With Neural Learning for Robots With Actuator Saturation | IEEE T-IE, 2019 | [10.1109/TIE.2019.2912781](https://doi.org/10.1109/TIE.2019.2912781) | Sensorless/admittance comparison and saturation constraints | Metadata only |
| A Unified Parametric Representation for Robotic Compliant Skills With Adaptation of Impedance and Force | IEEE/ASME T-Mech, 2021 | [10.1109/TMECH.2021.3109160](https://doi.org/10.1109/TMECH.2021.3109160) | Compliant skill parameterization relevant to reusable interfaces | Metadata only |
| Crossing the Reality Gap: A Survey on Sim-to-Real Transferability of Robot Controllers in Reinforcement Learning | IEEE Access, 2021 | [10.1109/ACCESS.2021.3126658](https://doi.org/10.1109/ACCESS.2021.3126658) | Transfer variables and evaluation language | Metadata only |
| Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors | IEEE RA-L, 2024 | [10.1109/LRA.2024.3475052](https://doi.org/10.1109/LRA.2024.3475052) | Humanoid multi-contact and tactile sensing direction | Metadata only |
| Dynamic locomotion for passive-ankle biped robots and humanoids using whole-body locomotion control | IJRR, 2020 | [10.1177/0278364920918014](https://doi.org/10.1177/0278364920918014) | Whole-body control and contact constraints for larger embodiments | Metadata only |

## Next reading action

Start with the survey and the RA-L force-learning paper. For each PDF, create
`docs/literature/notes/<slug>.md` using `paper-note-template.md`, record the
publisher/preprint URL and SHA-256 of the downloaded PDF, then extract the
task, sensor, controller, simulator, real-robot evidence, metrics, ablations,
failure cases, and limitations. A paper is not considered evidence for the
project until that note exists.

## Multi-axis discovery refresh

- Date: 2026-08-29 (Asia/Shanghai)
- Primary metadata source: Crossref Works API (`query.bibliographic`)
- Queries: `robot contact force control`; `humanoid whole-body multi-contact control`; `sim-to-real force control robot`
- Filters: journal articles from 2020 onward where the API exposed a date and DOI
- Ranking: title relevance followed by venue priority; DOI deduplication
- Full-text status: all entries below are `metadata-only` until verified through
  IEEE/Elsevier/publisher pages or the university portal

| Candidate | Venue/year | DOI | Axis | Status |
| --- | --- | --- | --- | --- |
| Multi-Contact Whole-Body Force Control for Position-Controlled Robots | IEEE RA-L, 2024 | [10.1109/LRA.2024.3396094](https://doi.org/10.1109/LRA.2024.3396094) | Humanoid/whole-body contact | Metadata only |
| Real-Time Deformable-Contact-Aware Model Predictive Control for Force-Modulated Manipulation | IEEE T-RO, 2023 | [10.1109/TRO.2023.3286070](https://doi.org/10.1109/TRO.2023.3286070) | Contact modeling and force modulation | Metadata only |
| Jerk Control of Floating Base Systems With Contact-Stable Parameterized Force Feedback | IEEE T-RO, 2021 | [10.1109/TRO.2020.3005547](https://doi.org/10.1109/TRO.2020.3005547) | Floating-base/contact stability | Metadata only |
| Robot peg-in-hole assembly based on contact force estimation compensated by convolutional neural network | Control Engineering Practice, 2022 | [10.1016/j.conengprac.2021.105012](https://doi.org/10.1016/j.conengprac.2021.105012) | Force estimation and assembly | Metadata only |
| Contact force cancelation in robot impedance control by target impedance modification | Robotica, 2023 | [10.1017/S0263574723000103](https://doi.org/10.1017/S0263574723000103) | Impedance adaptation | Metadata only |

These candidates expand the queue along the project taxonomy: learned force
interfaces, model-based contact prediction, floating-base stability, and
assembly force estimation. The next step is authorized full-text retrieval via
the school portal, followed by one structured note per paper; CNKI/万方 results
will be added through the same process after portal login.

## Public metadata tool verification

- Date: 2026-08-29 (Asia/Shanghai)
- Command: `scripts/literature-query.py "robot manipulator contact force control" --year-from 2022 --limit 5`
- Sources queried: OpenAlex and Crossref
- Result: 5 deduplicated metadata records; both sources returned successfully
- Evidence boundary: all records remain `metadata-only` until the final paper
  is obtained from a publisher or the authorized university portal
- Reproduction output: the JSON result was written to `/tmp` during validation;
  generated query output is not committed as a research claim

## Public discovery refresh (executed 2026-08-29)

The following four-axis pass was run with the repository tool. Each command
queried both OpenAlex and Crossref, used a publication-year lower bound of
2020, returned at most 12 records per source, and wrote transient JSON output
under `/tmp` (not into Git). All returned records remain `metadata-only`.

| Axis | Exact query | Output | Selected candidates for authorized full-text retrieval |
| --- | --- | --- | --- |
| Arm contact force learning | `robot manipulator contact force control learning` | `/tmp/arm-literature.json` | Learning Force Control (RA-L 2020, DOI `10.1109/LRA.2020.3010739`); Unified task-space motion/force/impedance control (RA-L 2022, DOI `10.1109/LRA.2021.3139675`) |
| Humanoid multi-contact | `humanoid whole body multi contact force control` | `/tmp/humanoid-literature.json` | Constraint-consistent task-oriented whole-body formulation (IJRR 2022, DOI `10.1177/02783649221120029`); Whole-Body Multi-Contact Motion Control (RA-L 2024, DOI `10.1109/LRA.2024.3475052`) |
| Transfer and force modulation | `sim-to-real compliant contact force control robot` | `/tmp/sim2real-literature.json` | Real-Time Deformable-Contact-Aware MPC (T-RO 2023, DOI `10.1109/TRO.2023.3286070`); Contact Force Control with Continuously Compliant Robotic Legs (ICRA 2023, DOI `10.1109/ICRA48891.2023.10160269`) |
| Chinese terminology probe | `机械臂 接触 力控制 仿真` | `/tmp/chinese-literature.json` | Public-index results were low precision; repeat through CNKI/万方 with title/keyword/abstract fields and terms `导纳控制`, `阻抗控制`, `混合位置力控制` |

The commands are reproducible from the repository root:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator contact force control learning" \
  --year-from 2020 --limit 12 --output /tmp/arm-literature.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole body multi contact force control" \
  --year-from 2020 --limit 12 --output /tmp/humanoid-literature.json
./.mamba-env/bin/python scripts/literature-query.py \
  "sim-to-real compliant contact force control robot" \
  --year-from 2020 --limit 12 --output /tmp/sim2real-literature.json
./.mamba-env/bin/python scripts/literature-query.py \
  "机械臂 接触 力控制 仿真" \
  --year-from 2020 --limit 12 --output /tmp/chinese-literature.json
```

The next evidence action is to obtain the selected publisher or university-
portal PDFs, record their SHA-256 values, and write structured notes. No
equation, baseline, or performance claim is promoted from this discovery pass.

## Focused venue and Chinese-term pass

- Date: 2026-08-29 (Asia/Shanghai)
- Tool: `scripts/literature-query.py`
- Public sources queried: OpenAlex and Crossref
- Evidence status: every result below is `metadata-only`; no PDF was used as
  experimental evidence

| Axis | Exact query and filter | Result | Candidate follow-up |
| --- | --- | --- | --- |
| Arm force learning | `force control contact-rich manipulation`, year >= 2022, venue `IEEE Robotics and Automation Letters` | 2 records; Crossref returned HTTP 429 | *Residual Learning From Demonstration: Adapting DMPs for Contact-Rich Manipulation* (RA-L 2022, DOI `10.1109/LRA.2022.3150024`) |
| Humanoid/contact dynamics | `humanoid whole body multi contact force control`, year >= 2022, venue `IEEE Transactions on Robotics` | 2 records; both public sources returned | *Optimization-Based Control for Dynamic Legged Robots* (T-RO 2023, DOI `10.1109/TRO.2023.3324580`); *Dynamic Complementarity Conditions and Whole-Body Trajectory Optimization for Humanoid Robot Locomotion* (T-RO 2022, DOI `10.1109/TRO.2022.3183785`) |
| Chinese terminology probe | `机械臂 接触 力控 导纳 阻抗`, year >= 2020, no venue filter | 10 records; low precision and unrelated records present | Repeat in CNKI/万方 through the university portal using title/keyword/abstract fields and the terms `导纳控制`, `阻抗控制`, `混合位置力控制` |

The focused pass confirms the source boundary: use public indexes to build a
candidate queue and DOI map, then verify venue and read the publisher or
authorized portal full text. The Chinese queue is intentionally not promoted
until the university portal supplies database identifiers and full text.

## Public metadata refresh (executed 2026-08-29)

A second three-axis pass queried OpenAlex and Crossref through
`scripts/literature-query.py`. The JSON outputs were transient files under
`/tmp/refresh-*-20260829.json`; no PDF was treated as obtained. Every result
below remains `metadata-only` until the DOI is opened at the publisher or
through the authorized school portal.

| Axis | Exact query | Selected candidates for portal verification |
| --- | --- | --- |
| Arm force/contact learning | `robot manipulator force control contact-rich learning` | *Unified Method for Task-Space Motion/Force/Impedance Control of Manipulator With Unknown Contact Reaction Strategy* (RA-L 2022, DOI `10.1109/LRA.2021.3139675`); *A review on reinforcement learning for contact-rich robotic manipulation tasks* (RCIM 2022, DOI `10.1016/j.rcim.2022.102517`); *Dynamic movement primitives in robotics: A tutorial survey* (IJRR 2023, DOI `10.1177/02783649231201196`) |
| Humanoid multi-contact | `humanoid whole-body compliant multi-contact control` | *Dynamic Complementarity Conditions and Whole-Body Trajectory Optimization for Humanoid Robot Locomotion* (T-RO 2022, DOI `10.1109/TRO.2022.3183785`); *ADHERENT: Learning Human-like Trajectory Generators for Whole-body Control of Humanoid Robots* (RA-L 2022, DOI `10.1109/LRA.2022.3141658`); *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* (RA-L 2024, DOI `10.1109/LRA.2024.3475052`) |
| Transfer and sensing | `sim-to-real force control contact manipulation robot` | *Real-Time Deformable-Contact-Aware Model Predictive Control for Force-Modulated Manipulation* (T-RO 2023, DOI `10.1109/TRO.2023.3286070`); *A soft thumb-sized vision-based sensor with accurate all-round force perception* (Nature Machine Intelligence 2022, DOI `10.1038/s42256-021-00439-3`); *Automatic Real-to-Sim-to-Real System through Iterative Interactions for Robust Robot Manipulation Policy Learning with Unseen Objects* (IROS 2025, DOI `10.1109/IROS60139.2025.11247488`) |

Reproduction commands:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator force control contact-rich learning" \
  --year-from 2022 --limit 12 --output /tmp/refresh-arm-20260829.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole-body compliant multi-contact control" \
  --year-from 2022 --limit 12 --output /tmp/refresh-humanoid-20260829.json
./.mamba-env/bin/python scripts/literature-query.py \
  "sim-to-real force control contact manipulation robot" \
  --year-from 2022 --limit 12 --output /tmp/refresh-transfer-20260829.json
```

The refresh improves candidate coverage but does not close the evidence gate:
the contact-manipulation survey and at least three Chinese CNKI/万方 full texts
still require the school portal. Search results with a public PDF URL are not
automatically promoted, because the PDF version, provenance, and hash must be
verified in `docs/literature/portal-intake.md`.

## Reproducible three-axis refresh (executed 2026-08-29)

The repository query tool was rerun from the project root. Each pass queried
OpenAlex and Crossref, used `--year-from 2020 --limit 12`, deduplicated by DOI,
and wrote transient JSON outside Git under `/tmp/codex-literature-20260829/`.
Both sources returned successfully and every record remains `metadata-only`.

| Axis | Exact query | Priority candidates for portal verification |
| --- | --- | --- |
| Arm contact force learning | `robot manipulator contact force control learning` | *Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots* (RA-L 2020, `10.1109/LRA.2020.3010739`); *Unified Method for Task-Space Motion/Force/Impedance Control of Manipulator With Unknown Contact Reaction Strategy* (RA-L 2022, `10.1109/LRA.2021.3139675`) |
| Humanoid multi-contact | `humanoid whole body multi contact force control` | *Dynamic Complementarity Conditions and Whole-Body Trajectory Optimization for Humanoid Robot Locomotion* (T-RO 2022, `10.1109/TRO.2022.3183785`); *Constraint-consistent task-oriented whole-body robot formulation* (IJRR 2022, `10.1177/02783649221120029`); *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* (RA-L 2024, `10.1109/LRA.2024.3475052`) |
| Sim-to-real and force modulation | `sim-to-real compliant contact force control robot` | *Real-Time Deformable-Contact-Aware Model Predictive Control for Force-Modulated Manipulation* (T-RO 2023, `10.1109/TRO.2023.3286070`); *Contact Force Control with Continuously Compliant Robotic Legs* (ICRA 2023, `10.1109/ICRA48891.2023.10160269`); *Forces for free: Vision-based contact force estimation with a compliant hand* (Science Robotics 2025, `10.1126/scirobotics.adq5046`) |

Reproduction commands:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator contact force control learning" --year-from 2020 \
  --limit 12 --output /tmp/codex-literature-20260829/arm.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole body multi contact force control" --year-from 2020 \
  --limit 12 --output /tmp/codex-literature-20260829/humanoid.json
./.mamba-env/bin/python scripts/literature-query.py \
  "sim-to-real compliant contact force control robot" --year-from 2020 \
  --limit 12 --output /tmp/codex-literature-20260829/transfer.json
```

These candidates are a retrieval queue only. Before they support a design
claim, use the university portal or an authorized open-access publisher copy,
record the DOI and SHA-256, and create a structured note with
`scripts/create-paper-note.py`. The Chinese axis still must be searched directly
in CNKI/万方 using title, keyword, and abstract fields.

## Public metadata probe (executed 2026-08-29, current session)

The following focused probe used the same repository query tool with
`--year-from 2020 --limit 10`. OpenAlex and Crossref both returned successfully;
all records remain `metadata-only`.

| Axis | Exact query | Representative candidates |
| --- | --- | --- |
| Arm contact force | `contact force control robotic manipulation` | *Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots* (RA-L 2020, DOI `10.1109/LRA.2020.3010739`); *A review on reinforcement learning for contact-rich robotic manipulation tasks* (RCIM 2022, DOI `10.1016/j.rcim.2022.102517`); *A survey of robot manipulation in contact* (RAS 2022, DOI `10.1016/j.robot.2022.104224`) |
| Humanoid multi-contact | `humanoid whole body multi contact force control` | *Dynamic Complementarity Conditions and Whole-Body Trajectory Optimization for Humanoid Robot Locomotion* (T-RO 2022, DOI `10.1109/TRO.2022.3183785`); *Constraint-consistent task-oriented whole-body robot formulation* (IJRR 2022, DOI `10.1177/02783649221120029`); *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* (RA-L 2024, DOI `10.1109/LRA.2024.3475052`) |
| Chinese terminology probe | `机械臂 导纳控制 力传感器` | Public ranking was low precision and included unrelated sensing papers; repeat in CNKI/万方 with title/keyword/abstract fields and the required terms `导纳控制`, `阻抗控制`, `混合位置力控制` |

Reproduction commands:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "contact force control robotic manipulation" --year-from 2020 --limit 10 \
  --output /tmp/contact-force-candidates.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole body multi contact force control" --year-from 2020 --limit 10 \
  --output /tmp/humanoid-force-candidates.json
./.mamba-env/bin/python scripts/literature-query.py \
  "机械臂 导纳控制 力传感器" --year-from 2020 --limit 10 \
  --output /tmp/chinese-admittance-candidates.json
```

This probe changes the candidate queue only. Formal evidence still requires the
publisher or authorized university-portal PDF, a local SHA-256, and a completed
structured note.
