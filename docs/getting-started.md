# Command reference

**Creating your own evaluation?** Begin at [Start here](../START_HERE.md).
It gives you a task workspace and an exact assistant kickoff.
Use this page for individual operations on existing/generated packs.
For the complete assisted creation path, see the
[first-session guide](first-session.md); for another prompt or policy change,
see [repeat use](reuse-an-evaluation.md).

Use Python 3.10+ from the repository root. No installation, account or API key
is needed for these commands. Windows accepts the relative paths below;
the same commands also work on macOS/Linux.

## Inspect the supplied collection

```powershell
python -m benchprime validate packs/alder/v0.1/evaluation.json
python -m benchprime inspect packs/alder/v0.1/evaluation.json
```

The first command reports structural validity with `semantic_certification:
false`. The second reports 12 cases, 133 criteria, five categories and nine
themes. Review status remains `partial`: five criteria were corrected by an
operator and remain proposed.

Open [the casebook](../packs/alder/v0.1/delivery/read/CASEBOOK.html) in your
browser. Excel and Word versions are in that same folder.

## Export candidate inputs

```powershell
python -m benchprime export packs/alder/v0.1/evaluation.json --case-number 1 --output work/candidate.json
python -m benchprime export packs/alder/v0.1/evaluation.json --output work/candidates.jsonl
```

The selected JSON has a tracking `case_id` and the candidate `input`. Pass
only `input` to the target. Never include criteria, casebook text, sibling
cases or expected behavior. Blocked/reserved cases are excluded from export.
Use a fresh context for each candidate.

Commands create output parents as needed and refuse overwrites. Use a new
filename when repeating a command. Keep changes outside `packs/`.

## Render a pack

```powershell
python -m benchprime render packs/alder/v0.1/evaluation.json --output work/casebook.html
```

Open `work/casebook.html`. HTML rendering is offline and standard-library-only.
The file embeds per-case Markdown downloads and the same candidate-only JSONL
produced by `export`, including its blocked/reserved-case exclusions. It can
be moved or shared without sibling files. Markdown downloads contain reviewer
criteria; send only the JSONL record's `input` to a target.

Standalone HTML omits links to Office files that were not generated.
The shipped Office files are prebuilt. Regenerating Office delivery through
the optional `benchprime.render` module requires the `office` dependencies;
the basic quickstart does not.

## Create your own evaluation

Run `python -m benchprime start work/my-eval`, edit its task and source material,
then paste the generated `KICKOFF.md` into an AI assistant with file access to this
checkout. The assistant follows [the guided workflow](../workflows/generate.md)
and manages the schema work. Local commands handle freezing, binding, checking
and export. See [the authored walkthrough](walkthrough.md) for concrete outputs.

The assistant's normal usage/costs and data policies still apply. This package
does not supply a model session or grant permission to upload private data.

For an exposed development rehearsal:

```powershell
python -m benchprime freeze examples/alder-intake.json --output work/brief.json
python -m benchprime references work/brief.json --output work/references.json
```

Both are offline operations. They do not generate tests. Alder has already
been used during development; regenerating it is a regression rehearsal,
not a fresh holdout.

## Preparing generated JSON

The assistant writes a collection-first draft matching
`schemas/evaluation-design.json`. It chooses evidence pointers and semantic
content. It may omit derived evidence `text`/`sha256`, excerpt offsets,
`pattern_bundle_hash` and `collection.catalog_hash`:

```powershell
python -m benchprime prepare work/draft.json --output work/evaluation.json
python -m benchprime validate work/evaluation.json
python -m benchprime render work/evaluation.json --output work/my-casebook.html
```

`prepare` derives only declared mechanical fields. If supplied evidence or a
hash disagrees with its source, it fails. It never chooses a verdict or repairs
the meaning. An omitted `pattern_applications` list is explicitly populated
with **deferred**, unassessed dispositions, reported in stdout. This is allowed
only for draft/partial packs; review those dispositions before claiming
method application. Omit unknown derived values instead of inventing hashes.

## Errors and scope

Commands return exit 1 with `ERROR:` for invalid input or filesystem failures;
argument syntax errors return exit 2. No successful output is reported after
a failed check. The validator implements the documented schema subset, not
a general JSON Schema engine.

Run local checks with `python -m unittest discover -s tests -v`.
See [evidence and limitations](evidence-and-limitations.md) and
[repository change guidelines](../CONTRIBUTING.md).
