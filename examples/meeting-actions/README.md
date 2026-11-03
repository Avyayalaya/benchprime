# Extracting actions from meeting notes

This example tests a system that extracts agreed future actions from meeting
notes. The policy defines which tasks qualify, how to handle missing owners
and dates, and which wording differences are acceptable. Six cases test three
of those distinctions.

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

**Read all six cases below.** Each uses the same [complete action policy](action-policy.txt).
The responses shown here are authored illustrations; no target model was run.

For interactive inspection, **[download the casebook](casebook.html?raw=1)
and open it locally in your browser**. GitHub's regular HTML file view shows
source code. [Evaluation JSON](evaluation.json) contains the full definition;
[candidate JSONL](candidates.jsonl) contains case IDs and isolated inputs.

## Six cases you can inspect here

These are alternative scenarios, not consecutive turns in one meeting.

### MA-001 / MA-002: a proposal becomes a commitment

MA-001 is the excerpt above. In MA-002, only Maya's statement changes:

```text
Maya: I'll send the pricing brief Friday.
Leo: I'll check the cost figures by Thursday.
```

Now both actions belong:

```json
{"actions": [{"task": "Send the pricing brief", "owner": "Maya", "due": "Friday"}, {"task": "Check the cost figures", "owner": "Leo", "due": "Thursday"}]}
```

**What to check:** A2 establishes explicit acceptance; A3 excludes the earlier
proposal. Leo's task, owner and Thursday deadline must stay unchanged.

### MA-003 / MA-004: a deadline appears; the owner stays unknown

MA-003:

```text
Maya: Agreed: prepare the launch checklist. No owner has been assigned.
```

```json
{"actions": [{"task": "Prepare the launch checklist", "owner": null, "due": null}]}
```

MA-004:

```text
Maya: Agreed: prepare the launch checklist by Tuesday. No owner has been assigned.
```

```json
{"actions": [{"task": "Prepare the launch checklist", "owner": null, "due": "Tuesday"}]}
```

**What to check:** A4 includes accepted work with missing fields. Maya is the
speaker, but she has not taken ownership. Adding Tuesday fills only the deadline.

### MA-005 / MA-006: completed work becomes future work

MA-005:

```text
Noor: I finished updating the contact list.
```

```json
{"actions": []}
```

MA-006:

```text
Noor: I'll update the contact list.
```

```json
{"actions": [{"task": "Update the contact list", "owner": "Noor", "due": null}]}
```

**What to check:** A3 excludes completed work. A2 includes Noor's future
self-commitment; A4 keeps the unstated deadline as `null`.

## What this small collection covers

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

For your own task, [create a workspace and review its design](../../START_HERE.md).

## Quality Check

Source/policy preservation, exact contrast edits, draft replay and candidate
isolation have focused [tests](../../tests/test_meeting_actions.py). These are
structural and fixed-source checks, with no semantic-calibration claim.
All criteria remain proposed; no target run or independent review is claimed.
The [provenance record](provenance.json) states the boundary.

Original synthetic material; **[MIT licensed](../../LICENSE)**.
