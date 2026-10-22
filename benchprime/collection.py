"""Collection-first ontology, exact counts and principle/dimension traceability."""

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("collection_contract_helpers", HERE / "contracts.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
obj, arr, enum, T = C.obj, C.arr, C.enum, C.T
digest = C.digest
LINK = obj(principle_id=T, explanation=T, status=enum("author_mapped", "model_proposed", "fixture"))
CATEGORY = obj(id=T, title=T, meaning=T, rationale=T, dimension_ids=arr(T, 1), principle_links=arr(LINK, 1))
THEME = obj(id=T, category_id=T, title=T, meaning=T, rationale=T, dimension_ids=arr(T, 1), principle_ids=arr(T, 1))
SCENARIO = obj(id=T, family_id=T, category_id=T, title=T, rationale=T, theme_ids=arr(T, 1), principle_ids=arr(T, 1))
ASSIGNMENT = obj(case_id=T, scenario_id=T, primary_category_id=T, secondary_category_ids=arr(T))
SCHEMA = obj(version=enum("1.0.0"), catalog_hash=T, purpose=T,
             provenance=obj(kind=enum("author_mapped", "model_proposed", "fixture"), note=T),
             categories=arr(CATEGORY, 1), themes=arr(THEME, 1), scenarios=arr(SCENARIO, 1),
             case_assignments=arr(ASSIGNMENT, 1))
C.V.audit_schema(SCHEMA)

# Blueprint references use local labels; controller/bridge binds stable IDs.
BLUEPRINT = obj(
    categories=arr(obj(key=T, title=T, meaning=T, rationale=T, principle_links=arr(LINK, 1)), 1),
    themes=arr(obj(key=T, category_key=T, title=T, meaning=T, rationale=T,
                   requirement_ids=arr(T, 1), principle_ids=arr(T, 1)), 1))


def index(rows, key="id"):
    C.unique([r[key] for r in rows], key)
    return {r[key]: r for r in rows}


def refs(values, allowed, name, nonempty=True):
    C.require((values or not nonempty) and len(values) == len(set(values)) and set(values) <= set(allowed),
              f"Invalid {name} references")


def catalog():
    value = C.V.load_json(HERE / "patterns" / "design_principles.json")
    C.require(value["document_type"] == "evaluation_design_principles" and value["version"] == "1.0.0",
              "Unsupported principle catalogue")
    C.require(set(index(value["principles"])) == {f"P{i}" for i in range(1, 11)}, "Principle catalogue inventory changed")
    C.require(set(index(value["generator_dimensions"])) == {f"D{i:02}" for i in range(1, 12)},
              "Generator responsibility inventory changed")
    return value


def root_of(key, dimensions):
    seen = set()
    while True:
        C.require(key in dimensions and key not in seen, "Invalid dimension hierarchy")
        seen.add(key)
        if dimensions[key]["parent_id"] is None:
            return key
        key = dimensions[key]["parent_id"]


def validate_blueprint(blueprint, requirements, families):
    errors = C.V.check_schema(BLUEPRINT, blueprint, {})
    C.require(not errors, "\n".join(errors))
    categories = index(blueprint["categories"], "key")
    themes = index(blueprint["themes"], "key")
    principles = index(catalog()["principles"])
    used_requirements = []
    for category in categories.values():
        C.require(all(category[k].strip() for k in ("title", "meaning", "rationale")) and
                  all(link["explanation"].strip() for link in category["principle_links"]),
                  "Category meaning and selection rationale must be substantive text")
        refs([l["principle_id"] for l in category["principle_links"]], principles, "principle")
    for theme in themes.values():
        C.require(theme["category_key"] in categories, "Unknown theme category")
        refs(theme["requirement_ids"], requirements, "theme requirement")
        refs(theme["principle_ids"], principles, "theme principle")
        used_requirements.extend(theme["requirement_ids"])
    C.require(len(used_requirements) == len(set(used_requirements)) and set(used_requirements) == set(requirements),
              "Every target requirement needs exactly one primary theme, including gaps")
    C.require({theme["category_key"] for theme in themes.values()} == set(categories),
              "Every declared category needs a theme tied to the target requirements")
    for family in families:
        C.require(family["category_key"] in categories, "Unknown family category")
        refs(family["theme_keys"], themes, "family theme")
        refs(family["principle_ids"], principles, "family principle")
        C.require(any(themes[t]["category_key"] == family["category_key"] for t in family["theme_keys"]),
                  "Family needs a theme in its primary category")
        routed = {r for t in family["theme_keys"] for r in themes[t]["requirement_ids"]}
        C.require(set(family["requirement_ids"]) <= routed, "Family requirements not explained by assigned themes")


def validate(pack):
    value = pack["collection"]
    errors = C.V.check_schema(SCHEMA, value, {})
    C.require(not errors, "\n".join(errors))
    def meaningful(node):
        if isinstance(node, str):
            C.require(bool(node.strip()), "Collection text must not be whitespace-only")
        elif isinstance(node, dict):
            for child in node.values():
                meaningful(child)
        elif isinstance(node, list):
            for child in node:
                meaningful(child)
    meaningful(value)
    C.require(value["catalog_hash"] == digest(catalog()), "Stale principle catalog binding")
    categories, themes, scenarios = (index(value[k]) for k in ("categories", "themes", "scenarios"))
    cases, families, dimensions = (index(pack[k]) for k in ("cases", "families", "dimensions"))
    principles = index(catalog()["principles"])
    roots = {k for k, d in dimensions.items() if d["parent_id"] is None}
    covered_roots = []
    for cat in categories.values():
        refs(cat["dimension_ids"], roots, "category dimension")
        refs([l["principle_id"] for l in cat["principle_links"]], principles, "principle")
        covered_roots += cat["dimension_ids"]
    C.require(len(covered_roots) == len(set(covered_roots)) and set(covered_roots) == roots,
              "Categories must partition all declared target dimension roots")
    for theme in themes.values():
        C.require(theme["category_id"] in categories, "Missing theme category")
        refs(theme["dimension_ids"], dimensions, "theme dimension")
        refs(theme["principle_ids"], principles, "theme principle")
        C.require(all(root_of(d, dimensions) in categories[theme["category_id"]]["dimension_ids"]
                      for d in theme["dimension_ids"]), "Cross-category theme dimension")
    C.require({t["category_id"] for t in themes.values()} == set(categories), "Every category needs declared themes, even with no tests")
    C.require(len(scenarios) == len(families) and {s["family_id"] for s in scenarios.values()} == set(families),
              "Every scenario group must map one existing family")
    for scenario in scenarios.values():
        C.require(scenario["category_id"] in categories, "Missing scenario category")
        refs(scenario["theme_ids"], themes, "scenario theme")
        refs(scenario["principle_ids"], principles, "scenario principle")
        C.require(all(themes[t]["category_id"] == scenario["category_id"] for t in scenario["theme_ids"]),
                  "Scenario theme crosses category")
    assignments = index(value["case_assignments"], "case_id")
    C.require(set(assignments) == set(cases), "Every distinct case requires one primary assignment")
    for cid, assignment in assignments.items():
        scenario = scenarios.get(assignment["scenario_id"])
        C.require(scenario is not None and scenario["family_id"] == cases[cid]["family_id"],
                  "Case scenario/family mismatch")
        cat = assignment["primary_category_id"]
        C.require(cat in categories and scenario["category_id"] == cat, "Case primary category differs from scenario")
        primary = cases[cid].get("primary_dimension_ids", cases[cid]["dimension_ids"])[0]
        C.require(root_of(primary, dimensions) in categories[cat]["dimension_ids"], "Case primary dimension/category mismatch")
        refs(assignment["secondary_category_ids"], categories, "secondary category", False)
        C.require(cat not in assignment["secondary_category_ids"], "Primary category repeated as secondary")
        actual_roots = {root_of(d, dimensions) for d in cases[cid]["dimension_ids"]}
        C.require(all(actual_roots.intersection(categories[c]["dimension_ids"])
                      for c in assignment["secondary_category_ids"]), "Secondary category lacks dimension evidence")
    return value


def project(pack):
    value = copy.deepcopy(validate(pack))
    categories, themes, scenarios = (index(value[k]) for k in ("categories", "themes", "scenarios"))
    assignments = value["case_assignments"]
    dimensions = index(pack["dimensions"])
    requirements = index(pack["requirements"])
    coverage = index(pack["coverage"], "requirement_id")
    cases = index(pack["cases"])
    for scenario in scenarios.values():
        ids = [a["case_id"] for a in assignments if a["scenario_id"] == scenario["id"]]
        scenario.update(case_ids=ids, test_count=len(ids),
                        check_count=sum(c["case_id"] in ids for c in pack["criteria"]))
    for theme in themes.values():
        groups = [s for s in scenarios.values() if theme["id"] in s["theme_ids"]]
        ids = sorted({c for s in groups for c in s["case_ids"]})
        theme.update(scenario_ids=[s["id"] for s in groups], test_count=len(ids),
                     scenario_count=len(groups), case_ids=ids)
    for cat in categories.values():
        ids = [a["case_id"] for a in assignments if a["primary_category_id"] == cat["id"]]
        groups = [s for s in scenarios.values() if s["category_id"] == cat["id"]]
        gaps = [rid for rid, r in requirements.items() if root_of(r["dimension_id"], dimensions) in cat["dimension_ids"]
                and coverage[rid]["status"] == "gap"]
        cat.update(case_ids=ids, test_count=len(ids), scenario_count=len(groups),
                   theme_ids=[t["id"] for t in themes.values() if t["category_id"] == cat["id"]],
                   scenario_ids=[s["id"] for s in groups], gap_requirement_ids=gaps,
                   secondary_case_ids=[a["case_id"] for a in assignments if cat["id"] in a["secondary_category_ids"]])
    value["counts"] = {
        "tests": len(cases), "checks": len(pack["criteria"]), "categories": len(categories),
        "populated_categories": sum(c["test_count"] > 0 for c in categories.values()),
        "themes": len(themes), "populated_themes": sum(t["test_count"] > 0 for t in themes.values()),
        "scenarios": len(scenarios), "requirements": len(requirements),
        "exposed_requirements": sum(r["status"] == "exposed" for r in coverage.values()),
        "gap_requirements": sum(r["status"] == "gap" for r in coverage.values()),
        "excluded_requirements": sum(r["status"] == "excluded" for r in coverage.values())}
    value["principles"] = copy.deepcopy(catalog()["principles"])
    value["generator_dimensions"] = copy.deepcopy(catalog()["generator_dimensions"])
    value["gaps"] = [{"requirement_id": rid, "dimension_id": requirements[rid]["dimension_id"],
                     "dimension": dimensions[requirements[rid]["dimension_id"]]["label"], "reason": row["reason"]}
                    for rid, row in coverage.items() if row["status"] == "gap"]
    return value


def summary(collection):
    c = collection["counts"]
    return (f'{c["tests"]} test definitions across {c["populated_categories"]} populated categories '
            f'and {c["scenarios"]} scenario groups, with {c["checks"]} checks.')


def overview_entries(model, detail=True):
    """Ordered semantic content shared by Office authoring and verification."""
    c = model["collection"]
    dims = index(model["dimensions"])
    principles = index(c["principles"])
    entries = [("Collection purpose", c["purpose"]), ("Collection summary", summary(c)),
               ("Declared coverage", f'{c["counts"]["categories"]} declared categories; '
                f'{c["counts"]["themes"]} themes ({c["counts"]["populated_themes"]} with tests); '
                f'{c["counts"]["exposed_requirements"]}/{c["counts"]["requirements"]} requirements exposed; '
                f'{c["counts"]["gap_requirements"]} gaps. No target runs or scores.'),
               ("Mapping provenance", c["provenance"]["note"]),
               ("Principle framework", "; ".join(p["title"] for p in c["principles"])),
               ("Generator quality scope", "The separate11generator-quality responsibilities assess the creation process and collection; target dimensions assess this system."),
               ("Counting rule", "Primary category counts sum to unique tests. Secondary category/theme incidence overlaps and is not additive. Quantity and priority are not measured performance.")]
    for cat in c["categories"]:
        entries += [(cat["title"], cat["meaning"]), ("Why selected", cat["rationale"]),
                    ("Volume", f'{cat["test_count"]} primary tests; {cat["scenario_count"]} scenario groups.'),
                    ("Target dimensions", "; ".join(dims[x]["label"] for x in cat["dimension_ids"]))]
        for link in cat["principle_links"]:
            entries.append((principles[link["principle_id"]]["title"], link["explanation"] + " [" + link["status"] + "]"))
        if not detail:
            entries.append(("Scenario groups", "; ".join(
                f'{s["title"]} ({s["test_count"]} tests)' for s in c["scenarios"] if s["category_id"] == cat["id"])
                or "No tests yet; declared coverage gap."))
            continue
        for theme in c["themes"]:
            if theme["category_id"] != cat["id"]:
                continue
            entries += [(theme["title"], theme["meaning"]), ("Theme rationale", theme["rationale"]),
                        ("Theme volume", f'{theme["test_count"]} linked tests; {theme["scenario_count"]} scenario groups.')]
            for group in c["scenarios"]:
                if theme["id"] in group["theme_ids"]:
                    entries.append((group["title"], group["rationale"] + f' ({group["test_count"]} tests)'))
    entries += [("Coverage gap: " + g["dimension"], g["reason"]) for g in c["gaps"]]
    if detail:
        entries += [("Principle: " + p["title"], p["meaning"] + " " + p["expression"]) for p in c["principles"]]
    return entries
