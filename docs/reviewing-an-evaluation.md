# Review an evaluation before relying on its results

Two questions matter before acting on an eval: is the check fair,
and does the answer meet it? Combining those questions can make a flaw in
the rubric look like a flaw in the system.

Work through them separately and keep the evidence with the decision.
Bring the original task, permitted sources and proposed evaluation.
If you have outputs to review, keep the instructions they were produced
under. Obtain or run those outputs through your own approved process.
This is a manual review guide; the local tools check the evaluation files.

## 1. Agree on the decision and preserve the original requirements

Start with the action the result could change: accepting an output,
revising a prompt or adding a check before the next workflow change.
Name the person who can make that decision and the behaviors this collection
leaves untested.

Keep the task instructions, source versions, evaluation version and output
versions together. For existing outputs, use the requirements that actually
applied when they were produced. A newly desired standard needs a new task
version and matching outputs; it cannot establish a failure in an old output.
Do not infer permission to process material from its public availability.

## 2. Review the criteria before judging responses

Ask four things of each proposed criterion:

- Which target-visible rule or fact supports it?
- Is it mandatory, a preference, or a diagnostic observation?
- When does it apply, and can that condition be established?
- Could a competent alternative satisfy the task and fail this check?

Record the criterion as **accepted**, **rejected** or **unresolved** in your
review notes. This records whether the check is justified. The response gets
its own judgment later. Freezing a version makes it traceable; it still needs
to earn your agreement.

Correct or remove a demonstrably unsupported check in a new evaluation
version, retaining the original and the reason. Leave uncertain authority
or interpretation unresolved. Do not grade a response against a rejected
or unresolved check, and do not count that check as passed or not applicable.
`not_applicable` belongs to a valid conditional check whose condition is
known not to hold.

## Worked example: the check is too strict

This fictional example shows how a plausible check can fail a valid
answer. The bad check and response were authored for illustration; no
generator or target was run to produce them, and they have no calibration claim.

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

**Reject the check as written.** The source is clear about what is
optional. Adding a stricter rule would penalize a response that followed
the task.

Replace the citation check with:

> Each bullet names the source document. A section reference may also appear,
> but is not required.

Record the original check, the optional-reference instruction, the corrected
wording and the new evaluation version. Review the correction before use.
Other requirements, such as factual support and the bullet limit, remain
separate checks.

Test the corrected check against these two variations:

| Variation | Judgment under the supplied task |
|---|---|
| One bullet includes both facts and names Harbor project note | Acceptable: the limit is at most two bullets, and both facts are present. |
| The response says the access review **completed** Friday | Unsupported: the source establishes a scheduled review. Revise that claim regardless of the citation-check correction. |

### If the instruction itself is ambiguous

Suppose another task says only, "Include document/section references,"
with no other citation rule. It does not settle whether document-only
references are acceptable or sections are required.

Mark a strict section-reference check **unresolved** and retain the disputed
interpretation. Seek clarification from the task owner before relying on
that check. If the owner adds a stricter requirement, apply it prospectively
with a new task version. Do not silently convert an old output into a failure.
Other justified checks can still establish a separate reason to revise.

## 3. Apply accepted checks and keep evidence with the judgment

Keep the criteria fixed for each review version. For each accepted check,
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

Name the action the result supports and the uncertainty it
leaves behind. An average score can hide a failed mandatory requirement;
a large case count can hide a coverage gap. Keep both visible in the decision.

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

The practical test is whether someone uses the evaluation to
change an action or adopts a justified check for the next item. For a trial,
save the person's initial decision before showing
the criteria or diagnostic examples. Both passes need the same task, visible
requirements and sources. Record any prior exposure or facilitator help;
someone who already knows the worked answer is not a blind reviewer.

After the criteria-assisted review, record a concrete correction or hold,
an adopted check, the effort required and the next item where it will be used.
If the original decision was already sound, record that too.

Record the extra work the review creates. A second reading or
facilitator help can explain a changed judgment, so one walkthrough cannot
establish causal improvement, broad accuracy or demand. Observe the next
actual use before claiming repeat value.

## Quality Check

The fictional task, source, response and flawed check appear together
so you can inspect the reasoning. The examples distinguish an unsupported
obligation, a valid alternative, a genuine factual failure and an ambiguous
rule. They illustrate the review method; independent calibration and target
performance remain unmeasured. Data permissions and execution decisions
remain yours to establish separately.

Return to [Start here](../START_HERE.md), the
[creation workflow](../workflows/generate.md) or the
[ticket-triage walkthrough](walkthrough.md). For a subsequent comparison,
use [the repeat-use guide](reuse-an-evaluation.md) to keep task, evaluation
and response versions separate.
