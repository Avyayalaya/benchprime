# Review an evaluation before relying on its results

Use this guide when an evaluation will inform an output review, a model or
prompt comparison, or another workflow decision. Start with the task, its
permitted sources and the proposed evaluation. Obtain any target responses
through a separately agreed process; this guide does not run a target.

The outcome is a review record: which criteria are justified, what the
responses show, what remains unsettled and what action follows. The local
tools check evaluation files. People still need to review their meaning.

## 1. Agree on the decision and preserve the original requirements

Name the decision and who can make it. Examples include accepting an output,
revising a prompt, or adding a check before the next workflow change.
State the scope and important behaviors the collection does not cover.

Keep the task instructions, source versions, evaluation version and output
versions together. For existing outputs, use the requirements that actually
applied when they were produced. A newly desired standard needs a new task
version and matching outputs; it cannot establish a failure in an old output.
Do not infer permission to process material from its public availability.

## 2. Review the criteria before judging responses

For each criterion, ask:

- Which target-visible rule or fact supports it?
- Is it mandatory, a preference, or a diagnostic observation?
- When does it apply, and can that condition be established?
- Could a competent alternative satisfy the task and fail this check?

Record the criterion as **accepted**, **rejected** or **unresolved** in your
review notes. These are assessments of the check itself, separate from the
response judgment. A frozen criterion is a versioned proposal; freezing it
does not make its interpretation correct.

Correct or remove a demonstrably unsupported check in a new evaluation
version, retaining the original and the reason. Leave uncertain authority
or interpretation unresolved. Do not grade a response against a rejected
or unresolved check, and do not count that check as passed or not applicable.
`not_applicable` belongs to a valid conditional check whose condition is
known not to hold.

## Worked example: the check is too strict

This is an authored fictional illustration, including the proposed bad check
and response. It is not a recorded generator run or a calibrated test case.

### Task supplied to the respondent

> Summarize the completed work and upcoming commitment in at most two bullets.
> Name the source document for each bullet. Section references are optional.
> Use only the supplied facts.

### Supplied source: Harbor project note

> **Done:** Inventory sync completed Tuesday.
>
> **Next:** Access review is scheduled for Friday.

### Response

> - Inventory sync completed Tuesday. (Harbor project note)
> - Access review is scheduled for Friday. (Harbor project note)

### Proposed check

> Every bullet must cite both the source document and its section.

That check would fail both bullets for missing section references. The task
explicitly makes those references optional. The response uses two bullets,
names the source for each, distinguishes completion from a scheduled action
and adds no facts. It satisfies this small task.

**Reject the check as written.** A source quote can be copied accurately
while the criterion draws an unsupported obligation from it.

Replace the citation check with:

> Each bullet names the source document. A section reference may also appear,
> but is not required.

Record the original check, the optional-reference instruction, the corrected
wording and the new evaluation version. Review the correction before use.
Other requirements, such as factual support and the bullet limit, remain
separate checks.

Two useful controls make the distinction clearer:

| Variation | Judgment under the supplied task |
|---|---|
| One bullet includes both facts and names Harbor project note | Acceptable: the limit is at most two bullets, and both facts are present. |
| The response says the access review **completed** Friday | Unsupported: the source establishes a scheduled review. Revise that claim regardless of the citation-check correction. |

### If the instruction itself is ambiguous

Suppose a task instead says only, "Include document/section references,"
with no other citation rule. It does not settle whether document-only
references are acceptable or sections are required.

Mark a strict section-reference check **unresolved** and retain the disputed
interpretation. Seek clarification from the task owner before relying on
that check. If the owner adds a stricter requirement, apply it prospectively
with a new task version. Do not silently convert an old output into a failure.
Other justified checks can still establish a separate reason to revise.

## 3. Apply accepted checks and keep evidence with the judgment

Keep the criteria fixed for the review version. For each accepted check,
record `met`, `not_met`, `not_applicable`, or `unresolved`, with a source or
output excerpt explaining the judgment. Mark unfinished work **not reviewed**;
missing review is different from a reviewed question that remains unsettled.

Keep graded examples, expected answers and reviewer notes outside target
inputs. If you discover a bad criterion during grading, preserve the prior
record, correct the evaluation version and re-review affected results.
Do not report that correction as an improvement in the target's performance.

## 4. Make a bounded decision

| State | Action |
|---|---|
| A valid, applicable mandatory check fails | Revise or reject within the agreed decision scope. Retain other unresolved and unfinished checks in the record. |
| No established failure, but an unresolved check or interpretation could change the decision | Hold that decision for review. State what evidence or clarification is needed. |
| Required checks have not been reviewed | Continue the review. Do not treat missing judgments as success. |
| Required review is complete, applicable mandatory checks are met and no decision-critical uncertainty remains | Ready for the owner's decision within the declared scope. This is not blanket production clearance. |

Case count and an average score cannot resolve an invalid criterion, a
mandatory failure or an important coverage gap. State what this evaluation
allows the owner to conclude and what remains outside its scope.

### Copyable review record

Use a task-specific, versioned filename. Copy one check record per criterion,
then add the overall decision once for the reviewed output or comparison.

```text
Task/instructions and source versions:
Evaluation version and declared gaps:
Case and output identifiers/versions:

Criterion identifier and wording:
Supporting rule/fact and applicability:
Criterion disposition: accepted / rejected / unresolved
Response judgment (accepted checks only):
Evidence and reasoning:
Correction, clarification or unfinished review:
Reviewer and date:

Overall decision and scope:
Concrete action, owner and unresolved conditions:
```

Keep this manual worksheet separate from the evaluation JSON.
`benchprime validate` checks evaluation definitions; it does not validate this
worksheet, grade meaning or authorize the resulting action.

## 5. Observe whether the evaluation is useful

For a practitioner trial, save the person's initial decision before showing
the criteria or diagnostic examples. Both passes need the same task, visible
requirements and sources. Record any prior exposure or facilitator help;
someone who already knows the worked answer is not a blind reviewer.

After the criteria-assisted review, record a concrete correction or hold,
an adopted check, the effort required and the next item where it will be used.
If the original decision was already sound, record that too.

A second reading or facilitator help can explain a changed judgment. One
walkthrough does not establish causal improvement, broad accuracy or demand.
Observe the next actual use before claiming repeat value.

## Quality Check

All instructions and facts needed to inspect the fictional example appear
above. It demonstrates an unsupported obligation, a valid alternative, a
genuine factual failure and a separately ambiguous rule. These authored
illustrations are neither independent calibration nor performance evidence.
No target execution, data-sharing permission or automated decision is implied.

Return to [Start here](../START_HERE.md), the
[creation workflow](../workflows/generate.md) or the
[ticket-triage walkthrough](walkthrough.md).
