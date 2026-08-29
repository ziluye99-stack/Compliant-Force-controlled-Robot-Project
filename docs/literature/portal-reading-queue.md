# Portal Reading Queue

This queue is for the university library portal and is intentionally separate
from the public metadata search log. A row becomes project evidence only after
the final paper is found through the portal or an authorized publisher route,
the PDF is downloaded outside Git, and a structured note passes the SHA-256
check.

## Priority queue

| Priority | Research axis | Candidate or portal query | Formal source to verify | Status |
| --- | --- | --- | --- | --- |
| P0 | Contact-manipulation survey | *A survey of robot manipulation in contact* | Robotics and Autonomous Systems, 2022; DOI `10.1016/j.robot.2022.104224`; [publisher DOI](https://doi.org/10.1016/j.robot.2022.104224) | Legal arXiv preprint read; publisher/portal PDF still optional to verify |
| P0 | Arm force learning baseline | *Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controlled Robots* | IEEE RA-L, 2020; DOI `10.1109/LRA.2020.3010739`; [publisher DOI](https://doi.org/10.1109/LRA.2020.3010739) | Note already completed from public full text; portal copy optional |
| P0 | Humanoid whole-body/multi-contact | *Whole-Body Multi-Contact Motion Control for Humanoid Robots Based on Distributed Tactile Sensors* | IEEE RA-L, 2024; DOI `10.1109/LRA.2024.3475052`; [publisher DOI](https://doi.org/10.1109/LRA.2024.3475052) | Candidate; verify final version |
| P1 | Chinese admittance control | Search title/keyword/abstract: `机械臂 AND 导纳控制 AND 力传感器`; prefer a paper with force-tracking plots and a real-arm or MuJoCo/Gazebo experiment | CNKI or 万方 record, identifier and official PDF URL required | Not selected until portal search |
| P1 | Chinese impedance/hybrid control | Search title/keyword/abstract: `(阻抗控制 OR 混合位置力控制) AND 机械臂 AND 接触/装配`; prefer an explicit selection matrix or impedance equation | CNKI or 万方 record, identifier and official PDF URL required | Not selected until portal search |
| P1 | Chinese humanoid/multi-contact | Search title/keyword/abstract: `(人形机器人 OR 类人机器人) AND (全身控制 OR 多接触) AND 柔顺/力控`; require contact assumptions and stability/force metrics | CNKI or 万方 record, identifier and official PDF URL required | Not selected until portal search |
| P1 | Constrained admittance | *Admittance-Based Controller Design for Physical Human-Robot Interaction in the Constrained Task Space* | IEEE T-ASE, 2020; DOI `10.1109/TASE.2020.2983225`; [publisher DOI](https://doi.org/10.1109/TASE.2020.2983225) | Discovery candidate; verify final PDF and experimental details |
| P1 | Humanoid whole-body constraints | *Constraint-consistent task-oriented whole-body robot formulation* | IJRR, 2022; DOI `10.1177/02783649221120029`; [publisher DOI](https://doi.org/10.1177/02783649221120029) | Discovery candidate; verify final PDF and contact/balance assumptions |
| P1 | Sim-to-real transfer | *Crossing the Reality Gap: A Survey on Sim-to-Real Transferability of Robot Controllers in Reinforcement Learning* | IEEE Access, 2021; DOI `10.1109/ACCESS.2021.3126658`; [publisher DOI](https://doi.org/10.1109/ACCESS.2021.3126658) | Discovery candidate; verify final PDF before using taxonomy |

The public metadata probe also returned *Neural Network Adaptive Force Tracking
Admittance Control for Spinning Yarn Piecing Robot* (Journal of Mechanical
Engineering, 2023, DOI `10.3901/jme.2023.11.221`). It is a possible Chinese
admittance candidate, not accepted evidence: locate the CNKI/万方 record and
confirm the title, authors, article type, and full text before selecting it.

## Portal procedure

For each P0/P1 row:

1. Open the university portal and search by DOI where available; for Chinese
   rows search the three fields separately (title, keyword, abstract).
2. Confirm title, authors, venue, year, document type, and database identifier.
3. Download the final PDF to
   `/mnt/research-data/literature/pdfs/` using a short ASCII filename.
4. Run `sha256sum` and retain the stable URL, access date, identifier, and hash.
5. Give Codex only the local PDF path and bibliographic handoff fields; never
   provide the portal password, cookies, OTP, or exported session.

Example handoff:

```text
PDF: /mnt/research-data/literature/pdfs/cnki-admittance-2024.pdf
DOI/数据库标识: CNKI:<identifier> or 万方:<identifier>
正式出版链接: <portal or publisher URL>
门户来源: CNKI / 万方 / IEEE / Nature / Web of Science
下载日期: YYYY-MM-DD
SHA-256: <64 hexadecimal characters>
```

Codex then creates or fills one note under `docs/literature/notes/`, translates
the abstract and key method text, maps Chinese/English terminology, separates
strengths from weaknesses and assumptions, extracts baselines/metrics/failure
cases, and proposes the smallest falsifiable MuJoCo follow-up. A metadata-only
record remains a queue item and cannot justify a design or performance claim.

## Selection rules for the three Chinese papers

Select exactly one paper for each axis (admittance; impedance or hybrid
position-force; humanoid whole-body/multi-contact). Prefer peer-reviewed journal
or conference papers with a reproducible controller equation, stated sensor
rate/calibration, force or contact metrics, and an identifiable baseline. Keep
theses or application reports as supplementary context rather than silently
mixing them with primary evidence. Record why near-duplicates were rejected in
the dated search log.
