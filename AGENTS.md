# BenchPrime: agent entry contract

Use BenchPrime to turn a user's task, rules and permitted sources into a
reviewable evaluation definition. This distribution supports English text/JSON
with a file-capable assistant and Python 3.10+. Run local commands from this
repository root. They use the standard library and make no provider calls.

**First choose the operation:** inspect an existing pack, start a new design,
or revise an accepted evaluation. A task workspace is scaffolding; creating it
does not generate cases or approve their use.

## Required inputs and default mode

Recover the evaluation purpose, subject/job, expected input/output, governing
rules and permitted source material. Keep facts, policies and preferences
separate. Ask about missing information only when it changes validity,
essential scope or permission. Declare unresolved rights/authority explicitly.

**Default: author-assisted in the current conversation.** Interpret, challenge,
write and review within that mode, recording actual exposure. Separate-context
work is optional and requires deliberately controlled handoffs. A new turn
does not establish independence.

## Execute this path

Use one new workspace for the task; replace `work/my-eval` below with its path.

| Stage | Action | Result / stop condition |
|---|---|---|
| Start | `python -m benchprime start work/my-eval` | `task.md`, `sources/`, `KICKOFF.md`; `generation_started: false` |
| Interpret and design | Read the task/sources and follow the selected mode in `workflows/generate.md` | Proposed `collection-design.md`, source authority, rights, distinctions and gaps |
| Approval | Present the design for review | **STOP.** No cases or criteria until the user accepts the scope. The assistant owns this pause; Python does not enforce it. |
| Create | Author the current intake, stage records and draft under the approved scope | Proposed cases/criteria with source evidence and acceptable alternatives; preserve actual assistance |
| Prepare | `python -m benchprime prepare work/my-eval/draft.json --output work/my-eval/evaluation.json` | Binds permitted derived fields and validates; never repairs semantic meaning |
| Check | `python -m benchprime validate work/my-eval/evaluation.json` then `inspect` with the same path | Structural validity and counts; semantic quality and target performance remain separate |
| Deliver | `render` and `export`, each with the evaluation path and a new `--output` path | Local casebook, isolated candidate inputs, review summary and unresolved gaps |

Use `freeze` and `references` for the current typed intake before authoring
source-bound stage records. The [full workflow](workflows/generate.md) defines
the formats and reasoning at each stage. The [human guide](START_HERE.md)
contains both handoff messages and the approval questions.

With `start --from-intake`, the workspace retains byte-exact
`imported-intake.json`. Use it to recover original identity, source provenance
and input shape. Keep it unchanged; task edits require a new current intake.
With `--task`, the starter copies the task file; add its source files explicitly.

**Completion:** return artifact paths, actual command outcomes, assistance
mode, proposed/accepted review status and remaining gaps. Only the candidate
record's `input` belongs in a separately approved target request. Do not send
its tracking ID, criteria, sibling cases or reviewer context.

**Recovery:** preserve failed drafts and source versions. For an unprepared
pack, use `prepare` on a new output path and then validate it. Repair genuine
field errors in a new draft version; never delete legitimate pack fields merely
to fit another document type. Existing outputs are immutable: retry using
new versioned filenames. Stop on unresolved source rights or governing conflicts.

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
