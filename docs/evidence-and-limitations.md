# Evidence and limitations

## Product scope and the supplied implementation

BenchPrime creates evaluations around a chosen purpose and use case.
Its definition is independent of the subject being evaluated or the interface
used to create the evaluation.

This repository currently supplies an assistant-led workflow and local Python
tools, with English text formats and examples. Other data formats, runners
and judging systems need their own support and validation. Broad product
scope is not a claim that every execution adapter or domain has been validated.

## What is included

This candidate extracts existing source-authority, design-validation,
collection and rendering components into portable Python modules. The core
CLI needs the standard library only. The supported starting point is a full
repository checkout. A Python wheel alone does not include the complete
workflow, schema and example library.

Generation uses the operator's AI assistant. No SDK, model credentials,
provider authorization, autonomous generation loop or target runner is
included. Optional Office renderer dependencies are declared separately.

## Alder development evidence

The example contains 12 candidate cases, 133 criteria, five categories,
nine themes and five scenario groups. All ten declared requirements have
designed exposure.

Generation needed operator-guided engineering and revisions. One key received
an explicit review-guided model repair. After model review, an AI operator
corrected five criteria, six comparison descriptions and two titles. The
corrected criteria remain proposed. All 35 illustrative controls were
excluded from the final example; they are not calibrated reference answers.
No target was run.

Portable extraction changes module/catalogue names, provenance metadata
bindings and the pack ID. Candidate input objects and criterion records are
unchanged. The example's [provenance](../packs/alder/v0.1/provenance.json)
identifies the upstream content fingerprint and retained limitations.

The example is fictional and development-exposed. It is useful for inspection
and regression rehearsal, not an unseen holdout or representative sample of
customer tasks. Structural checks do not establish criterion correctness.

## Authored ticket-triage walkthrough

The second example was authored during repository packaging to show a different
task and a complete input/design/output trail. It has six diagnostics,
18proposed checks, three categories and an explicit mixed-intent coverage gap.
Cases and keys were authored together in one assistant context. There is no
claim of blind generation, independent review, target performance or a new
daily live experiment.

Its supplied draft makes offline preparation/render/export replayable.
Replaying it does not create a new benchmark or demonstrate autonomous
generation. The user's own-task path still depends on their assistant and
appropriate review.

## External research

The method catalogue records public benchmark references and original
mechanism summaries. It imports no third-party benchmark dataset, grading
formula or domain authority. Reading code or a dataset card does not grant
rights to redistribute its underlying data.

There is no completed matched comparison establishing superiority over
ordinary prompting, DeepEval, Ragas or Giskard. Model/harness portability is
intended at the method level; performance across providers is unproven.

## Release boundary

This is a public developer preview. No reuse license has been selected, so
public visibility should not be treated as an open-source license grant.
No credentials, private run ledgers, raw provider sessions or external-action
permission are included.

The original example intakes retain their historical private-trial wording.
They are published for inspection as development records; they do not authorize
new model spending, target execution or transfers of private customer data.
