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
