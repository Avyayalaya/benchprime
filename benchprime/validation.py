"""Check pack structure and references; never generate, execute, or grade an agent."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
KEYWORDS = {"$schema", "$defs", "$ref", "title", "description", "oneOf", "type",
            "enum", "required", "properties", "additionalProperties", "items", "minItems", "minLength"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object, parse_constant=invalid_constant)


def audit_schema(schema):
    if not isinstance(schema, dict) or set(schema) - KEYWORDS:
        raise ValueError("Unsupported schema object or assertion")
    if "additionalProperties" in schema and type(schema["additionalProperties"]) is not bool:
        raise ValueError("This subset supports boolean additionalProperties only")
    for key in ("properties", "$defs"):
        if key in schema:
            if not isinstance(schema[key], dict):
                raise ValueError(f"Schema {key} must be an object")
            for child in schema[key].values():
                audit_schema(child)
    if "items" in schema:
        audit_schema(schema["items"])
    if "oneOf" in schema:
        if not isinstance(schema["oneOf"], list) or not schema["oneOf"]:
            raise ValueError("Schema oneOf must contain branches")
        for child in schema["oneOf"]:
            audit_schema(child)
    for key in ("minLength", "minItems"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise ValueError(f"Schema {key} must be a nonnegative integer")


def check_schema(schema, value, root, location="$"):
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise ValueError(f"Unsupported schema assertion at {location}: {sorted(unknown)}")
    if "$ref" in schema:
        reference = schema["$ref"]
        if not reference.startswith("#/$defs/") or reference[8:] not in root.get("$defs", {}):
            raise ValueError(f"Unsupported schema reference: {reference}")
        return check_schema(root["$defs"][reference[8:]], value, root, location)
    if "oneOf" in schema:
        alternatives = [check_schema(branch, value, root, location) for branch in schema["oneOf"]]
        if sum(not errors for errors in alternatives) != 1:
            return [f"{location}: must match exactly one contract"] + min(alternatives, key=len)
    errors = []
    types = schema.get("type")
    matches = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "null": value is None, "integer": type(value) is int,
        "number": type(value) in (int, float),
    }
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if any(kind not in matches for kind in types):
            raise ValueError(f"Unsupported schema type at {location}")
        if not any(matches[kind] for kind in types):
            return [f"{location}: expected {types}"]
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        errors.append(f"{location}: value outside enum")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{location}: empty/short string")
    if isinstance(value, dict):
        errors.extend(f"{location}: missing {key}" for key in schema.get("required", []) if key not in value)
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors += check_schema(properties[key], item, root, f"{location}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}: undeclared key {key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: too few items")
        if "items" in schema:
            for index, item in enumerate(value):
                errors += check_schema(schema["items"], item, root, f"{location}[{index}]")
    return errors


def changed_paths(a, b, prefix=""):
    if type(a) is not type(b):
        return {prefix}
    if isinstance(a, dict):
        paths = set()
        for key in a.keys() | b.keys():
            pointer = prefix + "/" + key.replace("~", "~0").replace("/", "~1")
            paths |= {pointer} if key not in a or key not in b else changed_paths(a[key], b[key], pointer)
        return paths
    if isinstance(a, list):
        if len(a) != len(b):
            return {prefix}
        return set().union(*(changed_paths(x, y, f"{prefix}/{i}") for i, (x, y) in enumerate(zip(a, b))))
    return set() if a == b else {prefix}

