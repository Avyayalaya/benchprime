# Working on this repository

The supported package is an assistant-led evaluation-creation workflow with
offline Python tools for English text and JSON. Python 3.10+ and a full
checkout are required. Provider execution, target runners and automatic
semantic grading are outside the current package.

## Reproduce a problem safely

Use the smallest fictional or permissioned example that reproduces it.
Include the command, Python/OS version, expected behavior, actual error and
whether the input or criteria were changed.

Do not post customer records, employer-confidential material, credentials or
raw private assistant conversations. Repository access does not establish
permission to share the data used in an evaluation.

## Preserve the evaluation trail

- Keep supplied source inputs, criteria and provenance intact. Use a new
  example/version for changed meaning.
- Separate authored fixtures, structural tests and actual target results.
- Keep candidate exports free of grading material.
- A renderer change should regenerate affected HTML projections deliberately
  and preserve input/criterion semantics.
- New generation or target execution needs its own permitted data/runtime scope.

Run the local checks from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The [MIT license](LICENSE) applies to the original repository material.
External dependencies and new source data retain their own terms.
