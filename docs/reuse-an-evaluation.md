# Use the evaluation on the next change

An evaluation becomes useful when it helps with the next decision too.
Keep the task, cases, criteria and observed responses versioned separately
so you can tell what caused a changed judgment.

## Decide what changed

| Change | Keep fixed | Create or review |
|---|---|---|
| A model, model setting or prompt implementation under the same task rules | Accepted evaluation version and candidate inputs | New target configuration and response records; review against the same criteria |
| A governing rule, source fact, output contract or task boundary | The old pack and its historical results | New brief and affected cases/criteria; new matching inputs/outputs before claiming performance under the new task |
| A criterion was wrong | Original inputs and responses, if they are still applicable | New criterion/review version; record the changed judgment as an evaluation correction |

A prompt edit can change the task itself. Check whether it adds a requirement
or changes authority before treating it as a model/prompt-only comparison.
For example, making optional section citations mandatory requires a new
task version. An old answer cannot retrospectively fail that new rule.

## Export the same inputs for a fair comparison

Use an accepted pack version and a new output directory. The supplied meeting
example is proposed, authored material; review its criteria before real use.

```powershell
python -m benchprime validate examples/meeting-actions/evaluation.json
python -m benchprime export examples/meeting-actions/evaluation.json --output work/meeting-comparison/inputs.jsonl
```

Each line has `case_id` and `input`. Keep `case_id` to associate results and
send only `input` to your own approved runner. Keep the criteria, casebook,
review probes and sibling cases out of that request. Blocked/reserved cases
are excluded by the exporter.

**Target execution is external to this package.** BenchPrime supplies no
run or response-grading command. Confirm the model, costs and data permissions
before execution. Give both compared configurations the same permitted inputs
and record anything that differs.

## Keep responses and decisions together

Save returned responses without editing them. A manual record can look like:

```text
Run label:
Model/version or prompt revision:
Task and source versions:
Evaluation and criteria version:
Case ID:
Exact response file:
Accepted criteria and judgments:
Supporting input/response excerpts:
Unresolved or unfinished checks:
Decision, action and owner:
Reviewer/date and assistance:
```

This is a manual worksheet, separate from the evaluation schema. Use the
[review guide](reviewing-an-evaluation.md) to reject unjustified criteria,
retain uncertainty and distinguish an unreviewed check from a real pass.
The two outputs below are **authored illustrations**, not model-run results:

| Same meeting input | What the review should establish |
|---|---|
| A response assigns Maya the pricing brief for Friday even though Maya only suggested it | The accepted-commitment check has a source-backed reason to fail. |
| Another response records only Leo's accepted task, phrased as “Verify the cost figures” | Equivalent task wording is acceptable; review owner, due date and completeness as separate requirements. |

A corrected response on one case supports a narrow finding. Keep regressions,
coverage gaps and differing effort visible; a headline average cannot cancel
a material mandatory failure.

## Change the task deliberately

Suppose the workflow should now list proposals alongside commitments. That
changes the requirements and output contract. Create a new workspace:

```powershell
python -m benchprime start work/meeting-v2 --from-intake examples/meeting-actions/intake.json
```

Edit its task and source policy, then have the assistant build a **new typed
intake from those edits**. Do not freeze the untouched bundled intake and
assume it reflects the new files. Review the design checkpoint, then create
new versions of the affected candidates and criteria.

Preserve v1. Records evaluated under v1 answer the old question; v2 answers
the revised one. The new evaluation still needs review, and historical
judgments remain attached to the rules that actually applied.

## Close the decision

Record a concrete result: retain the current configuration, revise a prompt,
hold for missing evidence or adopt a justified check. Record the review effort
and whether the check is used on the next actual item.

If nothing changes, record that too. A small comparison or facilitated review
cannot establish broad accuracy, independent calibration or product demand.
