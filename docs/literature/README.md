# Literature Research Workflow

The literature process supports the project vision: find credible evidence,
understand the experiment, identify a real gap, and turn it into a testable
MuJoCo experiment. Every claim used in a design or paper should have a saved
source URL/DOI and a reading note.

SCI is a Web of Science indexing and selection system, not a full-text
database by itself. For every paper, distinguish the index or discovery record
from the publisher page and from the PDF actually read.

## Source map

| Use | Preferred sources | Notes |
| --- | --- | --- |
| Broad discovery and citation graph | Semantic Scholar, OpenAlex, Crossref | Metadata, citations, DOI deduplication |
| Latest methods and preprints | arXiv, authors' repositories | Filter by `cs.RO`, `cs.LG`, `eess.SY` where relevant |
| Robotics conferences | RSS, CoRL, ICRA, IROS, RA-L, IEEE Xplore | Verify the final publisher version and venue |
| High-impact science | Nature, Science, Science Robotics, Nature Machine Intelligence | Use the school portal for full text when access-controlled |
| Engineering and control | IEEE Transactions on Robotics, T-ASE, T-MECH, Automatica, IJRR | Prefer primary experimental papers and supplementary material |
| Chinese research | 中国知网 (CNKI), 万方, 学校图书馆 discovery portal | Log in through the school portal; do not bypass paywalls or scrape access controls |
| Code and artifacts | GitHub, official project pages, Papers with Code | Record commit/tag and license; code is not evidence of published results |

Codex's `literature-search` skill uses Semantic Scholar and arXiv as its
default discovery engines, then supplements with OpenAlex/Crossref-compatible
metadata, Exa/Tavily-style web search, AMiner for Chinese authors and venues,
and citation chaining. It does not automatically inherit the school's CNKI
session. When a paper is behind the school portal, use the logged-in browser to
open and download it, then provide the PDF or stable URL to Codex.

The resulting evidence hierarchy is:

1. Publisher or official proceedings full text (IEEE Xplore, ScienceDirect,
   Springer, Wiley, Nature, Science, RSS/CoRL/ICRA/IROS proceedings).
2. Authorized university-portal full text (including Web of Science/SCI,
   CNKI, and 万方 links reached from the library app).
3. Author manuscript or institutional repository with clear provenance.
4. arXiv and metadata indexes for discovery, version comparison, and citation
   chaining only.
5. GitHub or Papers with Code for implementation clues and licenses, never as
   evidence for a published performance claim.

The machine-readable version of this policy is
`configs/literature_sources.yaml`. Validate it before a new search session:

```bash
./.mamba-env/bin/python scripts/check-literature-sources.py
```

The policy keeps SCI/Web of Science, top robotics venues, Nature/Science, and
CNKI/万方 in the primary evidence tier while keeping public indexes in the
discovery tier.

## Source priority for this project

Use the following order for force control, contact-rich manipulation, and
humanoid whole-body questions:

1. **Primary robotics venues:** IEEE Transactions on Robotics, IEEE Robotics
   and Automation Letters, IJRR, Science Robotics, RSS, CoRL, ICRA, and IROS.
   Prefer the final peer-reviewed version and supplementary material.
2. **High-impact multidisciplinary venues:** Nature, Nature Machine
   Intelligence, Science, and Science Robotics. Inspect the actual task and
   hardware evidence rather than relying on the headline result.
3. **Chinese literature:** 中国知网 (CNKI), 万方, and the university discovery
   portal. Search Chinese terminology and retain the Chinese title, authors,
   identifier, venue, and an English terminology mapping.
4. **Discovery and cross-check sources:** OpenAlex, Crossref, Semantic Scholar,
   arXiv, and official author/project pages. These verify metadata and citation
   links; they do not replace the publisher or portal record.

Record the discovery source and full-text source separately. For example, a
paper found through OpenAlex but read from IEEE Xplore or CNKI must list both
sources in the search log and paper note.

## School-portal full-text procedure

When the university portal is the authorized route to SCI, Nature, IEEE, or
CNKI content:

1. Open the portal app or its library link and complete login yourself. Codex
   must not receive or store the portal password, cookies, or one-time codes.
2. Search by DOI first, then exact title and author. Confirm venue, year, and
   article type before downloading.
3. Download the publisher PDF and relevant supplementary files to
   `/mnt/research-data/literature/pdfs/`, outside the Git repository.
4. Record the stable URL, access date, file name, and SHA-256 in the paper note.
   If only metadata or an abstract is available, label it `metadata-only` and
   do not use it as experimental evidence.
5. Provide Codex the local PDF path or stable URL for translation, technical
   digest, strengths/limitations analysis, and experiment-design extraction.

If the portal opens a publisher site in a separate tab, keep the DOI/title and
access date in the search log before downloading. If download is unavailable,
export only what the portal permits and mark the record `metadata-only`; do not
infer equations, baselines, or experimental results from an abstract.

For a restricted page that cannot be downloaded, keep its bibliographic record
and provide the PDF through the authorized portal. Do not bypass access
controls or use a copy with unclear provenance.

## Query strategy

Search in both English and Chinese. Start broad, then add the embodiment,
contact mode, sensor, controller, and metric:

```text
"force control" robotic manipulation contact stability
"sim-to-real" compliant manipulation force torque sensor
具身智能 机械臂 力控 接触 操作
人形机器人 全身柔顺控制 接触 学习
```

For each query, record date, source, filters, and the reason a paper was kept or
discarded. Use citation chains from the strongest papers to find predecessors,
concurrent work, and follow-ups.

## Access and provenance rules

- Use the school portal for subscriptions and CNKI access; never request or
  store the user's portal password or session cookies in the repository.
- Save DOI, publisher URL, preprint URL, access date, venue, year, and PDF hash
  when a full text is downloaded.
- Deduplicate by DOI first, then normalized title and author/year.
- Separate peer-reviewed papers, preprints, theses, benchmarks, and blog posts.
- Keep PDFs and exports outside Git, preferably on `/mnt/research-data`.
- Keep the abstract translation and technical conclusions in a committed note,
  but keep the full PDF, browser export, and raw annotations on the research
  drive.

## Outputs

Each serious reading produces a note from `paper-note-template.md`. A survey
also maintains a table of methods, sensors, tasks, metrics, baselines,
simulators, real-robot evidence, and limitations. A proposed project must cite
the gap it addresses and identify the minimum experiment that could falsify it.

The handoff from literature to engineering is explicit: the note's “follow-up
experiment in MuJoCo” becomes an experiment record, its interfaces become a
config and test, and its reported metrics become an evaluation script. Only
after that chain exists should a new model, mechanical change, or hardware
trial be proposed.

Discovery runs are recorded as dated `search-log-YYYY-MM-DD.md` files. The
current seed search is `search-log-2026-08-29.md`; it contains candidate DOIs
only, so it must not be cited as a completed review.

## Reproducible public-metadata query

For a new discovery session, run the repository tool with an English or
Chinese query. It queries OpenAlex and Crossref, deduplicates by DOI (then
normalized title/year), records source errors, and marks every result
`metadata-only`:

```bash
./.mamba-env/bin/python scripts/literature-query.py \
  "robot manipulator contact force control" \
  --year-from 2020 --limit 20 \
  --output /tmp/force-control-discovery.json
```

Use `--venue` for a narrow pass, for example `--venue "Robotics and
Automation Letters"`. Copy the query, date, sources, and selected DOI records
into a dated search log. This tool does not query CNKI or Web of Science
accounts and does not download restricted PDFs; use the school portal for
those steps and record the authorized full-text route in the paper note.

Before using notes to justify a new experiment, check the structured fields and
the evidence boundary:

```bash
./.mamba-env/bin/python scripts/check-paper-notes.py
./.mamba-env/bin/python scripts/check-paper-notes.py \
  --require-full-text --verify-files
```

The second command is the literature stage gate. It requires a non-empty
technical note, a non-`metadata-only` evidence status, and a matching SHA-256
for each referenced PDF. PDF files remain outside Git.

To start a note after an authorized PDF has been downloaded, use the helper to
record its hash before asking Codex to fill the analytical sections:

```bash
./.mamba-env/bin/python scripts/create-paper-note.py \
  --short-title contact-survey \
  --title "Exact paper title" \
  --authors "Author One; Author Two" \
  --venue-year "Journal, 2022" \
  --discovery-source "OpenAlex; CNKI" \
  --full-text-route "school portal -> CNKI" \
  --pdf /mnt/research-data/literature/pdfs/contact-survey.pdf \
  --output docs/literature/notes/contact-survey.md
```

The helper refuses missing/non-PDF inputs and refuses to overwrite an existing
note. It does not access the portal or store credentials.
