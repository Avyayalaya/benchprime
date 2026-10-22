"""Canonical evaluation design, benchmark methods and audience-safe projections."""

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("legacy_design_validation", HERE / "validation.py")
O = load_module("collection_ontology", HERE / "collection.py")
load = V.load_json


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode("utf-8")).hexdigest()


def text_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def obj(**fields):
    return {"type": "object", "additionalProperties": False,
            "required": list(fields), "properties": fields}


def arr(item, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum}


def enum(*values):
    return {"enum": list(values)}


T = {"type": "string", "minLength": 1}
TEXTS = arr(T)
REFS = arr(T, 1)
NULLTEXT = {"type": ["string", "null"]}
INPUT = obj(context=obj(task=T, policy=REFS, tool_boundary=T),
            case=obj(request=T, observations={"type": "object"}))
EVIDENCE = obj(pointer=T, text=T, sha256=T)
EVIDENCE["properties"]["excerpt"] = obj(label=T, start={"type": "integer"}, end={"type": "integer"},
                                        text=T, explanation=T)
DIMENSION = obj(id=T, parent_id=NULLTEXT, label=T, definition=T)
WORLD = obj(id=T, provenance=enum("fictional", "permissioned", "public"), notes=T,
            facts=arr(obj(id=T, statement=T, basis=enum("source", "synthetic", "unknown"))),
            constraints=TEXTS)
CASE = obj(id=T, title=T, job_id=T, world_id=T, family_id=T,
           track=enum("diagnostic", "worklike", "representative", "reserved"),
           dimension_ids=REFS, input=INPUT, status=enum("reviewable", "blocked"))
CASE["properties"]["primary_dimension_ids"] = REFS
CRITERION = obj(id=T, case_id=T, dimension_ids=REFS, statement=T,
                role=enum("must", "preference", "diagnostic"), applicability=T,
                evidence=arr(EVIDENCE, 1), alternatives=T, consequence=T,
                review=enum("proposed", "author_reviewed", "independent_reviewed"),
                mode=enum("semantic", "deterministic", "conditional"))
CRITERION["properties"]["dimension_ids"] = TEXTS
CRITERION["properties"]["scope"] = enum("case", "shared")
ANCHOR = obj(id=T, case_id=T, kind=enum("competent", "alternative", "near_miss", "ambiguous"),
             response=T, annotations=arr(obj(criterion_id=T, verdict=enum("met", "not_met", "unresolved", "not_applicable"),
                                              reason=T), 1),
             provenance=enum("authored"), audience=enum("internal", "customer_example"))
CONTRAST = obj(a=T, b=T, changed_paths=REFS, expected_relation=T, invariants=T, limit=T)
FAMILY = obj(id=T, title=T, case_ids=REFS, mechanism=T, contrasts=arr(CONTRAST, 1))
FAMILY["properties"]["selection_reason"] = T
REQUIREMENT = obj(id=T, job_id=T, dimension_id=T, priority=enum("must", "important", "exploratory"))
COVERAGE = obj(requirement_id=T, status=enum("exposed", "gap", "excluded"), case_ids=TEXTS, reason=T)
CHECKS = ("source_links", "contrast_diffs", "criterion_links", "coverage_links", "boundary_projection")
APPLICATION = obj(pattern_id=T, version=T, pattern_hash=T,
                  disposition=enum("selected", "adapted", "excluded", "deferred"),
                  rationale=T, artifact_refs=TEXTS, check_ids=TEXTS)
CARD = obj(title=T, job=T, scope=T, excluded=TEXTS, limitations=TEXTS)
REVIEW = obj(status=enum("draft", "partial", "review_ready"), limitations=TEXTS,
             findings=arr(obj(id=T, severity=enum("blocking", "warning"), message=T)))
BRIEF = obj(document_type=enum("evaluation_design_brief"), schema_version=enum("2.0.0"),
            brief_id=T, target_kind=enum("agent", "llm_process"), job=T,
            instructions=T, policies=REFS, sources=arr(obj(id=T, text=T, rights=T)),
            excluded=TEXTS)
PACK = obj(document_type=enum("evaluation_design_pack"), schema_version=enum("2.0.0"),
           pack_id=T, brief_id=T, card=CARD, jobs=arr(obj(id=T, label=T), 1),
           dimensions=arr(DIMENSION, 1), worlds=arr(WORLD, 1), cases=arr(CASE, 1),
           families=arr(FAMILY), criteria=arr(CRITERION), anchors=arr(ANCHOR),
           requirements=arr(REQUIREMENT, 1), coverage=arr(COVERAGE, 1),
           pattern_bundle_hash=T, pattern_applications=arr(APPLICATION, 1),
           selection=arr(obj(origin_id=T, case_ids=TEXTS, decision=T, reason=T)),
           generation=obj(mode=enum("imported", "scripted", "fresh_context", "author_assisted"),
                          limitations=TEXTS, target_executed=enum(False)),
           review=REVIEW)
PACK["properties"]["collection"] = O.SCHEMA
SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "Evaluation design v2; structural subset, not semantic certification",
          "oneOf": [BRIEF, PACK]}

PATTERN_SEEDS = [
    ("BP-01", "Workload coverage", ["B03", "B15", "B20"], "Declare job/behavior exposure and omissions.", ["requirement", "coverage"], ["coverage_links"]),
    ("BP-02", "Evidence-backed criteria", ["B01", "B02", "B17"], "Bind criteria to visible source text or policy.", ["criterion"], ["source_links"]),
    ("BP-03", "Distinct quality properties", ["B14", "B16"], "Separate meaning, relevance and communication.", ["dimension"], ["criterion_links"]),
    ("BP-04", "Controlled contrasts", ["B04", "B19"], "Record actual edits and expected semantic relation.", ["family"], ["contrast_diffs"]),
    ("BP-05", "Coherent worlds", ["B04", "B13"], "Preserve world provenance and constraints across variants.", ["world", "case"], ["source_links"]),
    ("BP-06", "Atomic and composed work", ["B07", "B09"], "Separate diagnostic exposure from representative work.", ["case"], ["coverage_links"]),
    ("BP-07", "Local acceptance criteria", ["B10", "B16"], "State criterion applicability, alternatives and consequence.", ["criterion"], ["criterion_links"]),
    ("BP-08", "Equivalent valid solutions", ["B05", "B08", "B10"], "Accept different correct answers and preserve unaffected facts.", ["anchor"], ["criterion_links"]),
    ("BP-09", "Information boundaries", ["B02", "B09", "B10"], "Keep inputs separate from criteria and internal examples.", ["case"], ["boundary_projection"]),
    ("BP-10", "Observable output contract", ["B11", "B12", "B21"], "Make outcome and verification mode explicit.", ["criterion"], ["criterion_links"]),
    ("BP-11", "Versions and generalization", ["B08", "B13", "B18"], "Pin sources and reserve disjoint development worlds.", ["world"], ["source_links"]),
    ("BP-12", "Key and fixture review", ["B01", "B05", "B09"], "Expose author/reviewer limits and challenge the key.", ["anchor"], ["criterion_links"]),
    ("BP-13", "Separate reporting axes", ["B14", "B20", "B21"], "Keep priority, exposure and observed outcomes separate.", ["coverage"], ["coverage_links"]),
    ("BP-14", "Portable customer delivery", ["B06", "B09", "B15"], "Supply complete inputs and usable customer explanations.", ["case"], ["boundary_projection"]),
]


def catalogue():
    return load(HERE / "patterns" / "benchmark_patterns.json")


def validate_catalogue(bundle):
    require(set(bundle) == {"document_type", "version", "review", "source_ledger_hash", "source_index", "patterns"},
            "Invalid pattern bundle fields")
    require(bundle["document_type"] == "benchmark_pattern_bundle" and bundle["version"] == "1.0.0",
            "Unsupported pattern bundle")
    require(bundle["review"]["status"] == "internal_reviewed" and bundle["review"]["decision"],
            "Pattern bundle needs an internal review record")
    sources = index(bundle["source_index"])
    patterns = index(bundle["patterns"])
    require(set(patterns) == {row[0] for row in PATTERN_SEEDS}, "Catalogue pattern inventory mismatch")
    require({b for p in patterns.values() for b in p["benchmark_ids"]} == {f"B{i:02}" for i in range(1, 22)},
            "Catalogue must account for all 21 researched families")
    for pattern in patterns.values():
        require(pattern["status"] in ("internal_reviewed", "quarantined", "deprecated"), "Unknown pattern state")
        require(set(pattern["check_ids"]) <= set(CHECKS) and pattern["check_ids"], "Untrusted pattern check")
        require(pattern["source_ids"] and set(pattern["source_ids"]) <= set(sources), "Missing method provenance")
        require(pattern["hash"] == digest({k: v for k, v in pattern.items() if k != "hash"}), "Pattern hash mismatch")
        require(pattern["rights"] == "mechanism_reference_only", "Data/code reuse not authorized")
    return patterns


def index(rows, key="id"):
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), f"Duplicate {key}")
    return result


def pointer(value, path):
    require(path.startswith("/"), "Evidence must use a JSON pointer")
    for part in path[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            require(re.fullmatch(r"0|[1-9][0-9]*", part) is not None and int(part) < len(value),
                    "Invalid JSON pointer array index")
            value = value[int(part)]
        else:
            value = value[part]
    return value


def evidence(candidate, path):
    text = pointer(candidate, path)
    require(isinstance(text, str) and text, "Evidence pointer must identify nonempty text")
    return {"pointer": path, "text": text, "sha256": text_hash(text)}


def excerpt(candidate, path, quote, label, explanation):
    ref = evidence(candidate, path)
    require(quote and ref["text"].count(quote) == 1, "Excerpt must occur exactly once in its source")
    start = ref["text"].index(quote)
    ref["excerpt"] = {"label": label, "start": start, "end": start + len(quote),
                      "text": quote, "explanation": explanation}
    return ref


def validate(document, bundle=None):
    errors = V.check_schema(SCHEMA, document, SCHEMA)
    if errors:
        return errors
    try:
        if document["document_type"] == "evaluation_design_brief":
            index(document["sources"])
            return []
        require(isinstance(document, dict), "Expected object")
        patterns = validate_catalogue(bundle or catalogue())
        require(document["pattern_bundle_hash"] == digest(bundle or catalogue()), "Wrong pinned pattern bundle")
        dims, jobs, worlds, cases, families, criteria, anchors, requirements = (
            index(document[key]) for key in
            ("dimensions", "jobs", "worlds", "cases", "families", "criteria", "anchors", "requirements"))
        children = set()
        for dim in dims.values():
            current, seen = dim["id"], set()
            while current is not None:
                require(current in dims and current not in seen, "Dimension cycle/missing parent")
                seen.add(current)
                current = dims[current]["parent_id"]
            if dim["parent_id"]:
                children.add(dim["parent_id"])
        leaves = set(dims) - children
        for case in cases.values():
            require(case["world_id"] in worlds and case["job_id"] in jobs, "Case world/job missing")
            require(set(case["dimension_ids"]) <= leaves, "Case dimensions must be leaves")
            require(case["family_id"] in families and case["id"] in families[case["family_id"]]["case_ids"],
                    "Case family link missing")
            if "documents" in case["input"]["case"]["observations"]:
                docs = case["input"]["case"]["observations"]["documents"]
                require(isinstance(docs, list) and docs, "Documents must be a nonempty list")
                index(docs)
                require(all(set(d) == {"id", "title", "text"} and all(isinstance(v, str) and v for v in d.values())
                            for d in docs), "Invalid supplied document")
            require(all(not p.startswith("@source:") for p in case["input"]["context"]["policy"]),
                    "V2 policy must be fully resolved before candidate delivery")
        for family in families.values():
            require(len(set(family["case_ids"])) == len(family["case_ids"]) and set(family["case_ids"]) <= cases.keys(),
                    "Missing/duplicate family case")
            require(all(cases[c]["family_id"] == family["id"] for c in family["case_ids"]), "Cross-family membership")
            for contrast in family["contrasts"]:
                require(contrast["a"] != contrast["b"] and
                        {contrast["a"], contrast["b"]} <= set(family["case_ids"]), "Invalid contrast")
                actual = V.changed_paths(cases[contrast["a"]]["input"], cases[contrast["b"]]["input"])
                require(actual == set(contrast["changed_paths"]), "Contrast paths do not match inputs")
        for criterion in criteria.values():
            require(criterion["case_id"] in cases, "Criterion case missing")
            case = cases[criterion["case_id"]]
            require(set(criterion["dimension_ids"]) <= set(case["dimension_ids"]), "Criterion dimension mismatch")
            require(criterion["dimension_ids"] or criterion.get("scope") == "shared",
                    "Case-specific criterion needs a behavioral dimension")
            for ref in criterion["evidence"]:
                value = pointer(case["input"], ref["pointer"])
                require(isinstance(value, str) and value == ref["text"] and text_hash(value) == ref["sha256"],
                        f"Stale/wrong evidence text in {criterion['id']}")
                if "excerpt" in ref:
                    part = ref["excerpt"]
                    require(0 <= part["start"] < part["end"] <= len(value) and
                            value[part["start"]:part["end"]] == part["text"],
                            f"Stale or out-of-bounds evidence excerpt in {criterion['id']}")
        for anchor in anchors.values():
            require(anchor["case_id"] in cases, "Anchor case missing")
            annotations = index(anchor["annotations"], "criterion_id")
            expected = {c["id"] for c in criteria.values() if c["case_id"] == anchor["case_id"]}
            require(set(annotations) == expected, "Anchor must account for all case criteria")
            verdicts = {a["verdict"] for a in annotations.values()}
            require(anchor["kind"] not in ("competent", "alternative") or
                    verdicts <= {"met", "not_applicable"} and "met" in verdicts,
                    "Competent anchor contradicts its annotations")
            require(anchor["kind"] != "near_miss" or "not_met" in verdicts, "Near miss without an unmet criterion")
        coverage = index(document["coverage"], "requirement_id")
        require(set(coverage) == set(requirements), "Coverage must account for every requirement")
        for req in requirements.values():
            require(req["job_id"] in jobs and req["dimension_id"] in leaves, "Invalid workload requirement")
            row = coverage[req["id"]]
            require(set(row["case_ids"]) <= set(cases), "Coverage references missing case")
            if row["status"] == "exposed":
                require(row["case_ids"] and all(cases[c]["job_id"] == req["job_id"] and
                        req["dimension_id"] in cases[c]["dimension_ids"] and cases[c]["status"] == "reviewable"
                        for c in row["case_ids"]), "False coverage claim")
        groups = {"dimension": dims, "world": worlds, "case": cases, "family": families,
                  "criterion": criteria, "anchor": anchors, "requirement": requirements, "coverage": coverage}
        applications = index(document["pattern_applications"], "pattern_id")
        require(set(applications) == set(patterns), "Every catalogue pattern needs a disposition")
        for application in applications.values():
            pattern = patterns[application["pattern_id"]]
            require(application["pattern_hash"] == pattern["hash"] and application["version"] == pattern["version"],
                    "Unpinned pattern application")
            if application["disposition"] in ("selected", "adapted"):
                require(pattern["status"] == "internal_reviewed", "Unusable pattern selected")
                require(set(application["check_ids"]) == set(pattern["check_ids"]), "Pattern check obligation missing")
                kinds = set()
                for ref in application["artifact_refs"]:
                    kind, key = ref.split(":", 1)
                    require(kind in groups and key in groups[kind], "Pattern artifact reference missing")
                    kinds.add(kind)
                require(set(pattern["artifact_kinds"]) <= kinds, "Citation alone does not fulfill a pattern")
                if pattern["id"] == "BP-05":
                    linked_worlds = [worlds[r.split(":", 1)[1]] for r in application["artifact_refs"] if r.startswith("world:")]
                    require(all(w["facts"] and w["constraints"] for w in linked_worlds),
                            "Parameterized-world pattern requires actual facts and constraints")
        index(document["selection"], "origin_id")
        require(all(set(row["case_ids"]) <= set(cases) for row in document["selection"]), "Selection reference missing")
        review = document["review"]
        index(review["findings"])
        if review["status"] == "review_ready":
            require(not any(f["severity"] == "blocking" for f in review["findings"]), "Blocking review finding")
            require(all(row["status"] != "gap" for row in document["coverage"]), "Unresolved coverage")
            require(all(c["status"] == "reviewable" for c in cases.values()), "Blocked case")
            for case in cases.values():
                case_criteria = [c for c in criteria.values() if c["case_id"] == case["id"]]
                require(case_criteria and all(c["review"] != "proposed" for c in case_criteria), "Unreviewed case criteria")
                require(any(a["case_id"] == case["id"] and a["kind"] == "competent" for a in anchors.values()),
                        "Case lacks reviewed illustrative competent response")
        if "collection" in document:
            O.validate(document)
        return []
    except (ValueError, KeyError, IndexError, TypeError) as error:
        return [str(error)]


def checked(pack, bundle=None):
    errors = validate(pack, bundle)
    require(not errors, "\n".join(errors))
    return pack


def project(pack):
    """Only explicit customer fields; creator provenance and anchors stay internal."""
    checked(pack)
    result = {
        "pack_id": pack["pack_id"], "pack_hash": digest(pack), "card": copy.deepcopy(pack["card"]),
        "dimensions": copy.deepcopy(pack["dimensions"]), "coverage": copy.deepcopy(pack["coverage"]),
        "families": copy.deepcopy(pack["families"]),
        "requirements": copy.deepcopy(pack["requirements"]), "jobs": copy.deepcopy(pack["jobs"]),
        "cases": [{**{k: copy.deepcopy(case[k]) for k in
                      ("id", "title", "family_id", "track", "dimension_ids", "input", "status")},
                   "primary_dimension_ids": copy.deepcopy(case.get("primary_dimension_ids", case["dimension_ids"])),
                   "criteria": [{**{k: copy.deepcopy(c[k]) for k in
                                 ("id", "statement", "role", "applicability", "evidence", "alternatives", "consequence", "mode", "review")},
                                 "scope": c.get("scope", "case")}
                                for c in pack["criteria"] if c["case_id"] == case["id"]],
                   "examples": [{k: copy.deepcopy(a[k]) for k in ("id", "response", "kind", "annotations", "provenance")}
                                for a in pack["anchors"] if a["case_id"] == case["id"] and a["audience"] == "customer_example"]}
                  for case in pack["cases"]],
        "status": pack["review"]["status"],
        "limitations": list(dict.fromkeys(pack["card"]["limitations"] + pack["generation"]["limitations"] +
                                          pack["review"]["limitations"])),
        "target_executed": False, "scores": None,
    }
    if "collection" in pack:
        result["collection"] = O.project(pack)
    return result


def candidates(pack):
    checked(pack)
    return [{"case_id": c["id"], "input": copy.deepcopy(c["input"])}
            for c in pack["cases"] if c["status"] == "reviewable" and c["track"] != "reserved"]


def customer_profile(pack, overrides):
    checked(pack)
    roots = [d["id"] for d in pack["dimensions"] if d["parent_id"] is None]
    require(set(overrides) == set(roots), "Profile must name exactly the pack's root dimensions")
    require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in overrides.values()),
            "Priorities must be finite nonnegative numbers")
    total = sum(overrides.values())
    require(math.isfinite(total) and total > 0, "Choose at least one positive priority")
    return {"document_type": "evaluation_customer_profile", "pack_hash": digest(pack),
            "overrides": overrides, "normalized": {k: v / total for k, v in overrides.items()},
            "meaning": "Customer importance preferences only; no target score or source change"}


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as out:
        out.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def build_catalogue(ledger):
    benchmarks = index(ledger["selection"]["families"])
    sources = index(ledger["sources"])
    patterns = []
    for pid, name, bids, mechanism, kinds, checks in PATTERN_SEEDS:
        p = {"id": pid, "version": "1.0.0", "name": name, "benchmark_ids": bids,
             "source_ids": sorted({sid for bid in bids for sid in benchmarks[bid]["source_ids"]}),
             "mechanism": mechanism, "eligibility": "Apply only where this mechanism addresses the declared job; otherwise exclude with rationale.",
             "non_transfer": "No external dataset, grading formula, task authority or execution capability is imported.",
             "artifact_kinds": kinds, "check_ids": checks, "rights": "mechanism_reference_only",
             "status": "internal_reviewed", "review_limit": "Author-curated from primary-source research; not independent certification"}
        p["hash"] = digest(p)
        patterns.append(p)
    bundle = {"document_type": "benchmark_pattern_bundle", "version": "1.0.0",
              "review": {"status": "internal_reviewed", "decision": "Author-curated mechanism references; source research retained",
                         "independent": False},
              "source_ledger_hash": digest(ledger),
              "source_index": [{k: s[k] for k in ("id", "url", "title", "access", "inspected", "version_scope", "commit", "sha256") if k in s}
                               for s in sources.values()],
              "patterns": patterns}
    validate_catalogue(bundle)
    return bundle


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    args = parser.parse_args()
    try:
        checked(load(args.pack))
        print("V2 structure, references and declared method obligations checked; semantic/human acceptance not inferred.")
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
