# Create an evaluation for your task

Start with the [six-case meeting example](examples/meeting-actions/README.md)
if you want to see the result first. It is readable on GitHub without setup.

You need a full BenchPrime checkout, Python 3.10+ and an AI assistant that
can read and write files in that checkout. Your assistant's normal costs
and data policies apply.

## 1. Describe the job

From the repository root:

```powershell
python -m benchprime start work/my-eval
```

This creates `task.md`, `sources/` and `KICKOFF.md`. It creates a workspace;
your assistant will write the evaluation.

Fill in `task.md` and add permitted sources. A concrete example:

| Field | Example |
|---|---|
| Decision | Compare two prompts for extracting agreed meeting actions |
| Job and input | Read an action policy and one meeting excerpt |
| Required output | JSON actions with task, owner and due date |
| Rules that matter | Include accepted future work; exclude proposals and completed work; use `null` for missing owner/date |
| Sources and rights | The bundled fictional policy and notes, with their declared MIT rights |

Use your own requirements and source permissions for your task. Preferences
such as wording or ordering should remain flexible unless the task requires them.

To explore that supplied task, choose a **different, new** workspace:

```powershell
python -m benchprime start work/meeting-design --from-intake examples/meeting-actions/intake.json
```

Typed startup preserves `imported-intake.json` alongside the editable summary.
Keep that original intact. If you change the task, create a new current intake.

## 2. Review the test plan

**First message** — after editing `work/my-eval/task.md`, give this to your assistant:

```text
Read work/my-eval/KICKOFF.md and follow it for work/my-eval/task.md.
Propose collection-design.md and stop for my review before creating cases.
```

If you chose a different directory, substitute its path. The default is an
**author-assisted** draft in your existing conversation.

Read `collection-design.md` and decide:

- **Right rules?** Each proposed requirement should follow from the task or a governing source.
- **Right distinctions?** Include consequential differences and valid alternatives; name important gaps.
- **Permitted sources?** Resolve missing authority, essential facts and processing rights.

Request corrections before accepting the design. This pause is an assistant
instruction; Python does not enforce it.

## 3. Build and inspect the evaluation

**Second message** — use only after you accept the design:

```text
The design is approved for the stated scope. Continue with the assisted
draft route. Preserve the task's rules and source text. Write coherent
cases, proposed criteria with evidence and acceptable alternatives, and
explicit coverage gaps. Keep the work labelled author-assisted.
Run prepare, validate, inspect, render and export on new output paths.
Do not run a target, install a provider or publish anything.
Finish with artifact paths, actual help used and unresolved review issues.
```

| Output | Use it to |
|---|---|
| `casebook.html` | Read the cases, proposed checks, evidence and gaps |
| `evaluation.json` | Preserve the complete evaluation definition |
| `candidates.jsonl` | Supply case IDs and inputs to a separately approved runner |
| Review summary | See unresolved findings, assistance and revisions |

Open the casebook locally and choose **Inspect a scenario**. Read its input,
check the supporting rule and try an acceptable alternative. Could a valid
answer fail the proposed check? Then review coverage and
[challenge the criteria](docs/reviewing-an-evaluation.md).

The assistant writes the content. Python checks its structure and exports it.
Target execution and grading use your own separately approved process.

## Inspect an example without a model

To explore the supplied meeting-actions example first:

```powershell
python -m benchprime inspect examples/meeting-actions/evaluation.json
python -m benchprime render examples/meeting-actions/evaluation.json --output work/meeting-demo/casebook.html
```

Open the HTML locally in a browser. It includes case downloads and
candidate-only JSONL. These commands make no model calls. GitHub displays
HTML as source; download/open it locally. Use a new output path on repeat
runs because the tools refuse overwrites.

For source-file options, optional separated contexts and recovery, use the
[full first-session guide](docs/first-session.md).
For the next prompt, model or rule change, use the
[repeat-use guide](docs/reuse-an-evaluation.md).
