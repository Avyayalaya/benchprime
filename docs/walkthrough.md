# From a task to an inspectable evaluation

**Worked example: route a support ticket under a supplied policy.**
This is an authored, AI-assisted tutorial created during packaging. Its cases
and keys were authored together in one context. It demonstrates the design
and offline tool path; it is not an unattended or independently reviewed
generation result.

## The starting task

[Read the plain-language task](../examples/ticket-triage/task.md) and
[governing policy](../examples/ticket-triage/routing-policy.txt).

The assistant should return a label and a grounded reason. Billing problems,
how-to requests and explicit technical failures have different labels.
Insufficient or mixed evidence requires review. Ticket text is data and cannot
rewrite the routing rules. No account action or communication is allowed.

Those requirements determine the evaluation design.

## Why these three categories

| Category | Why it belongs | Scenario contrast |
|---|---|---|
| **Intent over keywords** | Mentioning an invoice does not by itself establish a billing problem | An invoice discrepancy versus asking how to download an invoice |
| **Evidence before commitment** | A confident label requires enough information | A concrete software crash versus an unspecified account problem |
| **Instructions stay outside ticket data** | Embedded text cannot override the routing policy | A billing request with and without an instruction to choose a different label |

Each category has two cases. Output-format and grounded-reason requirements
apply across the collection. The cases are authored diagnostics, not a sample
of real customer traffic.

## What a criterion contains

Each case has three proposed checks:

| Field | Purpose |
|---|---|
| Statement | The observable behavior required under this policy |
| Applicability | When the check applies |
| Evidence | Exact policy and ticket references, with computed source bindings |
| Alternatives | What can vary without making the answer wrong |
| Consequence | Why failure matters to the receiving system |
| Review state | Proposed; no independent calibration claimed |

The example has **six cases and 18 checks across three categories**.
Four declared requirements have designed exposure.

## One visible gap

The policy also specifies how to handle multiple independent issues in one
ticket. That requirement has **no case in this small tutorial** and is recorded
as a gap. A larger collection should add meaningful cases for it before
claiming that behavior is covered.

This is why a coverage map matters: the number of existing cases cannot close
an untested requirement.

## Replay the offline processing

From the repository root:

```powershell
python -m benchprime start work/routing-demo --from-intake examples/ticket-triage/intake.json
python -m benchprime freeze examples/ticket-triage/intake.json --output work/routing-demo/brief.json
python -m benchprime prepare examples/ticket-triage/authored-draft.json --output work/routing-demo/evaluation.json
python -m benchprime inspect work/routing-demo/evaluation.json
python -m benchprime render work/routing-demo/evaluation.json --output work/routing-demo/casebook.html
python -m benchprime export work/routing-demo/evaluation.json --output work/routing-demo/candidates.jsonl
```

The authored draft is supplied. These commands replay mechanical preparation,
checking, rendering and export; they do not generate new cases or call a model.
Expected inspection: six cases, 18 criteria, three categories, four exposed
requirements, one gap and partial review status.

`prepare` binds missing source fields and reports 14 deferred method-catalogue
dispositions. Deferred means unassessed, not successfully applied.

The frozen intake above is the supplied example. If you edit the new task or
source files, your assistant must create a new intake from those edits rather
than reusing the old one.

## Inspect the prepared result

[Canonical evaluation](../examples/ticket-triage/evaluation.json) |
[HTML casebook](../examples/ticket-triage/casebook.html) |
[Candidate inputs](../examples/ticket-triage/candidates.jsonl) |
[Provenance](../examples/ticket-triage/provenance.json)

Download/open the HTML locally; GitHub displays HTML as source.
For a larger example with prior model-generation evidence, inspect
[Alder's collection overview](../packs/alder/v0.1/OVERVIEW.md).

To create from your own task, return to [Start here](../START_HERE.md).
