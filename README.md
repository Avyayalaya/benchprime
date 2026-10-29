# BenchPrime

**Turn a task into cases, grading criteria and a clear view of what remains untested.**

An eval should help explain where a system fails and what to change next.
I built BenchPrime around that job. Bring the task, its rules and permitted
sources; use your AI assistant to create an evaluation you can inspect,
challenge and export.

**[Inspect an example](examples/meeting-actions/README.md)** ·
**[Create your own](START_HERE.md)** ·
**[Explore the design](docs/methodology.md)**

## Test whether the action was actually agreed

Suppose a meeting assistant turns notes into a follow-up list:

> Maya: Could we send the pricing brief Friday?<br>
> Leo: I'll check the cost figures by Thursday.

The rule is to list only explicitly accepted future actions. An answer that
assigns Maya the pricing brief for Friday invents a commitment.

**A valid result, authored for this illustration:**

```json
{
  "actions": [
    {
      "task": "Check the cost figures",
      "owner": "Leo",
      "due": "Thursday"
    }
  ]
}
```

The evaluation should also accept equivalent wording such as “Verify the
cost figures”. A rubric that requires one exact task phrase would reject
a valid answer.

That gives the collection useful distinctions to test:

| Change in the notes | What the check should establish |
|---|---|
| A suggestion becomes an explicit commitment | The action list should change. |
| An accepted task has no stated deadline | The answer should preserve the missing value, using `null` under this task's policy. |
| Work is already complete | It should stay out of the future-action list. |

![Actual meeting-actions casebook: source notes, proposed checks and the evidence behind them](assets/meeting-actions-case.png)

This is the actual casebook produced by the local renderer from the
[authored fictional example](examples/meeting-actions/README.md). Its criteria
are proposed and its gaps are recorded. The displayed answer is an
illustration, not a model-run result.
Unresolved conditional commitments remain an explicit gap in this small collection.

## Inspect the output without a model

From a full checkout of this repository, with Python 3.10+:

```powershell
python -m benchprime inspect examples/meeting-actions/evaluation.json
python -m benchprime render examples/meeting-actions/evaluation.json --output work/meeting-demo/casebook.html
```

Open `work/meeting-demo/casebook.html` locally. Browse the plan, cases,
criteria and gaps; download candidate inputs without the grading material.
These commands process a supplied evaluation and make no model calls.
GitHub shows HTML as source, so download/open the file for the interactive view.

The [ticket-routing walkthrough](docs/walkthrough.md) and
[larger Alder collection](packs/alder/v0.1/OVERVIEW.md) show other task shapes.
The method follows your requirements; the current formats cover English
text and JSON.

## Create an evaluation for your own task

```powershell
python -m benchprime start work/my-eval
```

Describe the job in `task.md`, add permitted sources, then give `KICKOFF.md`
to a file-capable assistant opened on this checkout. **The first output is
a test plan for your review.** Approve its scope before continuing to cases,
criteria, `evaluation.json`, a casebook and candidate-only JSONL.

The default path is an **assisted draft**. The
[first-session guide](docs/first-session.md) specifies the handoffs, optional
separate-context route and recovery steps. The assistant does the generation;
Python checks the files. Your assistant's normal costs and data policies apply.

## How the evaluation is built

**Start from the decision.** Explain why each category and case belongs.
Source rules, preferences and descriptive facts carry different authority.

**Make differences meaningful.** Record what changed between related cases,
what stayed fixed and why the expected behavior should change or remain stable.

**Challenge the grading criteria.** Test valid alternatives, convincing
mistakes and applicability. A criterion can quote a source perfectly and
still invent an obligation.

**Leave gaps visible.** Every declared requirement leads to a case or a
named gap. Coverage describes the test design; actual responses and judgments
establish performance.

The [methodology](docs/methodology.md) explains the reasoning and the
[creation workflow](workflows/generate.md) gives the assistant exact stages.

<details>
<summary>Explore the three methodology maps</summary>

The first map separates responsibilities for designing a good evaluation
from the capabilities being evaluated. The second follows a capability
down to a testable distinction. The third shows how to challenge the key.

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-atlas-mobile.png">
  <img src="assets/methodology-atlas.png" alt="Eleven responsibilities for evaluation design, grouped into intent and grounding, coverage and measurement, and delivery and revision.">
</picture>

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-depth-mobile.png">
  <img src="assets/methodology-depth.png" alt="Follow a capability through a distinction, failure mechanism and observable difference; record repeated or unsupported branches as stopping points or gaps.">
</picture>

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-review-mobile.png">
  <img src="assets/methodology-review.png" alt="Derive criteria from one case input, then review valid alternatives, plausible mistakes and uncertainty; preserve review-guided revisions.">
</picture>

</details>

## Use it on the next change

Keep the accepted evaluation fixed when comparing implementations of the
same task. Revise it when the governing rules or source facts change.
The [repeat-use guide](docs/reuse-an-evaluation.md) connects exports, your
approved runner, response records and a decision. Those execution and
grading steps remain separate from this package.

## Current scope

This is a developer preview with working local file tools and inspectable
examples. Useful case selection and fair criteria still need review.
The CLI does not enforce fresh contexts or create target responses.
Label shared-context work **author-assisted** and feedback-based repairs
**review-guided**. Independent practitioner value and superiority over
another generator remain unproven.

[MIT licensed](LICENSE), including the original documentation, assets and
fictional examples. Keep the copyright and permission notice when reusing
them. See [evidence and limitations](docs/evidence-and-limitations.md),
[release status](RELEASE_STATUS.json) and the [command reference](docs/getting-started.md).
