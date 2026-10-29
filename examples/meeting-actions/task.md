# Meeting actions

## The job

Turn meeting notes into a list of genuinely agreed future actions without
converting suggestions into commitments.

## Evaluation purpose

Give a reviewer a small, inspectable collection for checking whether an
action-extraction system respects acceptance, ownership, deadlines and
completion status. The intended first use is to review the inputs and expected
behavior before deciding whether to evaluate a real system.

## Candidate input and output

Each input carries the whole [action policy](action-policy.txt), one request and
one short meeting excerpt. Return a JSON object with an `actions` list; each
action has `task`, `owner` and `due`. Include every explicitly accepted,
unconditional future task. Use JSON `null` for each missing owner or due date.
Preserve task meaning; equivalent wording is acceptable.

Exclude unaccepted proposals, unresolved conditional commitments and completed
work. Speaker attribution identifies the owner of "I'll"; agreement alone
does not identify an owner. No tools or external actions.

## Sources and authority

- `MA-ACTION-POLICY` in [intake.json](intake.json) is normative.
- `MA-NOTES-001` through `MA-NOTES-006` are descriptive evidence. Each is a
  separate synthetic meeting excerpt, including paired counterfactual variants.
- All source notes, policy, criteria and illustrative responses are original,
  fictional, AI-assisted authoring in one context. There are no real meetings,
  employers, participants or confidential records.
- All example material is supplied under the repository's [MIT license](../../LICENSE).

## Bounded collection

Six diagnostic cases form three controlled pairs: proposal to accepted
commitment; missing to explicit deadline; completed to future work. The
[collection design](collection-design.md) records the exact edits and invariants.
Unresolved conditional commitments remain an explicit coverage gap. This
collection makes no claim to exhaustive meeting-language coverage.

## Use boundary

The [casebook](casebook.html) and [evaluation definition](evaluation.json) are
reviewer material. Only [candidate inputs](candidates.jsonl) belong at the target
boundary. Responses in this example are authored illustrations. No target has
been run, and no independent semantic calibration or live-generation result is
claimed.
