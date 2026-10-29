# Meeting actions: collection design

## Reader job and decision

Review whether an extractor can turn short meeting notes into agreed future
actions while preserving the available owner and deadline evidence.
The first decision is whether these cases and proposed checks are useful
enough for a downstream evaluation. This authored example contains no observed
target output or score.

## Authority and source boundary

[action-policy.txt](action-policy.txt) is the normative task policy. Its exact
text is included in every candidate under `/context/policy/0`.
The six note sources in [intake.json](intake.json) are descriptive synthetic
evidence. Each maps one-to-one to `/case/observations/notes` in MA-001 through
MA-006. Each pair represents alternative versions of an excerpt, rather than
successive turns in one meeting.

The author selected all inputs, criteria and response illustrations together
in one AI context. Rights to this original example are granted under the
[MIT license](../../LICENSE). No existing meeting dataset was copied.

## Smallest useful contrasts

| Family | Cases | Exact source edit | Intended distinction and invariant |
|---|---|---|---|
| MA-F-01: acceptance | MA-001, MA-002 | `Maya: Could we send the pricing brief Friday?` becomes `Maya: I'll send the pricing brief Friday.` | The pricing task joins the action list only in MA-002. Leo's cost-figure check, owner and Thursday deadline stay identical. |
| MA-F-02: deadline evidence | MA-003, MA-004 | `prepare the launch checklist.` becomes `prepare the launch checklist by Tuesday.` | The same accepted task gains a deadline. Its unassigned owner stays JSON `null`; missing due is `null` in MA-003. |
| MA-F-03: completion status | MA-005, MA-006 | `I finished updating` becomes `I'll update` | Completed work yields an empty action list; future work yields Noor's contact-list update with a `null` due. The task object, speaker and lack of deadline stay fixed. |

In all three pairs the only changed JSON path is
`/case/observations/notes`. The request, task, complete policy and no-tools
boundary are byte-for-byte unchanged. Source changes are deliberately small,
yet they are linguistic changes with grammatical adjustments. They do not
isolate every possible cue to acceptance or temporality. Actual edits are
validated; causal effects on a target remain unmeasured.

## Categories, themes and accounting

- **Agreed work**: accepted commitment versus proposal; unresolved conditions.
  Two primary cases. The conditional theme has no case.
- **Grounded owners and deadlines**: assignment evidence; deadline evidence.
  Two primary cases. The checklist pair also exercises an accepted task with
  no assigned owner, and with both owner and due missing in MA-003.
- **Future work**: completed versus pending work. Two primary cases.

This produces 6 unique cases, 3 populated categories, 5 themes (4 populated),
3 scenario groups and 17 checks. Primary counts sum to six. Secondary dimension
exposure overlaps and must not be added to the test count.

Five requirements are declared:

| Requirement | Exposure |
|---|---|
| MA-R-acceptance | MA-001 / MA-002: proposal and explicit acceptance |
| MA-R-owner | MA-001 / MA-002 / MA-003 / MA-004 / MA-006: self-commitment attribution or unassigned owner |
| MA-R-due | MA-001 / MA-002 / MA-003 / MA-004 / MA-006: stated deadlines or absent deadlines |
| MA-R-future | MA-005 / MA-006: completed or future task |
| MA-R-conditions | **Gap**: A3 excludes unresolved conditional commitments, but no case contains one |

Every case has an action-set check and a separate JSON-shape check. The five
nonempty expected responses also have a grounded-owner/deadline check.
MA-005 has no vacuous field check. Meaning and attribute judgments are semantic;
the format check is deterministic and collection-wide. All checks specify
applicability, alternatives and consequence. Source excerpts and hashes bind
each proposed criterion to the actual candidate input.

Equivalent task wording is acceptable; action order and JSON key order are
irrelevant. The [README's authored probes](README.md#reviewer-only-authored-probes)
show a valid paraphrase and an overcommitment that still passes the format
criterion. They support key review, with no independent calibration claim.
All eight anchors (six expected illustrations and two hero probes) are internal
reviewer material in [authored-draft.json](authored-draft.json) and
[evaluation.json](evaluation.json). They never enter candidate inputs.

## Limits and the next review boundary

The conditional gap is the one declared, unexposed target requirement.
Other unexercised behaviors include revocation, conflicting assignments,
pronoun resolution beyond "I'll", repeated tasks, embedded instructions,
calendar normalization and long meetings. None is claimed as covered.
The no-external-actions rule is visible in every input; this text-only
collection does not test a tool-enabled target's enforcement.

Principle links are author mappings. All 14 method-catalogue dispositions
remain deferred. Preparation and schema validation certify mechanical
consistency only. No live generation, target execution, production
representativeness or independent review is claimed. A reviewer can revise the
policy or add a new family, then regenerate the definition and inspect both
the changed source and its expected behavior before use.

## Quality Check

The [focused tests](../../tests/test_meeting_actions.py) freeze the six source
excerpts and independently state their expected action data. They check policy
preservation, exact contrasts, source authority, replay parity, honest gaps and
candidate isolation. These regression checks cannot establish whether a
semantic evaluator accepts every valid paraphrase or whether the collection
predicts performance on real meetings.
