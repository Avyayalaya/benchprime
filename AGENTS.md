# BenchPrime capability manifest

BenchPrime is a system for creating evaluations for user-defined purposes and
use cases. Separate the evaluation purpose, what is being evaluated, and the
creation/execution interface. The assistant-led route below is one packaged
implementation; it does not define the product's intended domain.

Status: developer preview. Read `RELEASE_STATUS.json` for distribution scope.
No reuse license has been selected; do not describe this release as licensed
open source.

## Capabilities in this local distribution

| Capability | Input | Output | Entry point |
|---|---|---|---|
| Start an evaluation | New workspace path, optional task file/typed intake | task.md, source files and exact assistant kickoff; no generation | `python -m benchprime start` |
| Guided evaluation design | Typed task, policies and source material | Reviewable collection of categories, scenarios, cases and criteria | `workflows/generate.md` |
| Freeze task and bind references | `schemas/task-intake.json` | Hashed brief and exact authority-tagged references | `python -m benchprime freeze` / `references` |
| Check evaluation definitions | `schemas/evaluation-design.json` | Structural/reference errors or explicit structural validity | `python -m benchprime validate` |
| Complete derived fields | Draft with chosen evidence pointers | Bound evidence/hashes and disclosed deferred methods | `python -m benchprime prepare` |
| Inspect and export | Valid collection-first pack | Counts; isolated candidate JSON/JSONL | `python -m benchprime inspect` / `export` |
| Render | Valid pack | Offline HTML casebook | `python -m benchprime render` |

Run from this directory with Python 3.10+. Core commands use only the standard
library. No provider credentials, network calls or target actions are needed.
For the user-facing first-use route, begin with `START_HERE.md`.

## Complete example

```powershell
python -m benchprime inspect packs/alder/v0.1/evaluation.json
```

Expected fields: `cases: 12`, `criteria: 133`, `categories: 5`, `themes: 9`,
`scenario_groups: 5`, `requirements_exposed: 10`, `gaps: 0`,
`review_status: "partial"`, `target_executed: false`.

The separately labelled ticket-triage walkthrough is authored tutorial content:
six cases,18proposed criteria, three categories and one deliberate coverage gap.
Do not present it as a fresh autonomous generation or an independently
calibrated benchmark.

## Boundaries

Structural validity does not certify semantic correctness, representative
coverage or target performance. Generation uses the operator's assistant;
this package has no provider-backed generation command. Operator-managed
context isolation differs from a runtime-enforced pipeline.

Keep original sources and case input intact. Never silently fix mismatched
evidence, upgrade review status, infer source rights or pass grading material
to a target. Preserve unknowns and review findings. Every output write uses a
new filename; bundled packs are immutable. See `docs/getting-started.md`.
