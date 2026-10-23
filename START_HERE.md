# Create an evaluation for your purpose and use case

First define what you want the evaluation to establish and what you are
evaluating. The steps below use the local route supplied in this repository:
an AI assistant that can read files and run Python. That is one way to operate
BenchPrime. The evaluation's subject and purpose are chosen separately.
Model use follows your assistant's normal costs and data policies.

## 1. Start a workspace

From the repository root:

```powershell
python -m benchprime start work/my-eval
```

This creates:

```text
work/my-eval/
  task.md
  KICKOFF.md
  sources/
```

State the evaluation purpose, the subject or use case, and the requirements
in `task.md`.
Add sources and say which contain rules, facts or examples. State what you
have permission to process. The assistant should ask for missing information
when it changes the requirements or what counts as a correct answer.

Already have a task file?

```powershell
python -m benchprime start work/my-eval --task my-task.md
```

Use a new directory name if one exists. The command never overwrites a prior
workspace and does not make model calls.

## 2. Give your assistant the kickoff

Paste the contents of `work/my-eval/KICKOFF.md` into the assistant opened on
this repository. The kickoff names your task, the workflow and the output
directory. It tells the assistant to write the JSON files and run the commands.

The assistant first lists and checks the requirements. It then plans the test
categories, writes cases, derives grading criteria and reviews the result.
You supply the task's rules and settle questions the source material cannot
answer. You also review whether the final cases and criteria fit the task.

The workflow uses fresh contexts for blind work when available. If those
contexts cannot be established, the work must remain explicitly author-assisted.
The Python tools do not enforce assistant isolation or certify the judgments.

## 3. Inspect the result

The expected artifacts in your workspace are:

- `collection-design.md`: what needs testing, why each category exists and what is still missing.
- `evaluation.json`: cases, grading criteria, sources, coverage and review status.
- `casebook.html`: a standalone browser view with embedded per-case Markdown and candidate-only JSONL downloads.
- `candidates.jsonl`: the inputs to send to the target, with grading material excluded.
- A review summary: changes made, assistance used and unresolved issues.

Start with the overview. Check the rationale, then the criteria and their
source support. A successful structural check is not an independent quality
endorsement.

Before using the results for a decision, follow
[Review an evaluation](docs/reviewing-an-evaluation.md). It shows how to catch
an unjustified criterion, preserve disputed judgments and record the action
supported by the evidence.

## Reference inputs

```powershell
python -m benchprime start work/routing-demo --from-intake examples/ticket-triage/intake.json
```

This copies the declared task and sources into an editable workspace. It
does not generate cases. Follow [the worked creation](docs/walkthrough.md)
to inspect an explicitly authored result and replay its offline processing.

No hosted account or BenchPrime provider configuration is required.
Do not submit private data to your assistant without appropriate permission.
