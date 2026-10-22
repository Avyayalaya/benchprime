"""Portable stdlib-only export of customer priorities from a delivered workbook."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def read_sheet(book, name):
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    sheets = [s for s in workbook.findall("s:sheets/s:sheet", NS) if s.get("name") == name]
    require(len(sheets) == 1, f"Workbook is missing the {name} sheet")
    relation = sheets[0].get("{" + NS["r"] + "}id")
    rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    paths = [r.get("Target") for r in rels if r.get("Id") == relation]
    require(len(paths) == 1, "Workbook sheet relationship missing")
    target = paths[0]
    require(".." not in target.split("/"), "Unsupported workbook sheet path")
    path = target.lstrip("/") if target.startswith("/") else "xl/" + target
    strings = []
    if "xl/sharedStrings.xml" in book.namelist():
        strings = ["".join(si.itertext()) for si in ET.fromstring(book.read("xl/sharedStrings.xml"))]
    cells = {}
    for c in ET.fromstring(book.read(path)).findall(".//s:sheetData/s:row/s:c", NS):
        if c.find("s:f", NS) is not None:
            cells[c.get("r")] = {"formula": True}
            continue
        value = c.find("s:v", NS)
        kind = c.get("t")
        if kind == "inlineStr":
            cells[c.get("r")] = "".join(c.find("s:is", NS).itertext())
        elif value is not None and value.text is not None:
            if kind == "s":
                cells[c.get("r")] = strings[int(value.text)]
            elif kind in (None, "n"):
                cells[c.get("r")] = float(value.text)
            else:
                cells[c.get("r")] = {"invalid_type": kind}
    return cells


def export_profile(workbook, package):
    package = Path(package).resolve()
    manifest = json.loads((package / "manifest.json").read_text("utf-8"))
    require(manifest.get("document_type") == "evaluation_design_delivery", "Unknown delivery manifest")
    model_path = "read/CUSTOMER_MODEL.json"
    raw = (package / model_path).read_bytes()
    require(sha(raw) == manifest["files"][model_path], "Customer metadata does not match delivery")
    model = json.loads(raw)
    require(sha(canonical(model).encode("utf-8")) == manifest["customer_model_hash"], "Customer model hash mismatch")
    with ZipFile(workbook) as book:
        meta, values = read_sheet(book, "_profile"), read_sheet(book, "Priorities")
    require(meta.get("B1") == manifest["pack_hash"] and meta.get("B2") == manifest["customer_model_hash"],
            "Workbook belongs to a different or stale pack")
    roots = [d for d in model["dimensions"] if d["parent_id"] is None]
    overrides = {}
    for row, root in enumerate(roots, 2):
        require(values.get(f"A{row}") == root["id"], "Priority dimensions were changed")
        value = values.get(f"C{row}", 0)
        require(type(value) in (float, int) and math.isfinite(value) and value >= 0,
                f"Priority for {root['label']} must be a finite nonnegative number (not a formula)")
        overrides[root["id"]] = value
    # Reject unexpected editable values beyond the known root set/total row.
    require(not any(address.startswith("C") and int(address[1:]) > len(roots) + 2
                    for address in values), "Unexpected priority rows")
    total = sum(overrides.values())
    require(math.isfinite(total) and total > 0, "Enter at least one positive priority; an all-blank/zero profile is unset")
    return {"document_type": "evaluation_customer_profile", "pack_hash": manifest["pack_hash"],
            "overrides": overrides, "normalized": {k: v / total for k, v in overrides.items()},
            "meaning": "Customer importance preferences only; no target score or source change"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = export_profile(args.workbook, args.package)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(f"Customer profile written: {args.output}. Original cases and criteria unchanged.")
    except (ValueError, OSError, KeyError, ET.ParseError) as error:
        print(f"Cannot export priorities: {error}", file=sys.stderr)
        sys.exit(1)
