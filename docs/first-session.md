# Your first creation session

The first useful output is a test plan you can question. Once the plan fits
the job, continue to cases, criteria and a casebook.

## Use a concrete local setup

Open the full BenchPrime checkout in a file-capable Copilot session and use
Python 3.10 or later from its repository root. The local walkthrough is
exercised on Windows with Python 3.13; the offline commands also have
Linux/Python 3.10 coverage. Your assistant's normal costs and data policies apply.

There are two distinct activities:

- **Inspect an existing example:** use the commands in
  [Start Here](../START_HERE.md#inspect-an-example-without-a-model). This is
  offline and needs no model access.
- **Create a new evaluation:** give the generated kickoff to your assistant.
  The assistant writes the content; Python checks and exports it.

The default creation route is an **assisted draft**. It uses the conversation
you already have and records that exposure. Separate-context work needs
the deliberate handoffs below. A new message in the same conversation
does not establish independence.

## First message: stop at the design

```powershell
python -m benchprime start work/my-eval
```

Fill `work/my-eval/task.md`, add permitted sources, and paste
`work/my-eval/KICKOFF.md` into the assistant. For a supplied task, you can
start from the new [meeting-actions intake](../examples/meeting-actions/intake.json):

```powershell
python -m benchprime start work/meeting-design --from-intake examples/meeting-actions/intake.json
```

The kickoff asks the assistant to **stop after `collection-design.md`**.
That file should state:

- The decision, task requirements and which sources justify them.
- The capabilities and categories to test, with a reason for each.
- The scenario groups, expected contrasts and known gaps.
- Processing rights, unresolved questions and the assistance mode.

Separate questions that change validity or permission from optional preferences.
Unspecified ordering or wording can remain flexible; a preferred style should
not become a new mandatory grading rule.

Review the proposed distinctions. For meeting actions, a suggestion versus
an accepted commitment matters; a different spelling of the same accepted
task usually should not change the result. Add missing requirements now.

This pause is an assistant instruction, not a software-enforced gate. If the
assistant writes cases early, preserve that output as premature work. Settle
the design before using it, and disclose any exposure it introduced.

## Second message: approve a scope and continue

After you accept the design, use a specific continuation:

```text
The design is approved for the stated scope. Continue with the assisted
draft route. Preserve the task's rules and source text. Write coherent
cases, proposed criteria with evidence and acceptable alternatives, and
explicit coverage gaps. Keep the work labelled author-assisted.
Run prepare, validate, inspect, render and export on new output paths.
Do not run a target, install a provider or publish anything.
Finish with artifact paths, actual help used and unresolved review issues.
```

Expect `evaluation.json`, `casebook.html`, `candidates.jsonl` and a review
summary. Commands and their exit status should appear in the session.
Use [the workflow](../workflows/generate.md) for exact schema/stage requirements.
A generated file alone does not establish that its contents are correct.

## Optional: separate the stages manually

Use this route only when your runtime can provide clean contexts and you can
control what each one receives. The CLI does not create sessions, restrict
file access or verify conversation history. Keep a record of what was actually
visible; when that cannot be established, retain the assisted label.

| Stage | Supply | Keep out | Save for the next stage |
|---|---|---|---|
| Profile reading | Frozen brief, computed references and inventory schema | Challenge interpretation | Profile inventory |
| Challenge reading, fresh context | The same brief, references and schema | Profile inventory and prior discussion | Challenge inventory |
| Reconciliation/design | Both inventories and their sources | Target outputs | Agreed requirements, disputes and collection design |
| Case writing | Agreed design and sources | Target outputs | Self-contained candidate inputs |
| Initial criteria, fresh context per case | Only an opaque ID and that case's complete `input`, plus the neutral request below | Case title, family, failure hypothesis, siblings, draft keys and expected response | Proposed criteria and exact supporting passages |
| Review and assembly | Cases, criteria, evidence and labelled review probes | Unapproved external/customer material | Versioned revisions, pack and review record |

Neutral request for the initial criteria pass:

```text
For this case input, propose observable acceptance criteria. For each,
state applicability, supporting input passage, acceptable alternatives
and consequence of failure. Separate mandatory requirements from
preferences and diagnostic observations. Leave ambiguity unresolved.
Use only the supplied input; do not infer an author's intended answer.
```

Before assembly, candidate inputs may be copied manually from the case draft.
The checked-pack `export` command is for an assembled, valid evaluation;
it cannot export an unfinished criteria-free draft. Use neutral case IDs and
filenames in handoffs so they do not disclose the expected failure.

Any pass that sees earlier keys or critique is **review-guided**. Opening
another tab does not erase prior context, shared workspace instructions or
memory. Record these limits instead of asserting blind generation.

## Recover without losing the trail

| What happened | Recovery |
|---|---|
| The assistant cannot read files or run Python | Use a compatible local session, or inspect a supplied example offline. Do not claim a newly generated checked pack. |
| The schema check fails | Keep the failed draft, read the specific error and repair that file in a new version. Do not weaken the validator. |
| A fresh context saw the intended answer | Record the exposure. Treat that pass as assisted/review-guided, or use a genuinely unexposed reviewer for a new pass. |
| The session was interrupted | List the saved task/source versions, last completed stage, actual context exposure and unresolved questions. Resume from verified files; file existence alone is not a completed stage. |
| A source or governing rule changed | Freeze a new brief and review affected cases/criteria. Preserve the old pack and results. |
| An output filename already exists | Choose a new versioned filename. The commands intentionally refuse overwrites. |

When the first pack is ready, [review its criteria](reviewing-an-evaluation.md)
before relying on its results. Then use the [repeat-use guide](reuse-an-evaluation.md)
for the next prompt, model or policy change.
