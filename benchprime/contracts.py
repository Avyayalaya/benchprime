"""Offline, opt-in source/authority compiler. No inference or target execution."""

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
VERSION = "3.0.0"
spec = importlib.util.spec_from_file_location("repeatability_validation", HERE / "validation.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def obj(**fields):
    return {"type": "object", "additionalProperties": False, "required": list(fields), "properties": fields}


def arr(item, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum}


def enum(*values):
    return {"enum": list(values)}


T = {"type": "string", "minLength": 1}
NULL = {"type": "null"}
INT = {"type": "integer"}
TEXTS = arr(T)
AUTHORITY = obj(kind=enum("normative", "descriptive", "unknown"), basis=T)
RIGHTS = obj(status=enum("granted", "unknown", "denied"), basis=T)
TARGET = obj(job=T, instructions=T, input_shape={"type": ["string", "null"]},
             output_shape={"type": ["string", "null"]}, language=enum("en"))
SOURCE = obj(source_id=T, title=T, text=T,
             role=enum("policy", "evidence", "example", "implementation_description"),
             authority=AUTHORITY, provenance=enum("fictional", "public", "permissioned"), rights=RIGHTS)
INTAKE = obj(document_type=enum("repeatability_intake"), schema_version=enum(VERSION),
             brief_id=T, revision=T, target=TARGET, sources=arr(SOURCE, 1),
             target_policies=TEXTS, preferences=TEXTS, creator_constraints=TEXTS,
             examples=TEXTS, scope_exclusions=TEXTS, rights=RIGHTS)
BRIEF = copy.deepcopy(INTAKE)
BRIEF["properties"]["document_type"] = enum("repeatability_brief")
BRIEF["properties"]["sources"]["items"]["properties"]["sha256"] = T
BRIEF["properties"]["sources"]["items"]["required"].append("sha256")
BRIEF["properties"]["brief_sha256"] = T
BRIEF["required"].append("brief_sha256")
REF = obj(pointer=T, start=INT, end=INT, text=T, sha256=T)
CLAIM = obj(local_key=T, statement=T, source_refs=arr(REF, 1))
INVENTORY = obj(document_type=enum("requirement_inventory"), schema_version=enum(VERSION),
                brief_sha256=T, role=enum("profile", "challenge"), source_ids=TEXTS, items=arr(CLAIM, 1))
CLAIM_LINK = obj(role=enum("profile", "challenge"), local_key=T)
REQ = obj(condition=T, observable_outcome=T, modality=enum("must", "preference"),
          severity=enum("critical", "major", "minor"), authority_refs=arr(REF, 1))
ROUTE = obj(claims=arr(CLAIM_LINK, 1), disposition=enum("target", "creator_only", "evidence", "unknown", "excluded"),
            reason=T, requirement={"oneOf": [REQ, NULL]}, exclusion_ref={"oneOf": [REF, NULL]})
RESOLUTION = obj(winner=INT, actor=T, decision_ref=T, reason=T)
CONFLICT = obj(refs=arr(REF, 2), effect=T, question=T, resolution={"oneOf": [RESOLUTION, NULL]})
REVIEWER = obj(actor=T, decision_ref=T, kind=enum("human", "operator", "model", "fixture"),
               semantic_review=enum("reviewed", "unreviewed"))
ASSUMPTION = obj(statement=T, effect=T, status=enum("confirmed", "unresolved"), decision_ref={"type": ["string", "null"]})
REVIEW = obj(document_type=enum("inventory_review"), schema_version=enum(VERSION), brief_sha256=T,
             inventory_hashes=obj(profile=T, challenge=T), reviewer=REVIEWER,
             routes=arr(ROUTE, 1), conflicts=arr(CONFLICT), assumptions=arr(ASSUMPTION))
SELECTION = obj(document_type=enum("projection_selection"), schema_version=enum(VERSION),
                contract_sha256=T, unit_id=T, requirement_ids=arr(T, 1),
                passages=arr(obj(ref=REF, reason=T)),
                omissions=arr(obj(source_id=T, reason=T)))
FINAL_REQ = obj(id=T, job_id=T, condition=T, observable_outcome=T,
                modality=enum("must", "preference"), severity=enum("critical", "major", "minor"),
                authority_refs=arr(REF, 1), source_refs=arr(REF, 1), claim_ids=arr(T, 1))
SOURCE_RECORD = copy.deepcopy(SOURCE)
del SOURCE_RECORD["properties"]["text"]
SOURCE_RECORD["required"].remove("text")
SOURCE_RECORD["properties"]["sha256"] = T
SOURCE_RECORD["required"].append("sha256")
SOURCE_RECORD["properties"]["reported_by"] = arr(enum("profile", "challenge"), 2)
SOURCE_RECORD["required"].append("reported_by")
FINAL_CLAIM = obj(id=T, role=enum("profile", "challenge"), local_key=T, statement=T, source_refs=arr(REF, 1))
FINAL_ROUTE = obj(id=T, claim_ids=arr(T, 1), disposition=ROUTE["properties"]["disposition"],
                  reason=T, requirement_id={"type": ["string", "null"]}, exclusion_ref={"oneOf": [REF, NULL]})
FINAL_CONFLICT = copy.deepcopy(CONFLICT)
FINAL_CONFLICT["properties"]["id"] = T
FINAL_CONFLICT["required"].append("id")
CONTRACT = obj(document_type=enum("task_contract"), schema_version=enum(VERSION), brief_id=T, revision=T,
               brief_sha256=T, contract_sha256=T, job_id=T, target=TARGET,
               target_requirements=arr(FINAL_REQ), creator_constraints=TEXTS,
               source_inventory=arr(SOURCE_RECORD, 1), claims=arr(FINAL_CLAIM, 2),
               routing=arr(FINAL_ROUTE, 1), conflicts=arr(FINAL_CONFLICT), assumptions=arr(ASSUMPTION),
               review=REVIEWER, input_hashes=obj(profile=T, challenge=T, review=T),
               readiness=obj(status=enum("ready", "partial", "needs_input"), reasons=TEXTS, questions=TEXTS),
               limitations=TEXTS, execution_authorized=enum(False))
PASSAGE = obj(source_id=T, title=T, role=SOURCE["properties"]["role"], authority=AUTHORITY,
              provenance=SOURCE["properties"]["provenance"], rights=RIGHTS,
              source_sha256=T, start=INT, end=INT, text=T, reason=T)
OMITTED = obj(source_id=T, start=INT, end=INT, reason=T)
PROJECTION = obj(document_type=enum("evidence_projection"), schema_version=enum(VERSION),
                 projection_sha256=T, brief_sha256=T, contract_sha256=T, selection_sha256=T,
                 unit_id=T, requirement_ids=arr(T, 1),
                 payload=obj(target=TARGET, target_policies=TEXTS, preferences=TEXTS,
                             target_requirements=arr(FINAL_REQ, 1), sources=arr(PASSAGE),
                             authority_decisions=arr(obj(conflict_id=T, refs=arr(REF, 2), winner=INT, reason=T))),
                 omissions=arr(OMITTED), limitations=TEXTS, execution_authorized=enum(False))
SCHEMAS = {s["properties"]["document_type"]["enum"][0]: s
           for s in (INTAKE, BRIEF, INVENTORY, REVIEW, SELECTION, CONTRACT, PROJECTION)}
SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "Repeatability D1: declared authority and exact provenance, not semantic certification",
          "oneOf": list(SCHEMAS.values())}
V.audit_schema(SCHEMA)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode("utf-8")).hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def without_hash(value, key):
    return {k: v for k, v in value.items() if k != key}


def typed_id(prefix, namespace, unit, local):
    require(prefix in ("CLM", "REQ", "JOB", "RTE", "CFL"), "Unknown ID type")
    return prefix + "-" + digest([namespace, unit, local])


def checked_shape(value, kind):
    errors = V.check_schema(SCHEMAS[kind], value, SCHEMA)
    require(not errors, "\n".join(errors))

    def text_check(node):
        if isinstance(node, str):
            require(bool(node.strip()), "Whitespace-only text is not a usable value")
            node.encode("utf-8")
        elif isinstance(node, dict):
            for child in node.values():
                text_check(child)
        elif isinstance(node, list):
            for child in node:
                text_check(child)
    text_check(value)


def unique(values, label):
    require(len(values) == len(set(values)), f"Duplicate {label}")
    return set(values)


def check_brief_fields(brief):
    unique([s["source_id"] for s in brief["sources"]], "source IDs")
    for source in brief["sources"]:
        require(source["authority"]["kind"] != "normative" or source["role"] == "policy",
                "Only a declared policy source may have normative authority")
    for field in ("target_policies", "preferences", "creator_constraints", "examples", "scope_exclusions"):
        unique(brief[field], field)


def freeze_brief(intake):
    checked_shape(intake, "repeatability_intake")
    check_brief_fields(intake)
    brief = copy.deepcopy(intake)
    brief["document_type"] = "repeatability_brief"
    for source in brief["sources"]:
        source["sha256"] = text_hash(source["text"])
    brief["brief_sha256"] = digest(brief)
    checked_brief(brief)
    return brief


def checked_brief(brief):
    checked_shape(brief, "repeatability_brief")
    check_brief_fields(brief)
    for source in brief["sources"]:
        require(source["sha256"] == text_hash(source["text"]), "Stale source hash")
    require(brief["brief_sha256"] == digest(without_hash(brief, "brief_sha256")), "Stale brief hash")
    return brief


def resolve_text(brief, pointer):
    if pointer == "/target/instructions":
        return brief["target"]["instructions"], {"kind": "normative", "source_id": None}
    match = re.fullmatch(r"/(sources|target_policies|preferences|creator_constraints|examples|scope_exclusions)/(0|[1-9][0-9]*)(/text)?", pointer)
    require(match is not None, "Reference pointer outside permitted text fields")
    group, number, suffix = match.groups()
    require((group == "sources") == (suffix == "/text"), "Noncanonical text pointer")
    index = int(number)
    require(index < len(brief[group]), "Reference index out of bounds")
    if group == "sources":
        source = brief[group][index]
        return source["text"], {"kind": source["authority"]["kind"], "source_id": source["source_id"]}
    kind = {"target_policies": "normative", "preferences": "preference",
            "creator_constraints": "creator", "examples": "descriptive", "scope_exclusions": "exclusion"}[group]
    return brief[group][index], {"kind": kind, "source_id": None}


def reference(brief, pointer, start=0, end=None):
    checked_brief(brief)
    text, _ = resolve_text(brief, pointer)
    end = len(text) if end is None else end
    require(type(start) is int and type(end) is int and 0 <= start < end <= len(text), "Invalid evidence offsets")
    return {"pointer": pointer, "start": start, "end": end, "text": text[start:end], "sha256": text_hash(text)}


def checked_ref(brief, ref):
    errors = V.check_schema(REF, ref, SCHEMA)
    require(not errors, "\n".join(errors))
    text, info = resolve_text(brief, ref["pointer"])
    require(0 <= ref["start"] < ref["end"] <= len(text), "Invalid evidence offsets")
    require(ref["text"] == text[ref["start"]:ref["end"]] and bool(ref["text"].strip()),
            "Evidence quote does not match the exact source span")
    require(ref["sha256"] == text_hash(text), "Evidence source hash mismatch")
    return info


def dedupe_refs(refs):
    return list({encoded(r): r for r in refs}.values())


def overlap(a, b):
    return a["pointer"] == b["pointer"] and a["start"] < b["end"] and b["start"] < a["end"]


def compile_contract(brief, profile, challenge, review):
    checked_brief(brief)
    checked_shape(review, "inventory_review")
    require(review["brief_sha256"] == brief["brief_sha256"], "Review brief hash mismatch")
    namespace = brief["brief_sha256"]
    source_ids = {s["source_id"] for s in brief["sources"]}
    claims, lookup = [], {}
    for role, inventory in (("profile", profile), ("challenge", challenge)):
        checked_shape(inventory, "requirement_inventory")
        require(inventory["role"] == role, "Inventory role mismatch")
        require(inventory["brief_sha256"] == namespace, "Inventory brief hash mismatch")
        require(review["inventory_hashes"][role] == digest(inventory), "Reviewed inventory hash mismatch")
        require(unique(inventory["source_ids"], "reported source IDs") == source_ids,
                f"{role} must account for every supplied source ID")
        unique([i["local_key"] for i in inventory["items"]], f"{role} local keys")
        for index, item in enumerate(inventory["items"]):
            for ref in item["source_refs"]:
                checked_ref(brief, ref)
            claim = {"id": typed_id("CLM", namespace, role, index), "role": role, **copy.deepcopy(item)}
            claims.append(claim)
            lookup[(role, item["local_key"])] = claim
    cited = {ref["pointer"] for claim in claims for ref in claim["source_refs"]}
    for group in ("target_policies", "preferences", "creator_constraints"):
        require(all(f"/{group}/{i}" in cited for i in range(len(brief[group]))),
                f"Inventories omit explicit {group}")

    requirements, routing, routed = [], [], set()
    questions, reasons = [], []
    job_id = typed_id("JOB", namespace, "target", 0)
    for route in review["routes"]:
        keys = [(link["role"], link["local_key"]) for link in route["claims"]]
        require(len(keys) == len(set(keys)) and not routed.intersection(keys), "Claim routed more than once")
        require(set(keys) <= set(lookup), "Unknown claim in routing")
        routed.update(keys)
        inputs = [lookup[key] for key in keys]
        ids = sorted(c["id"] for c in inputs)
        refs = dedupe_refs([r for c in inputs for r in c["source_refs"]])
        kinds = {checked_ref(brief, ref)["kind"] for ref in refs}
        disposition = route["disposition"]
        requirement = route["requirement"]
        exclusion = route["exclusion_ref"]
        rid = None
        require((disposition == "target") == (requirement is not None), "Only target routes may have a requirement")
        require((disposition == "excluded") == (exclusion is not None), "Excluded route needs explicit exclusion reference")
        if "creator" in kinds:
            require(kinds == {"creator"} and disposition == "creator_only",
                    "A creator claim cannot be merged or promoted into target behavior")
        if disposition == "creator_only":
            require(kinds == {"creator"}, "creator_only route must cite creator constraints")
        if disposition == "evidence":
            require(kinds <= {"descriptive"}, "Normative/unknown claims cannot be silently routed as evidence")
        if "unknown" in kinds:
            require(disposition == "unknown", "Unknown source authority must remain an unresolved claim")
        if disposition == "excluded":
            require(checked_ref(brief, exclusion)["kind"] == "exclusion", "Invalid exclusion authority")
        if disposition == "unknown":
            questions.append(route["reason"])
            reasons.append("unresolved_inventory_claim")
        if requirement is not None:
            require("creator" not in kinds and "exclusion" not in kinds, "Non-target basis in target route")
            require(requirement["modality"] != "must" or "preference" not in kinds,
                    "A preference cannot be promoted to mandatory behavior")
            allowed = {"normative"} if requirement["modality"] == "must" else {"normative", "preference"}
            require(all(checked_ref(brief, ref)["kind"] in allowed for ref in requirement["authority_refs"]),
                    "Requirement has no permitted normative/preference authority")
            rid = typed_id("REQ", namespace, "requirement", ids)
            requirements.append({"id": rid, "job_id": job_id, **copy.deepcopy(requirement),
                                 "source_refs": copy.deepcopy(dedupe_refs(refs + requirement["authority_refs"])),
                                 "claim_ids": ids})
        routing.append({"id": typed_id("RTE", namespace, "route", ids), "claim_ids": ids,
                        "disposition": disposition, "reason": route["reason"], "requirement_id": rid,
                        "exclusion_ref": copy.deepcopy(exclusion)})
    require(routed == set(lookup), "Every inventory claim must have exactly one routing disposition")
    conflicts = []
    for index, conflict in enumerate(review["conflicts"]):
        for ref in conflict["refs"]:
            require(checked_ref(brief, ref)["kind"] not in ("creator", "exclusion"),
                    "Authority conflict cannot promote creator/exclusion text")
        unique([encoded(ref) for ref in conflict["refs"]], "conflict evidence")
        resolution = conflict["resolution"]
        if resolution is None:
            questions.append(conflict["question"])
            reasons.append("unresolved_authority_conflict")
        else:
            winner = resolution["winner"]
            require(0 <= winner < len(conflict["refs"]), "Conflict winner out of bounds")
            require(checked_ref(brief, conflict["refs"][winner])["kind"] == "normative",
                    "Conflict resolution cannot promote descriptive data to authority")
            losers = [r for i, r in enumerate(conflict["refs"]) if i != winner]
            require(not any(overlap(ref, lost) for req in requirements for ref in req["authority_refs"] for lost in losers),
                    "Requirement still uses rejected conflict authority")
        conflicts.append({"id": typed_id("CFL", namespace, "conflict", index), **copy.deepcopy(conflict)})
    for assumption in review["assumptions"]:
        if assumption["status"] == "unresolved":
            reasons.append("unresolved_assumption")
            questions.append(assumption["effect"])
        else:
            require(assumption["decision_ref"] is not None and assumption["decision_ref"].strip(),
                    "Confirmed assumption requires a decision reference")
    for name in ("input_shape", "output_shape"):
        if brief["target"][name] is None:
            reasons.append("missing_target_" + name)
            questions.append(f"Specify the target's {name}; creator output formats cannot fill this field.")
    for label, rights in [("brief", brief["rights"])] + [(s["source_id"], s["rights"]) for s in brief["sources"]]:
        if rights["status"] != "granted":
            reasons.append("source_permission_not_granted")
            questions.append(f"Permission for {label} is {rights['status']}; provide permitted material or explicit rights.")
    if not requirements:
        reasons.append("no_target_requirements")
        questions.append("Supply a supported target requirement; creator-only work is not an evaluation task.")
    status = "needs_input" if reasons else "ready"
    if review["reviewer"]["semantic_review"] != "reviewed":
        reasons.append("semantic_review_not_recorded")
        if status == "ready":
            status = "partial"
    for label, records in (("claim IDs", claims), ("requirement IDs", requirements),
                           ("route IDs", routing), ("conflict IDs", conflicts)):
        unique([row["id"] for row in records], label)
    result = {
        "document_type": "task_contract", "schema_version": VERSION,
        "brief_id": brief["brief_id"], "revision": brief["revision"], "brief_sha256": namespace,
        "job_id": job_id, "target": copy.deepcopy(brief["target"]),
        "target_requirements": requirements, "creator_constraints": copy.deepcopy(brief["creator_constraints"]),
        "source_inventory": [{**{k: copy.deepcopy(v) for k, v in source.items() if k != "text"},
                              "reported_by": ["profile", "challenge"]} for source in brief["sources"]],
        "claims": claims, "routing": routing, "conflicts": conflicts,
        "assumptions": copy.deepcopy(review["assumptions"]), "review": copy.deepcopy(review["reviewer"]),
        "input_hashes": {"profile": digest(profile), "challenge": digest(challenge), "review": digest(review)},
        "readiness": {"status": status, "reasons": list(dict.fromkeys(reasons)),
                      "questions": list(dict.fromkeys(questions))},
        "limitations": [
            "D1 compiles explicitly supplied inventories and review decisions; it does not extract semantics or discover every contradiction.",
            "Hashes prove input binding, not truth, entitlement or authenticated approval. Source roles and reviewer decisions are trusted local declarations.",
            "Ready means structurally compiled with a recorded review, not an evaluated pack, human acceptance, prompt-injection resistance or execution permission."
        ], "execution_authorized": False
    }
    result["contract_sha256"] = digest(result)
    checked_shape(result, "task_contract")
    return result


def checked_contract(contract, brief):
    checked_brief(brief)
    checked_shape(contract, "task_contract")
    require(contract["brief_sha256"] == brief["brief_sha256"], "Contract brief hash mismatch")
    require(contract["contract_sha256"] == digest(without_hash(contract, "contract_sha256")), "Contract hash mismatch")
    require(contract["target"] == brief["target"] and contract["creator_constraints"] == brief["creator_constraints"],
            "Contract governing fields changed")
    for claim in contract["claims"]:
        for ref in claim["source_refs"]:
            checked_ref(brief, ref)
    for req in contract["target_requirements"]:
        for ref in req["source_refs"] + req["authority_refs"]:
            checked_ref(brief, ref)
    unique([r["id"] for r in contract["target_requirements"]], "requirement IDs")
    return contract


def verify_contract(contract, brief, profile, challenge, review):
    checked_contract(contract, brief)
    require(contract == compile_contract(brief, profile, challenge, review),
            "Contract differs from exact recompilation of its reviewed inputs")
    return contract


def build_projection(brief, contract, selection):
    checked_contract(contract, brief)
    checked_shape(selection, "projection_selection")
    require(contract["readiness"]["status"] == "ready", "Contract is not ready for projection")
    require(selection["contract_sha256"] == contract["contract_sha256"], "Selection contract hash mismatch")
    requirements = {r["id"]: r for r in contract["target_requirements"]}
    selected_ids = unique(selection["requirement_ids"], "selected requirement IDs")
    require(selected_ids <= set(requirements), "Unknown selected requirement")
    sources = {s["source_id"]: s for s in brief["sources"]}
    ranges, included = {}, []
    for item in selection["passages"]:
        ref = item["ref"]
        info = checked_ref(brief, ref)
        sid = info["source_id"]
        require(sid is not None, "Projected passages must reference raw source text")
        require(sources[sid]["rights"]["status"] == "granted", "Projected source permission is not granted")
        intervals = ranges.setdefault(sid, [])
        require(not any(ref["start"] < end and start < ref["end"] for start, end in intervals),
                "Duplicate or overlapping projected passages")
        intervals.append((ref["start"], ref["end"]))
        source = sources[sid]
        included.append({k: copy.deepcopy(source[k]) for k in ("source_id", "title", "role", "authority", "provenance", "rights")})
        included[-1].update(source_sha256=source["sha256"], start=ref["start"], end=ref["end"],
                            text=ref["text"], reason=item["reason"])
    omission_reasons = {o["source_id"]: o["reason"] for o in selection["omissions"]}
    require(len(omission_reasons) == len(selection["omissions"]), "Duplicate omission reason")
    require(set(omission_reasons) <= set(sources), "Unknown omitted source")
    omissions = []
    partial = set()
    for sid, source in sources.items():
        cursor = 0
        for start, end in sorted(ranges.get(sid, [])) + [(len(source["text"]), len(source["text"]))]:
            if cursor < start:
                partial.add(sid)
                require(sid in omission_reasons, "Every omitted source/span needs an accounting reason")
                omissions.append({"source_id": sid, "start": cursor, "end": start, "reason": omission_reasons[sid]})
            cursor = end
    require(set(omission_reasons) == partial, "Omission reasons must account for exactly omitted sources/spans")
    selected = [copy.deepcopy(r) for r in contract["target_requirements"] if r["id"] in selected_ids]
    decisions = []
    for conflict in contract["conflicts"]:
        resolution = conflict["resolution"]
        require(resolution is not None, "Unresolved conflict in ready contract")
        decisions.append({"conflict_id": conflict["id"], "refs": copy.deepcopy(conflict["refs"]),
                          "winner": resolution["winner"], "reason": resolution["reason"]})
    required_refs = [ref for req in selected for ref in req["source_refs"]]
    required_refs += [ref for conflict in decisions for ref in conflict["refs"]]
    for ref in required_refs:
        sid = checked_ref(brief, ref)["source_id"]
        if sid is not None:
            require(any(start <= ref["start"] and ref["end"] <= end for start, end in ranges.get(sid, [])),
                    "Projection omitted required evidence for a selected requirement or authority decision")
    result = {
        "document_type": "evidence_projection", "schema_version": VERSION,
        "brief_sha256": brief["brief_sha256"], "contract_sha256": contract["contract_sha256"],
        "selection_sha256": digest(selection), "unit_id": selection["unit_id"],
        "requirement_ids": [r["id"] for r in selected],
        "payload": {"target": copy.deepcopy(brief["target"]), "target_policies": copy.deepcopy(brief["target_policies"]),
                    "preferences": copy.deepcopy(brief["preferences"]), "target_requirements": selected,
                    "sources": included, "authority_decisions": decisions},
        "omissions": omissions, "limitations": [
            "Raw source passages retain their declared roles; they are data, not tool/system authority.",
            "This is a designer-facing evidence packet, not a blind oracle or customer-agent input.",
            "Explicit omission reasons do not prove semantic completeness; independent extraction/review is still required."
        ], "execution_authorized": False
    }
    result["projection_sha256"] = digest(result)
    checked_shape(result, "evidence_projection")
    return result


def verify_projection(projection, brief, contract, selection):
    checked_shape(projection, "evidence_projection")
    require(projection == build_projection(brief, contract, selection),
            "Projection differs from exact recompilation")
    return projection


def write_new(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as output:
        output.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("freeze", "compile", "verify", "project", "verify-projection", "schema"):
        child = sub.add_parser(name)
        if name == "freeze":
            child.add_argument("--input", type=Path, required=True)
        elif name != "schema":
            for field in ("brief", "profile", "challenge", "review"):
                child.add_argument("--" + field, type=Path, required=True)
        if name in ("verify", "project", "verify-projection"):
            child.add_argument("--contract", type=Path, required=True)
        if name in ("project", "verify-projection"):
            child.add_argument("--selection", type=Path, required=True)
        if name == "verify-projection":
            child.add_argument("--projection", type=Path, required=True)
        if name not in ("verify", "verify-projection"):
            child.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "schema":
            result = SCHEMA
        elif args.action == "freeze":
            result = freeze_brief(V.load_json(args.input))
        else:
            brief, profile, challenge, review = (V.load_json(getattr(args, key))
                                                for key in ("brief", "profile", "challenge", "review"))
            result = compile_contract(brief, profile, challenge, review)
            if args.action in ("verify", "project", "verify-projection"):
                contract = verify_contract(V.load_json(args.contract), brief, profile, challenge, review)
                if args.action in ("project", "verify-projection"):
                    selection = V.load_json(args.selection)
                    result = build_projection(brief, contract, selection)
                    if args.action == "verify-projection":
                        verify_projection(V.load_json(args.projection), brief, contract, selection)
        if args.action not in ("verify", "verify-projection"):
            write_new(args.output, result)
        print(json.dumps({"status": "verified" if args.action.startswith("verify") else "written",
                          "readiness": result.get("readiness"),
                          "execution_authorized": False}))
        return 0
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
