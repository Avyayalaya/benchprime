# Current capabilities and evidence

## Product scope and the supplied implementation

Choose the job you want to evaluate, what you need to learn and how you
will use the result. The method accommodates different purposes and use
cases; each needs explicit requirements and an appropriate execution setup.

The current package provides an assistant-led creation workflow and local
Python tools for English text and JSON. Other formats, runners and judging
systems need their own support and validation. Coverage across domains
and execution environments remains unproven.

## What is included

The source-reference, validation, collection and rendering components run
as portable Python modules. Start from a full checkout so your
assistant can read the workflow, schemas and examples. The core CLI uses
only the standard library; a wheel alone omits part of that material.

Your assistant does the generation using its own model runtime. This repo
does not supply an SDK, model credentials, provider authorization, autonomous
generation loop or target runner. Optional Office-rendering dependencies
are declared separately.

## Alder development evidence

Alder provides a larger collection to inspect: 12 cases,
133 criteria, five categories, nine themes and five scenario groups.
Each of its ten declared requirements has designed case coverage.

The generation needed operator-guided engineering and revisions. One key received
an explicit review-guided model repair. After model review, an AI operator
corrected five criteria, six comparison descriptions and two titles. The
corrected criteria remain proposed. All 35 illustrative controls were
excluded from the final example; they are not calibrated reference answers.
No target was run.

Portable extraction changes module/catalogue names, provenance metadata
bindings and the pack ID. Candidate input objects and criterion records are
unchanged. The example's [provenance](../packs/alder/v0.1/provenance.json)
identifies the upstream content fingerprint and retained limitations.

Use this fictional, development-exposed material for inspection and
regression rehearsal. It is unsuitable as an unseen holdout and cannot
establish performance on representative customer tasks. The structural
checks leave criterion correctness for review.

## Authored ticket-triage walkthrough

The ticket-routing tutorial shows a different task with a complete
input/design/output trail: six diagnostics, 18 proposed checks,
three categories and an explicit mixed-intent coverage gap.
Cases and keys were authored together in one assistant context. There is no
claim of blind generation, independent review, target performance or a new
daily live experiment.

You can replay preparation, rendering and export from the supplied draft.
That exercises the local tools without generating a new evaluation.
Creating from your own task still needs your assistant and appropriate review.

## Authored meeting-actions example

The lead example turns fictional meeting notes into explicitly accepted
future actions. It has six cases, 17 proposed checks, three categories,
five themes and three controlled families. Four declared requirements have
case exposure; unresolved conditional commitments remain an explicit gap.

The cases and criteria were authored together in one AI context. Tests cover
structural replay, exact source/policy preservation, candidate isolation and
specific source-driven contrasts. They do not establish independent semantic
calibration, target performance or customer usefulness.

The README screenshot comes from the actual casebook. The illustrative
responses are authored examples; no target was executed. A new task's rules
must establish its own definition of a commitment and acceptable output.

## Assisted first-session rehearsal

One internal native Copilot rehearsal followed the generated kickoff, stopped
at the design checkpoint, then continued after explicit approval to a pack,
casebook, candidate-only export and review summary. The local preparation,
validation, inspection, rendering and export commands completed.

The same retained context authored and reviewed that rehearsal. It remains
assisted/partial; the exercise does not establish independent criteria,
human usability or reliable generation across assistants. No target was run.
It exposed a Markdown display gap: string observations appeared in exact
inputs but were absent from the dedicated Source notes section. HTML and
Markdown now share that source-display logic, with regression coverage.

The [first-session guide](first-session.md) states the supported assisted
path and the additional work required for operator-managed context separation.

## External research

The method catalogue connects public benchmark references to original
summaries of the relevant mechanisms. The package imports no third-party
benchmark dataset, grading formula or domain authority. A dataset card or
code license alone does not grant rights to redistribute the underlying data.

A matched comparison against ordinary prompting, DeepEval, Ragas or
Giskard remains unrun; superiority is unproven. Independent practitioner
value, human calibration and consistent generation quality across
providers also remain unestablished.

## Release boundary

This developer preview is covered by the [MIT license](../LICENSE).
The grant covers this repository's original code, documentation, assets
and fictional examples. Separately licensed dependencies and external
benchmark datasets retain their own terms. The package
excludes credentials, private run ledgers and raw provider sessions, and
confers no permission for external actions.

The original example intakes and provenance retain historical private-trial
wording, including pending-licensing and private-candidate fields. Those
records describe their development state; the root LICENSE governs the
current distribution. Preserving them keeps the original inputs and their
evidence bindings intact.

MIT does not supply permission to process new customer or employer data,
authorize model spending or execute external actions. Establish those
permissions separately for each task.
