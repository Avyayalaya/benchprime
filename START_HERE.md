# Create your first evaluation

You need a full BenchPrime checkout, Python 3.10+ and an AI assistant that
can read and write files in that checkout. Your assistant's normal costs
and data policies apply.

## 1. Describe the job

From the repository root:

```powershell
python -m benchprime start work/my-eval
```

This creates `task.md`, `sources/` and `KICKOFF.md`.

In `task.md`, describe what your AI should do, what decision the evaluation
should support and which rules it must follow. Add permitted sources and
identify their roles and processing rights.

## 2. Review the test plan

Give the generated `KICKOFF.md` to your file-capable assistant.
It should write **`collection-design.md` and stop for your review**.

Check whether the proposed categories and scenarios cover the distinctions
that matter. Resolve questions about validity and permission before
continuing. Your assistant must honor this review pause. Python does not enforce it.

## 3. Build and inspect the evaluation

Approve the stated design, then continue with the
[copyable second message](docs/first-session.md#second-message-approve-a-scope-and-continue).

| Output | Use it to |
|---|---|
| `casebook.html` | Read the cases, proposed checks, evidence and gaps |
| `evaluation.json` | Preserve the complete evaluation definition |
| `candidates.jsonl` | Supply case IDs and inputs to a separately approved runner |
| Review summary | See unresolved findings, assistance and revisions |

Start with one case: could a valid answer fail its checks? Then review the
collection's coverage. Keep the work labelled **author-assisted** and
[review the criteria](docs/reviewing-an-evaluation.md) before relying on them.

The assistant generates the content. Python checks and exports it.
BenchPrime does not run your target or grade its responses.

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

For source-file options, manual context handoffs and recovery, use the
[full first-session guide](docs/first-session.md).
For the next prompt, model or rule change, use the
[repeat-use guide](docs/reuse-an-evaluation.md).
