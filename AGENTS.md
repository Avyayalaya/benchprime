# BenchPrime capability manifest

BenchPrime is a system for creating evaluations for user-defined purposes and
use cases. Separate the evaluation purpose, what is being evaluated, and the
creation/execution interface. The assistant-led route below is one packaged
implementation; it does not define the product's intended domain.

Status: developer preview. Read `RELEASE_STATUS.json` for distribution scope.
License: MIT; see `LICENSE`. It covers the original code, documentation,
assets and fictional examples in this distribution. Source permissions for
new tasks and separately licensed dependencies remain separate.

## Capabilities in this local distribution

| Capability | Input | Output | Entry point |
|---|---|---|---|
| Start an evaluation | New workspace path, optional task file/typed intake | task.md, source files and exact assistant kickoff; no generation | `python -m benchprime start` |
| Guided evaluation design | Typed task, policies and source material | Reviewable collection of categories, scenarios, cases and criteria | `workflows/generate.md` |
| First-session handoff | Plain-language task and permitted sources | Design checkpoint, then an approved assisted draft; optional manual context separation | `docs/first-session.md` |
| Freeze task and bind references | `schemas/task-intake.json` | Hashed brief and exact authority-tagged references | `python -m benchprime freeze` / `references` |
| Check evaluation definitions | `schemas/evaluation-design.json` | Structural/reference errors or explicit structural validity | `python -m benchprime validate` |
| Complete derived fields | Draft with chosen evidence pointers | Bound evidence/hashes and disclosed deferred methods | `python -m benchprime prepare` |
| Inspect and export | Valid collection-first pack | Counts; isolated candidate JSON/JSONL | `python -m benchprime inspect` / `export` |
| Render | Valid pack | Offline HTML casebook | `python -m benchprime render` |
| Review criteria and use results | Versioned task/sources, evaluation and permitted responses | Manual criterion-validity and decision record; no automated grading | `docs/reviewing-an-evaluation.md` |
| Reuse an evaluation | Accepted pack plus a changed prompt/model or task policy | Explicit fixed/revised artifacts and manual decision record; external execution remains separate | `docs/reuse-an-evaluation.md` |

Run from this directory with Python 3.10+. Core commands use only the standard
library. No provider credentials, network calls or target actions are needed.
For the user-facing first-use route, begin with `START_HERE.md`.
The generated kickoff asks for a collection design and a stop for approval
before cases/criteria. This is an instruction to the assistant, not a runtime
enforcement mechanism. Default provenance is author-assisted; record actual
context exposure before making any independence claim.

## Complete example

The lead authored meeting-actions collection is directly inspectable:

```powershell
python -m benchprime inspect examples/meeting-actions/evaluation.json
```

Expected fields: `cases: 6`, `criteria: 17`, `categories: 3`, `themes: 5`,
`scenario_groups: 3`, `requirements_exposed: 4`, `gaps: 1`,
`review_status: "partial"`, `target_executed: false`.
Unresolved conditional commitments remain a gap. Source notes and criteria
were authored in one context; human calibration remains unestablished.

For the larger model-assisted development example:

```powershell
python -m benchprime inspect packs/alder/v0.1/evaluation.json
```

Expected fields: `cases: 12`, `criteria: 133`, `categories: 5`, `themes: 9`,
`scenario_groups: 5`, `requirements_exposed: 10`, `gaps: 0`,
`review_status: "partial"`, `target_executed: false`.

The separately labelled ticket-triage walkthrough is authored tutorial content:
six cases, 18 proposed criteria, three categories and one deliberate coverage gap.
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
