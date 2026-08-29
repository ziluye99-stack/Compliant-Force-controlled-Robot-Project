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

## Focused second pass

A second public-metadata pass was run on the same date to improve coverage of
learning-based compliant manipulation and humanoid contact control:

| Exact query | Sources | Selected candidates for portal verification |
| --- | --- | --- |
| `robot force control contact-rich manipulation reinforcement learning` | OpenAlex, Crossref | *Learning contact-rich whole-body manipulation with example-guided reinforcement learning* (Science Robotics, 2025, DOI `10.1126/scirobotics.ads6790`); *Learning Variable Impedance Control via Inverse Reinforcement Learning for Force-Related Tasks* (IEEE RA-L, 2021, DOI `10.1109/LRA.2021.3061374`); *Stability-Guaranteed Reinforcement Learning for Contact-Rich Manipulation* (IEEE RA-L, 2021, DOI `10.1109/LRA.2020.3028529`); *A Contact-Safe Reinforcement Learning Framework for Contact-Rich Robot Manipulation* (IROS, 2022, DOI `10.1109/iros47612.2022.9981185`); *Adaptive Contact-Rich Manipulation Through Few-Shot Imitation Learning With Force-Torque Feedback and Pre-Trained Object Representations* (IEEE RA-L, 2025, DOI `10.1109/LRA.2024.3497713`) |
| `humanoid whole-body force control multi-contact tactile` | OpenAlex, Crossref | *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* (IEEE RA-L, 2024, DOI `10.1109/LRA.2024.3475052`); *Multi-Contact Whole-Body Force Control for Position-Controlled Robots* (IEEE RA-L, 2024, DOI `10.1109/LRA.2024.3396094`); *Whole-Body Control of Humanoid Robot in 3D Multi-Contact under Contact Wrench Constraints Including Joint Load Reduction with Self-Collision and Internal Wrench Distribution* (IROS, 2019, DOI `10.1109/iros40897.2019.8967555`) |
| `robotic assembly force control admittance impedance sim-to-real` | OpenAlex, Crossref | *Variable Compliance Control for Robotic Peg-in-Hole Assembly: A Deep-Reinforcement-Learning Approach* (Applied Sciences, 2020, DOI `10.3390/app10196923`); *A review on reinforcement learning for contact-rich robotic manipulation tasks* (Robotics and Computer-Integrated Manufacturing, 2022, DOI `10.1016/j.rcim.2022.102517`); *Variable impedance control on contact-rich manipulation of a collaborative industrial mobile manipulator: An imitation learning approach* (Robotics and Computer-Integrated Manufacturing, 2024, DOI `10.1016/j.rcim.2024.102896`) |

The transient JSON outputs for this pass were `/tmp/lit-arm-contact-learning-20260830.json`,
`/tmp/lit-humanoid-force-20260830.json`, and
`/tmp/lit-assembly-transfer-20260830.json`. They are reproducibility aids for
the query session only and are not project evidence. All selected records remain
`metadata-only` until the final version is verified and read from a publisher,
authorized university portal, or clearly attributable open-access full text.

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

## Focused refresh: 2026-08-30 afternoon

The same reproducible tool was run with four narrower queries (15 records per
query, year >= 2020). The tool queried OpenAlex and Crossref only; this pass is
still discovery metadata and does not replace Web of Science/SCI, publisher,
or CNKI/万方 verification.

| Query axis | Candidate worth portal verification | Venue/year and DOI | Why retain |
| --- | --- | --- | --- |
| Arm force/contact learning | *Fine Robotic Manipulation Without Force/Torque Sensor* | IEEE RA-L, 2024; `10.1109/LRA.2023.3341770` | Tests whether contact behavior can be inferred without a wrist F/T sensor; useful sensor-ablation baseline |
| Arm force/contact learning | *Multifingered Robot Hand Compliant Manipulation Based on Vision-Based Demonstration and Adaptive Force Control* | IEEE T-NNLS, 2022; `10.1109/TNNLS.2022.3184258` | Connects demonstration, visual sensing, and adaptive force control |
| Sim-to-real | *Crossing the Reality Gap: A Survey on Sim-to-Real Transferability of Robot Controllers in Reinforcement Learning* | IEEE Access, 2021; `10.1109/ACCESS.2021.3126658` | Candidate taxonomy for calibration, randomization, and transfer failure analysis |
| Humanoid multi-contact | *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* | IEEE RA-L, 2024; `10.1109/LRA.2024.3475052` | Directly matches the humanoid/tactile branch and contact switching interface |
| Humanoid multi-contact | *Multi-Contact Whole-Body Force Control for Position-Controlled Robots* | IEEE RA-L, 2024; `10.1109/LRA.2024.3396094` | Relevant to position-controlled hardware and wrench feasibility constraints |
| Tactile sensing | *A soft thumb-sized vision-based sensor with accurate all-round force perception* | Nature Machine Intelligence, 2022; `10.1038/s42256-021-00439-3` | Candidate sensor calibration and force-perception reference |
| Assembly transfer | *A review on reinforcement learning for contact-rich robotic manipulation tasks* | RCIM, 2022; `10.1016/j.rcim.2022.102517` | Organizes contact-rich task, reward, simulator, and sim-to-real choices |

The Chinese query `机械臂 阻抗控制 混合位置力控制 接触 装配` returned mostly
low-precision engineering records. It remains a terminology probe only. The
Chinese evidence gate is unchanged: search CNKI/万方 through the university
portal, select one admittance, one impedance/hybrid position-force, and one
humanoid multi-contact paper, then download and hash the authorized PDFs.

## Chinese-axis probe for the portal handoff

To prepare the next portal session, the repository query tool was run again on
2026-08-30 with 15 records per axis and year >= 2020. It queried OpenAlex and
Crossref only; transient outputs were `/tmp/lit-cn-admittance-20260830.json`,
`/tmp/lit-cn-impedance-20260830.json`, and
`/tmp/lit-cn-humanoid-20260830.json`.

| Axis | Exact public query | Result | Decision |
| --- | --- | --- | --- |
| Admittance | `机械臂 导纳控制 力传感器` | 15 records; most were unrelated sensing or manufacturing papers; one force-tracking admittance candidate was retained | Use CNKI/万方 title/keyword/abstract search; verify the candidate only after the portal record is found |
| Impedance/hybrid position-force | `机械臂 阻抗控制 混合位置力 接触 装配` | 15 records; low precision, with unrelated mechanical-engineering reviews | Do not select a paper from this probe; search the portal with separate title/keyword/abstract fields and `(阻抗控制 OR 混合位置力控制)` |
| Humanoid multi-contact | `人形机器人 全身控制 多接触 柔顺 力控` | 15 records; public ranking mixed unrelated engineering and optical papers; one admittance candidate recurred | Search the portal directly and require humanoid/multi-contact assumptions plus force or stability metrics |

This probe is discovery metadata only. It does not establish a method,
equation, baseline, or performance claim. The three accepted papers must still
be selected through the university portal, downloaded outside Git, hashed, and
read into structured notes on the `codex/chinese-force-control-notes` branch.

## Focused public refresh: three project axes

On 2026-08-30, the repository discovery tool was run with three narrower
queries to prepare the next portal session. OpenAlex and Crossref were queried
in parallel; results were deduplicated by DOI and remain `metadata-only`.

| Axis | Exact query | Candidates retained for official-version verification |
| --- | --- | --- |
| Arm contact force control | `robot manipulator contact force control compliant manipulation` | *Unified Method for Task-Space Motion/Force/Impedance Control of Manipulator With Unknown Contact Reaction Strategy* (IEEE RA-L, 2022, DOI `10.1109/LRA.2021.3139675`); *Real-Time Deformable-Contact-Aware Model Predictive Control for Force-Modulated Manipulation* (IEEE T-RO, 2023, DOI `10.1109/TRO.2023.3286070`) |
| Admittance / hybrid control | `admittance impedance hybrid position force control robot assembly` | *Admittance-Based Controller Design for Physical Human–Robot Interaction in the Constrained Task Space* (IEEE T-ASE, 2020, DOI `10.1109/TASE.2020.2983225`); *Force Sensorless Admittance Control With Neural Learning for Robots With Actuator Saturation* (IEEE T-IE, 2019, DOI `10.1109/TIE.2019.2912781`) |
| Humanoid whole-body / multi-contact | `humanoid whole body multi contact force control` | *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* (IEEE RA-L, 2024, DOI `10.1109/LRA.2024.3475052`); *Multi-Contact Whole-Body Force Control for Position-Controlled Robots* (IEEE RA-L, 2024, DOI `10.1109/LRA.2024.3396094`); *Constraint-consistent task-oriented whole-body robot formulation* (IJRR, 2022, DOI `10.1177/02783649221120029`) |

The exact transient outputs were `/tmp/discovery-contact-force-20260830.json`,
`/tmp/discovery-admittance-20260830.json`, and
`/tmp/discovery-humanoid-force-20260830.json`. They are not copied into Git
and are reproducibility aids only. Before any paper is used for a design or
performance statement, verify its final publisher or proceedings version in
the school portal, record the authorized URL and access date, download the PDF
to `/mnt/research-data/literature/pdfs/`, compute its SHA-256, and create a
structured note.

Reproduction commands:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator contact force control compliant manipulation" \
  --year-from 2020 --limit 20 \
  --output /tmp/discovery-contact-force-20260830.json
./.mamba-env/bin/python scripts/literature-query.py \
  "admittance impedance hybrid position force control robot assembly" \
  --year-from 2018 --limit 20 \
  --output /tmp/discovery-admittance-20260830.json
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole body multi contact force control" \
  --year-from 2018 --limit 20 \
  --output /tmp/discovery-humanoid-force-20260830.json
```

## Public-source adapter verification

The repository query tool was extended and verified on 2026-08-30. The
default source set is now OpenAlex, Crossref, Semantic Scholar, and arXiv; the
new run below used all four sources and retained the same `metadata-only`
boundary:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "humanoid whole-body multi-contact force control" \
  --year-from 2022 --limit 5 --timeout 10 \
  --output /tmp/lit-public-sources-20260830.json
```

OpenAlex and Crossref returned records. Semantic Scholar returned HTTP 429 and
arXiv timed out within the 10-second test budget; both failures were preserved
under `source_errors` while the run still returned five deduplicated records.
The retained records included *Dynamic Complementarity Conditions and
Whole-Body Trajectory Optimization for Humanoid Robot Locomotion* (IEEE T-RO,
2022), *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on
Distributed Tactile Sensors* (IEEE RA-L, 2024), and *Multi-Contact Whole-Body
Force Control for Position-Controlled Robots* (IEEE RA-L, 2024).

This verifies source isolation, not paper validity. Semantic Scholar/arXiv
availability can vary with rate limits and network latency. WoS/SCI, CNKI/万方,
and publisher claims still require portal or official-version verification and
an SHA-256-tracked PDF before entering the literature evidence gate.
