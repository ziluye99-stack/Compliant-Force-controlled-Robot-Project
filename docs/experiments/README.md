# Experiment Records

Create one Markdown record per experiment family. Read
`docs/PROJECT_VISION.md` first, then state the question, hypothesis, independent
variables, controlled variables, safety constraints, success metrics, baseline,
ablations, and artifact run IDs. Link to committed configuration files and
literature notes instead of duplicating parameters.

An experiment record should identify the smallest MuJoCo test that could falsify
the hypothesis. Promote it to hardware only after the safety gate in
`docs/workflow.md` is complete.
