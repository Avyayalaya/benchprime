# Export your priorities

Use & adapt in the casebook exports a JSON profile directly, entirely offline.

For workbook edits: keep the original delivery intact, save a copy as `edited_priorities.xlsx` next to the delivery folder, and edit only the blue Customer priority cells. From the delivery root, run:

```powershell
python .\run\export_priorities.py --workbook ..\edited_priorities.xlsx --output ..\customer_priorities.json
```

Python 3.10+ standard library only; no package install, creator pack or creator checkout is required. The helper reads the bundled public customer metadata and manifest, validates pack identity and requires finite, nonnegative values with at least one positive priority. Blank cells mean zero when at least one value is set. A new output file is required. Values normalize across these root dimensions only. It neither changes cases/criteria nor computes a model-performance score. Source/content edits require a new reviewed collection. Manifest hashes detect accidental drift under trusted local use, not malicious rewriting.
