"""Offline commands for preparing, checking and using evaluation definitions."""

import argparse
import copy
import json
from pathlib import Path
import sys

from . import contracts as C
from . import design as D
from . import render as R
from . import onboarding

ROOT = Path(__file__).resolve().parent.parent


def output_new(path, text):
    path = path.resolve()
    D.require(not path.is_relative_to((ROOT / "packs").resolve()),
              "Write outside the bundled packs directory; keep example versions immutable")
    D.require(not path.exists(), "Output already exists; choose a new filename")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def checked_pack(path):
    pack = D.checked(D.load(path))
    D.require(pack["document_type"] == "evaluation_design_pack", "This command needs an evaluation pack")
    D.require("collection" in pack, "The guided workflow requires a collection-first design")
    return pack


def prepare(draft):
    D.require(isinstance(draft, dict), "An evaluation draft must be a JSON object")
    pack = copy.deepcopy(draft)
    D.require(pack.get("document_type") == "evaluation_design_pack", "Prepare an evaluation pack draft")
    bound = 0

    def bind(obj, key, value):
        nonlocal bound
        if key in obj:
            D.require(obj[key] == value, "Supplied " + key + " disagrees with its source; revise the draft")
        else:
            obj[key] = value
            bound += 1

    bundle = D.catalogue()
    bind(pack, "pattern_bundle_hash", D.digest(bundle))
    bind(pack["collection"], "catalog_hash", D.digest(D.O.catalog()))
    deferred = 0
    if "pattern_applications" not in pack:
        D.require(pack["review"]["status"] in ("draft", "partial"),
                  "Unassessed methods cannot be prepared as review_ready")
        pack["pattern_applications"] = [{
            "pattern_id": pattern["id"], "version": pattern["version"], "pattern_hash": pattern["hash"],
            "disposition": "deferred", "rationale": "Not assessed in this guided draft; review explicitly.",
            "artifact_refs": [], "check_ids": []
        } for pattern in bundle["patterns"]]
        deferred = len(pack["pattern_applications"])
    cases = D.index(pack["cases"])
    for criterion in pack["criteria"]:
        candidate = cases[criterion["case_id"]]["input"]
        for ref in criterion["evidence"]:
            source = D.evidence(candidate, ref["pointer"])
            bind(ref, "text", source["text"])
            bind(ref, "sha256", source["sha256"])
            if "excerpt" in ref:
                part = ref["excerpt"]
                if "start" not in part or "end" not in part:
                    quote = part["text"]
                    D.require(bool(quote) and ref["text"].count(quote) == 1,
                              "An excerpt without offsets must occur exactly once")
                    start = ref["text"].index(quote)
                    bind(part, "start", start)
                    bind(part, "end", start + len(quote))
    D.checked(pack)
    return pack, bound, deferred


def references(brief):
    C.checked_brief(brief)
    pointers = ["/target/instructions"]
    for group in ("sources", "target_policies", "preferences", "creator_constraints", "examples", "scope_exclusions"):
        pointers.extend(f"/{group}/{i}" + ("/text" if group == "sources" else "")
                        for i in range(len(brief[group])))
    rows = []
    for pointer in pointers:
        text, authority = C.resolve_text(brief, pointer)
        if text.strip():
            rows.append({"handle": f"REF-{len(rows)+1:03}", "authority": authority,
                         "reference": C.reference(brief, pointer)})
    return {"brief_sha256": brief["brief_sha256"], "references": rows}


def parser():
    root = argparse.ArgumentParser(prog="benchprime", description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "inspect", "prepare", "export", "render", "freeze", "references"):
        command = commands.add_parser(name)
        command.add_argument("document", type=Path)
        if name in ("prepare", "export", "render", "freeze", "references"):
            command.add_argument("--output", type=Path, required=True)
        if name == "export":
            selection = command.add_mutually_exclusive_group()
            selection.add_argument("--case-number", type=int)
            selection.add_argument("--case-id")
    commands.add_parser("catalog")
    start = commands.add_parser("start", help="Create a task workspace and assistant kickoff; no model call")
    start.add_argument("directory", type=Path)
    source = start.add_mutually_exclusive_group()
    source.add_argument("--task", type=Path)
    source.add_argument("--from-intake", type=Path)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            result = onboarding.start(args.directory, args.task, args.from_intake)
        elif args.command == "catalog":
            result = {"patterns": D.catalogue(), "principles": D.O.catalog()}
        elif args.command == "freeze":
            brief = C.freeze_brief(D.load(args.document))
            output_new(args.output, json_text(brief))
            result = {"status": "frozen", "brief_sha256": brief["brief_sha256"],
                      "sources": len(brief["sources"]), "provider_calls": 0}
        elif args.command == "references":
            catalog = references(D.load(args.document))
            output_new(args.output, json_text(catalog))
            result = {"status": "bound", "references": len(catalog["references"]), "provider_calls": 0}
        elif args.command == "prepare":
            pack, bound, deferred = prepare(D.load(args.document))
            output_new(args.output, json_text(pack))
            result = {"status": "prepared", "bound_fields": bound, "deferred_patterns": deferred,
                      "review_status": pack["review"]["status"], "semantic_certification": False}
        elif args.command == "validate":
            document = D.load(args.document)
            D.require(isinstance(document, dict), "A document must be a JSON object")
            if document.get("document_type") == "repeatability_brief":
                C.checked_brief(document)
            else:
                D.checked(document)
                if document["document_type"] == "evaluation_design_pack":
                    D.require("collection" in document, "Collection-first metadata is required")
            result = {"status": "structurally_valid", "semantic_certification": False, "target_executed": False}
        else:
            pack = checked_pack(args.document)
            if args.command == "inspect":
                result = {"pack_id": pack["pack_id"], "cases": len(pack["cases"]),
                          "criteria": len(pack["criteria"]), "categories": len(pack["collection"]["categories"]),
                          "themes": len(pack["collection"]["themes"]), "scenario_groups": len(pack["families"]),
                          "requirements_exposed": sum(r["status"] == "exposed" for r in pack["coverage"]),
                          "gaps": sum(r["status"] == "gap" for r in pack["coverage"]),
                          "review_status": pack["review"]["status"], "target_executed": False}
            elif args.command == "render":
                output_new(args.output, R.render_html(D.project(pack), standalone_inputs=D.candidates(pack)))
                result = {"status": "rendered", "format": "html", "target_executed": False}
            else:
                rows = D.candidates(pack)
                case_id = args.case_id
                if args.case_number is not None:
                    D.require(1 <= args.case_number <= len(pack["cases"]), "Case number is outside this pack")
                    case_id = pack["cases"][args.case_number - 1]["id"]
                if case_id:
                    row = next((r for r in rows if r["case_id"] == case_id), None)
                    D.require(row is not None, "Unknown, blocked or reserved case")
                    output_new(args.output, json_text(row))
                    count = 1
                else:
                    output_new(args.output, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
                    count = len(rows)
                result = {"status": "exported", "cases": count, "target_executed": False}
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1
