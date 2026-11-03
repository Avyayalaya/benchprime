"""Regression cases for document-discriminated structural diagnostics."""

import copy
import unittest

from benchprime import validation as V


def contract(kind, *fields):
    return {
        "type": "object", "additionalProperties": False,
        "required": ["document_type", *fields],
        "properties": {"document_type": {"enum": [kind]},
                       **{field: {"type": "string"} for field in fields}},
    }


class DocumentDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.brief = contract("brief", "title")
        self.pack = contract("pack", "cases", "criteria", "source")
        self.schema = {"oneOf": [self.brief, self.pack]}

    def check(self, value, schema=None):
        schema = self.schema if schema is None else schema
        return V.check_schema(schema, value, schema)

    def test_explicit_type_selects_diagnostics_even_with_more_errors(self):
        self.assertEqual(self.check({"document_type": "pack"}), [
            "$: must match exactly one contract", "$: missing cases",
            "$: missing criteria", "$: missing source",
        ])

    def test_ref_branches_and_ref_discriminators_select_the_declared_type(self):
        pack = copy.deepcopy(self.pack)
        pack["properties"]["document_type"] = {"$ref": "#/$defs/pack_type"}
        schema = {
            "$defs": {"brief": self.brief, "pack": pack,
                      "pack_alias": {"$ref": "#/$defs/pack"},
                      "pack_type": {"enum": ["pack"]}},
            "oneOf": [{"$ref": "#/$defs/brief"}, {"$ref": "#/$defs/pack_alias"}],
        }
        self.assertEqual(self.check({"document_type": "pack"}, schema), [
            "$: must match exactly one contract", "$: missing cases",
            "$: missing criteria", "$: missing source",
        ])

    def test_wrong_declared_type_is_not_replaced_by_shape_guessing(self):
        self.assertEqual(self.check({"document_type": "brief", "cases": "input"}), [
            "$: must match exactly one contract", "$: missing title",
            "$: undeclared key cases",
        ])

    def test_missing_unknown_and_invalid_types_keep_fallback_errors(self):
        for value in ({}, {"document_type": "unknown"}, {"document_type": None},
                      {"document_type": ["pack"]}, {"document_type": 1}):
            with self.subTest(value=value):
                expected = min((V.check_schema(branch, value, self.schema)
                                for branch in self.schema["oneOf"]), key=len)
                self.assertEqual(self.check(value), ["$: must match exactly one contract"] + expected)

    def test_ambiguous_discriminator_keeps_fallback_diagnostics(self):
        other_pack = contract("pack", "title")
        schema = {"oneOf": [self.pack, other_pack]}
        self.assertEqual(self.check({"document_type": "pack"}, schema),
                         ["$: must match exactly one contract", "$: missing title"])

    def test_overlapping_successful_branches_still_fail_exactly_one(self):
        schema = {"oneOf": [self.brief, {"type": "object"}]}
        self.assertEqual(self.check({"document_type": "brief", "title": "test"}, schema),
                         ["$: must match exactly one contract"])

    def test_discriminator_does_not_change_exact_one_acceptance(self):
        schema = {"oneOf": [self.pack, {"type": "object"}]}
        self.assertEqual(self.check({"document_type": "pack"}, schema), [])
        self.assertEqual(self.check({"document_type": "pack", "cases": "x",
                                     "criteria": "y", "source": "z"}), [])

    def test_a_matching_discriminator_never_turns_an_invalid_branch_green(self):
        errors = self.check({"document_type": "pack", "cases": [], "criteria": 1, "source": False})
        self.assertEqual(errors, ["$: must match exactly one contract",
                                  "$.cases: expected ['string']",
                                  "$.criteria: expected ['string']",
                                  "$.source: expected ['string']"])

    def test_nested_location_is_preserved(self):
        schema = {"type": "object", "properties": {"payload": self.schema}}
        self.assertEqual(V.check_schema(schema, {"payload": {"document_type": "pack"}}, schema), [
            "$.payload: must match exactly one contract", "$.payload: missing cases",
            "$.payload: missing criteria", "$.payload: missing source",
        ])

    def test_unsupported_schema_in_another_branch_is_never_skipped(self):
        for unsupported in ({"not": {}}, {"$ref": "other.json"},
                            {"$ref": "#/$defs/missing"}, {"type": "unknown"}):
            with self.subTest(unsupported=unsupported):
                schema = {"oneOf": [self.pack, unsupported]}
                with self.assertRaisesRegex(ValueError, "Unsupported schema"):
                    self.check({"document_type": "pack"}, schema)


if __name__ == "__main__":
    unittest.main()
