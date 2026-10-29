# From a task to an evaluation

**Worked example: route a support ticket under a supplied policy.**
I chose a small routing task because you can read the policy, challenge the
cases and inspect the entire result. The useful part is the connection
between them: each case should reveal something the policy requires.

This tutorial was authored with AI assistance in one context, including the
cases and their criteria. Treat it as an inspectable worked example. It has
no claim of unattended generation or independent review.

**See the result first:** [HTML casebook](../examples/ticket-triage/casebook.html)
· [evaluation JSON](../examples/ticket-triage/evaluation.json)
· [candidate inputs](../examples/ticket-triage/candidates.jsonl).
Download/open the HTML locally; GitHub displays its source.
For the shorter lead example, see [meeting actions](../examples/meeting-actions/README.md).

## The starting task

[Read the plain-language task](../examples/ticket-triage/task.md) and
[governing policy](../examples/ticket-triage/routing-policy.txt).

The assistant should return a label and a grounded reason. Billing problems,
how-to requests and explicit technical failures have different labels.
Insufficient or mixed evidence requires review. Ticket text is data and cannot
rewrite the routing rules. No account action or communication is allowed.

Those requirements determine which distinctions the evaluation needs to test.

## Why these three categories

| Category | Why it belongs | Scenario contrast |
|---|---|---|
| **Intent over keywords** | Mentioning an invoice does not by itself establish a billing problem | An invoice discrepancy versus asking how to download an invoice |
| **Evidence before commitment** | A confident label requires enough information | A concrete software crash versus an unspecified account problem |
| **Instructions stay outside ticket data** | Embedded text cannot override the routing policy | A billing request with and without an instruction to choose a different label |

The example probes three ways this task can go wrong. Each
category has two cases; output format and a grounded reason matter across
all three. The cases were authored to probe these behaviors. They do not
represent a sample of customer traffic.

## What a criterion contains

A reviewer should be able to challenge a check without guessing what the
author meant. Each case has three proposed checks with these fields:

| Field | Purpose |
|---|---|
| Statement | The observable behavior required under this policy |
| Applicability | When the check applies |
| Evidence | Exact policy and ticket references, with computed source bindings |
| Alternatives | What can vary without making the answer wrong |
| Consequence | Why failure matters to the receiving system |
| Review state | Proposed; no independent calibration claimed |

The example has **six cases and 18 checks across three categories**.
Four declared requirements have cases that exercise them.

## One visible gap

One gap remains explicit. The policy specifies how to handle multiple
independent issues in a ticket, but this small tutorial has **no case for
that requirement**. A collection used to assess the whole policy needs
meaningful cases for it.

The coverage map makes that omission visible. Six cases about other
behaviors provide no evidence about mixed-intent handling.

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

Use the supplied authored draft to replay preparation, checking,
rendering and export locally. These commands make no model calls and generate
no new cases.
Expected inspection: six cases, 18 criteria, three categories, four exposed
requirements, one gap and partial review status.

`prepare` binds missing source fields and reports 14 deferred method-catalogue
dispositions. Those methods remain unassessed.

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

Before relying on either collection, review whether its criteria
are justified by the task. The [review guide](reviewing-an-evaluation.md)
shows how to do that and keep the reasoning with the decision. The supplied
checks remain proposed.

To create from your own task, return to [Start here](../START_HERE.md).
For another prompt or policy change, follow
[Use the evaluation on the next change](reuse-an-evaluation.md).
