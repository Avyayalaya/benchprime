# Get to a useful evaluation

Start by inspecting a complete example, or go straight to your own task.
The local tools use Python 3.10+ from a full repository checkout.

## Inspect an example without a model

The [meeting-actions example](examples/meeting-actions/README.md) starts with
a familiar mistake: treating a suggestion in meeting notes as an agreed action.
Read its sources, proposed checks, acceptable alternatives and gaps.

```powershell
python -m benchprime inspect examples/meeting-actions/evaluation.json
python -m benchprime render examples/meeting-actions/evaluation.json --output work/meeting-demo/casebook.html
```

Open `work/meeting-demo/casebook.html` in a browser. These commands process an
already-authored example; they make no model calls. The HTML embeds case
downloads and candidate-only JSONL, so it works without a server or sibling
files. GitHub displays HTML as source; download/open it locally.

Use a new output path on a repeat run. Commands refuse overwrites.

## Create an evaluation for your own task

```powershell
python -m benchprime start work/my-eval
```

This creates `task.md`, `sources/` and `KICKOFF.md`. Describe the job, what
you want to learn or decide, the rules it must follow and which material it
can use. Identify source roles and processing rights.

Paste the generated kickoff into a file-capable assistant opened on this
checkout. It asks for **`collection-design.md` first, then a stop for your
review**. The first decision is whether the test plan covers the behaviors
that matter. Cases and criteria follow after you approve that plan.

The [first-session guide](docs/first-session.md) gives a concrete local
Copilot setup, the continuation message, optional manual context handoffs
and recovery steps. The default route is an **assisted draft**. Your assistant's
normal costs and data policies apply; the CLI neither runs the model nor
enforces conversation isolation.

To supply an existing task or start from the example's task:

```powershell
python -m benchprime start work/custom-eval --task my-task.md
python -m benchprime start work/meeting-design --from-intake examples/meeting-actions/intake.json
```

These commands create workspaces. They do not generate cases or authorize
processing private material.

## Inspect what comes back

| File | What to look for |
|---|---|
| `collection-design.md` | Why each category belongs; intended contrasts and gaps |
| `evaluation.json` | Cases, criteria, source evidence, alternatives and actual review state |
| `casebook.html` | Readable overview and case details, with embedded downloads |
| `candidates.jsonl` | Only case IDs and inputs for a separately approved target process |
| Review summary | Changes made, help/context exposure and unresolved findings |

Start with one case. Check whether a valid answer could fail its rubric,
then inspect the whole collection's coverage. Structural validity is only
one part of that review.

Use [Review an evaluation](docs/reviewing-an-evaluation.md) for the judgment
record and [Use it on the next change](docs/reuse-an-evaluation.md) for repeat use.
The [command reference](docs/getting-started.md) covers individual operations.
