# Meeting actions

Meeting summaries can create work nobody agreed to do. This example checks
whether an extractor keeps the distinction.

**Input excerpt, MA-001** (the [full candidate](candidates.jsonl) also includes
the complete [action policy](action-policy.txt)):

```text
Maya: Could we send the pricing brief Friday?
Leo: I'll check the cost figures by Thursday.
```

**Illustrative expected response - authored:**

```json
{"actions": [{"task": "Check the cost figures", "owner": "Leo", "due": "Thursday"}]}
```

Only Leo accepted a future task. Maya proposed one. The policy also includes
accepted tasks with missing owners or deadlines, using JSON `null` for each
missing field.

Open the **[complete casebook](casebook.html)** to inspect all six inputs and
their checks. [Evaluation JSON](evaluation.json) contains the full definition;
[candidate JSONL](candidates.jsonl) contains only target inputs.

## What changes across the cases

| Pair | One controlled distinction |
|---|---|
| MA-001 / MA-002 | Maya's proposal becomes her explicit commitment; Leo's task stays fixed. |
| MA-003 / MA-004 | An agreed checklist gains Tuesday as its deadline; its owner stays unspecified. |
| MA-005 / MA-006 | Noor's completed update becomes future work; no deadline is supplied. |

There are 6 cases, 3 families and 17 checks. Four of five declared requirements
are exposed. **Unresolved conditional commitments are a gap.** Longer meetings,
conflicting assignments and instructions embedded in notes also need further
cases. See the [design and limits](collection-design.md).

## Reviewer-only authored probes

These are illustrative responses created alongside the cases in one AI
context. They are excluded from every exported candidate.

**Competent equivalent wording:**

```json
{"actions": [{"task": "Verify the cost figures", "owner": "Leo", "due": "Thursday"}]}
```

This preserves the agreed work. Literal matching against "Check" would reject
a valid paraphrase.

**Plausible overcommitment:**

```json
{"actions": [{"task": "Send the pricing brief", "owner": "Maya", "due": "Friday"}, {"task": "Check the cost figures", "owner": "Leo", "due": "Thursday"}]}
```

Its JSON shape is valid. Its extra action and assignment lack an accepted
commitment in MA-001.

## Inspect or rebuild locally

From the repository root, with Python 3.10+ and fresh output paths:

```powershell
python -S -m benchprime inspect .\examples\meeting-actions\evaluation.json
python -S -m benchprime prepare .\examples\meeting-actions\authored-draft.json --output .\meeting-actions-replayed.json
python -S -m benchprime render .\meeting-actions-replayed.json --output .\meeting-actions-casebook.html
```

These commands operate offline. Replaying a draft binds and validates the
authored definition; it makes no model calls.

## Quality Check

Source/policy preservation, exact contrast edits, draft replay and candidate
isolation have focused [tests](../../tests/test_meeting_actions.py). These are
structural and fixed-source checks, with no semantic-calibration claim.
All criteria remain proposed; no target run or independent review is claimed.
The [provenance record](provenance.json) states the boundary.

Original synthetic material; **[MIT licensed](../../LICENSE)**.
