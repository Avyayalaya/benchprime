# Alder project-update evaluations

**12 cases / 133 criteria / five categories / nine themes.**
The task is a source-grounded project update for an operations decision.

[HTML casebook](delivery/read/CASEBOOK.html) |
[Excel workbook](delivery/read/EVALUATION_DESIGN.xlsx) |
[Word overview](delivery/read/EXECUTIVE_DESIGN_BRIEF.docx) |
[Canonical JSON](evaluation.json)

The collection covers reporting cutoffs, decision authority, readiness
conditions, evidence/measurement fidelity and useful communication.
All ten declared requirements have designed exposure.

GitHub displays HTML as source. Download the repository or the HTML file and
open it locally for the interactive collection; no server is required.

This is fictional, development-exposed, operator-assisted material.
Five corrected criteria remain proposed; review status is partial.
There is no independent human calibration or target-performance result.
See [provenance](provenance.json) and the repository's evidence documentation.

From the repository root:

```powershell
python -m benchprime inspect packs/alder/v0.1/evaluation.json
python -m benchprime export packs/alder/v0.1/evaluation.json --output work/alder-inputs.jsonl
```

Candidate-only records are also in `delivery/run/CANDIDATE_INPUTS.jsonl`.
Only the `input` field belongs in the target's context. Keep evaluator material
separate and do not treat fictional requests as permission for real actions.

This original fictional pack is covered by the repository's
[MIT license](../../../LICENSE). The intake and provenance retain their
historical private-development wording; those records do not describe the
current distribution license. Preserve the original records and check new
source permissions when adapting the pack.
