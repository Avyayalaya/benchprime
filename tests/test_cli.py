import base64
import copy
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "packs" / "alder" / "v0.1" / "evaluation.json"


class HtmlLinks(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append((attrs[key], attrs.get("download")))

    def downloads(self):
        return {name: base64.b64decode(url.split(",", 1)[1], validate=True).decode("utf-8")
                for url, name in self.links if name and url.startswith("data:")}


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="benchprime-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.pack = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def call(self, *args, success=True):
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTHONPATH", "GH_TOKEN", "GITHUB_TOKEN")}
        result = subprocess.run([sys.executable, "-S", "-m", "benchprime", *map(str, args)],
                                cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0 if success else 1, result.stdout + result.stderr)
        return result

    def save(self, value, name="input.json"):
        path = self.work / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_sample_validates_without_semantic_certification(self):
        result = json.loads(self.call("validate", SAMPLE).stdout)
        self.assertEqual(result["status"], "structurally_valid")
        self.assertFalse(result["semantic_certification"])

    def test_collection_summary_has_real_counts(self):
        result = json.loads(self.call("inspect", SAMPLE).stdout)
        self.assertEqual((result["cases"], result["criteria"], result["categories"]), (12, 133, 5))

    def test_export_contains_only_candidate_data(self):
        destination = self.work / "candidate.json"
        self.call("export", SAMPLE, "--case-number", 1, "--output", destination)
        value = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(set(value), {"case_id", "input"})
        self.assertEqual(value["input"], self.pack["cases"][0]["input"])

    def test_export_all_excludes_reserved_cases(self):
        self.pack["cases"][0]["track"] = "reserved"
        destination = self.work / "inputs.jsonl"
        self.call("export", self.save(self.pack), "--output", destination)
        rows = [json.loads(line) for line in destination.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 11)
        self.assertNotIn(self.pack["cases"][0]["id"], {row["case_id"] for row in rows})

    def test_refuses_output_overwrite(self):
        destination = self.work / "candidate.json"
        destination.write_text("keep")
        self.call("export", SAMPLE, "--case-number", 1, "--output", destination, success=False)
        self.assertEqual(destination.read_text(), "keep")

    def test_refuses_writes_inside_bundled_packs(self):
        self.call("export", SAMPLE, "--output", SAMPLE.parent / "unexpected.jsonl", success=False)
        self.assertFalse((SAMPLE.parent / "unexpected.jsonl").exists())

    def test_bad_case_number_is_explicit(self):
        self.call("export", SAMPLE, "--case-number", 0, "--output", self.work / "out.json", success=False)

    def test_tampered_evidence_is_rejected(self):
        self.pack["criteria"][0]["evidence"][0]["text"] += " changed"
        self.call("validate", self.save(self.pack), success=False)

    def test_duplicate_json_key_is_rejected(self):
        path = self.work / "duplicate.json"
        path.write_text('{"document_type":"evaluation_design_pack","document_type":"other"}')
        self.call("validate", path, success=False)

    def test_missing_coverage_is_rejected(self):
        self.pack["coverage"].pop()
        self.call("validate", self.save(self.pack), success=False)

    def test_prepare_binds_only_missing_derived_fields(self):
        del self.pack["pattern_bundle_hash"]
        del self.pack["collection"]["catalog_hash"]
        for criterion in self.pack["criteria"]:
            for ref in criterion["evidence"]:
                del ref["text"]
                del ref["sha256"]
        output = self.work / "prepared.json"
        result = json.loads(self.call("prepare", self.save(self.pack), "--output", output).stdout)
        prepared = json.loads(output.read_text(encoding="utf-8"))
        self.assertGreater(result["bound_fields"], 0)
        self.assertEqual(prepared["cases"], self.pack["cases"])
        self.call("validate", output)

    def test_prepare_never_repairs_supplied_wrong_hash(self):
        self.pack["criteria"][0]["evidence"][0]["sha256"] = "wrong"
        output = self.work / "prepared.json"
        self.call("prepare", self.save(self.pack), "--output", output, success=False)
        self.assertFalse(output.exists())

    def test_prepare_explicitly_defers_unassessed_methods(self):
        del self.pack["pattern_applications"]
        output = self.work / "prepared.json"
        result = json.loads(self.call("prepare", self.save(self.pack), "--output", output).stdout)
        self.assertEqual(result["deferred_patterns"], 14)
        self.assertEqual({x["disposition"] for x in json.loads(output.read_text(encoding="utf-8"))["pattern_applications"]},
                         {"deferred"})

    def test_invalid_array_pointer_is_rejected(self):
        ref = self.pack["criteria"][0]["evidence"][0]
        ref["pointer"] = "/context/policy/-1"
        ref.pop("text")
        ref.pop("sha256")
        self.call("prepare", self.save(self.pack), "--output", self.work / "bad.json", success=False)

    def test_html_render_escapes_untrusted_title(self):
        self.pack["card"]["title"] = "<script>alert('x')</script>"
        output = self.work / "casebook.html"
        self.call("render", self.save(self.pack), "--output", output)
        html = output.read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>alert('x')</script>", html)

    def test_html_render_has_no_missing_local_dependencies(self):
        output = self.work / "casebook.html"
        self.call("render", SAMPLE, "--output", output)
        page = HtmlLinks(output.read_text(encoding="utf-8"))
        for url, _ in page.links:
            if url.startswith("#"):
                self.assertIn(url[1:], page.ids)
            else:
                self.assertIn(urlsplit(url).scheme, {"data", "https", "http"}, url)
        downloads = page.downloads()
        markdown = [text for name, text in downloads.items() if name.endswith(".md")]
        self.assertEqual(len(markdown), len(self.pack["cases"]))
        for case in self.pack["cases"]:
            self.assertTrue(any(case["id"] in text and "## Expected behavior" in text for text in markdown))
        self.assertNotIn("EVALUATION_DESIGN.xlsx", downloads)
        self.assertNotIn("EXECUTIVE_DESIGN_BRIEF.docx", downloads)

    def test_html_embedded_candidates_match_filtered_export(self):
        self.pack["cases"][0]["track"] = "reserved"
        self.pack["cases"][1]["status"] = "blocked"
        blocked_id = self.pack["cases"][1]["id"]
        for row in self.pack["coverage"]:
            row["case_ids"] = [case_id for case_id in row["case_ids"] if case_id != blocked_id]
            if row["status"] == "exposed" and not row["case_ids"]:
                row["status"] = "gap"
                row["reason"] = "The blocked fixture case has no reviewable replacement."
        document = self.save(self.pack)
        output, export = self.work / "casebook.html", self.work / "inputs.jsonl"
        self.call("render", document, "--output", output)
        self.call("export", document, "--output", export)
        payload = HtmlLinks(output.read_text(encoding="utf-8")).downloads()["CANDIDATE_INPUTS.jsonl"]
        self.assertEqual(payload, export.read_text(encoding="utf-8"))
        self.assertEqual(len(payload.splitlines()), 10)
        self.assertTrue(all(set(json.loads(line)) == {"case_id", "input"} for line in payload.splitlines()))

    def test_html_embeds_an_empty_export_when_all_cases_are_reserved(self):
        for case in self.pack["cases"]:
            case["track"] = "reserved"
        output = self.work / "casebook.html"
        self.call("render", self.save(self.pack), "--output", output)
        self.assertEqual(HtmlLinks(output.read_text(encoding="utf-8")).downloads()["CANDIDATE_INPUTS.jsonl"], "")

    def test_full_delivery_renderer_retains_bundle_links(self):
        code = ("import json; from pathlib import Path; from benchprime import design, render; "
                f"pack=json.loads(Path({str(SAMPLE)!r}).read_text(encoding='utf-8')); "
                "print(render.render_html(design.project(pack)))")
        result = subprocess.run([sys.executable, "-S", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONUTF8": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        links = {url for url, _ in HtmlLinks(result.stdout).links}
        self.assertIn("../run/CANDIDATE_INPUTS.jsonl", links)
        self.assertIn("../run/ADAPTER_GUIDE.md", links)
        self.assertIn("EVALUATION_DESIGN.xlsx", links)
        self.assertIn("EXECUTIVE_DESIGN_BRIEF.docx", links)
        self.assertTrue(any(url.startswith("cases/") for url in links))

    def test_freeze_validates_typed_intake_and_computes_hashes(self):
        output = self.work / "brief.json"
        self.call("freeze", ROOT / "examples" / "alder-intake.json", "--output", output)
        brief = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(brief["document_type"], "repeatability_brief")
        self.assertEqual(len(brief["brief_sha256"]), 64)
        self.assertTrue(all(len(source["sha256"]) == 64 for source in brief["sources"]))

    def test_error_does_not_create_an_output(self):
        output = self.work / "out.json"
        self.call("export", self.work / "missing.json", "--output", output, success=False)
        self.assertFalse(output.exists())

    def test_non_object_input_returns_an_explicit_error(self):
        result = self.call("validate", self.save([]), success=False)
        self.assertIn("JSON object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_references_are_bound_to_frozen_source_authority(self):
        brief_path, refs_path = self.work / "brief.json", self.work / "refs.json"
        self.call("freeze", ROOT / "examples" / "alder-intake.json", "--output", brief_path)
        self.call("references", brief_path, "--output", refs_path)
        refs = json.loads(refs_path.read_text(encoding="utf-8"))["references"]
        self.assertEqual(refs[0]["reference"]["pointer"], "/target/instructions")
        self.assertEqual(refs[0]["authority"]["kind"], "normative")
        self.assertTrue(any(r["authority"]["kind"] == "descriptive" for r in refs))

    def test_start_creates_task_and_exact_kickoff_without_generation(self):
        destination = self.work / "my-eval"
        result = json.loads(self.call("start", destination).stdout)
        self.assertFalse(result["generation_started"])
        self.assertTrue((destination / "sources").is_dir())
        self.assertIn("## The job", (destination / "task.md").read_text(encoding="utf-8"))
        self.assertIn("## Evaluation purpose", (destination / "task.md").read_text(encoding="utf-8"))
        kickoff = (destination / "KICKOFF.md").read_text(encoding="utf-8")
        self.assertIn("workflows/generate.md", kickoff)
        self.assertIn("casebook.html", kickoff)
        self.assertIn("purpose and use case", kickoff)
        self.assertNotIn("coding assistant", kickoff)

    def test_start_from_task_preserves_exact_text(self):
        task = self.work / "original.md"
        task.write_text("# My task\nPreserve caf\u00e9 names.\n", encoding="utf-8")
        destination = self.work / "started"
        self.call("start", destination, "--task", task)
        self.assertEqual((destination / "task.md").read_bytes(), task.read_bytes())

    def test_start_from_intake_preserves_source_text_and_authority(self):
        destination = self.work / "alder"
        self.call("start", destination, "--from-intake", ROOT / "examples" / "alder-intake.json")
        intake = json.loads((ROOT / "examples" / "alder-intake.json").read_text(encoding="utf-8"))
        source_files = sorted((destination / "sources").glob("*.txt"))
        self.assertEqual([p.read_text(encoding="utf-8") for p in source_files],
                         [s["text"] for s in intake["sources"]])
        task = (destination / "task.md").read_text(encoding="utf-8")
        self.assertIn("normative", task)
        self.assertIn("descriptive", task)
        self.assertIn("private", task)
        self.assertIn("## Evaluation purpose", task)

    def test_start_refuses_existing_directory(self):
        self.call("start", self.work, success=False)
        self.assertFalse((self.work / "task.md").exists())

    def test_start_refuses_bundled_pack_directory(self):
        self.call("start", SAMPLE.parent / "new-task", success=False)
        self.assertFalse((SAMPLE.parent / "new-task").exists())

    def test_start_invalid_intake_does_not_create_workspace(self):
        destination = self.work / "invalid"
        self.call("start", destination, "--from-intake", self.save({}), success=False)
        self.assertFalse(destination.exists())

    def test_start_source_ids_cannot_escape_sources_directory(self):
        intake = json.loads((ROOT / "examples" / "alder-intake.json").read_text(encoding="utf-8"))
        intake["sources"][0]["source_id"] = "../../outside"
        destination = self.work / "safe"
        self.call("start", destination, "--from-intake", self.save(intake))
        self.assertFalse((self.work / "outside.txt").exists())
        self.assertTrue(all(p.parent == destination / "sources" for p in destination.rglob("*.txt")))

    def test_tutorial_counts_and_gap_are_explicit(self):
        result = json.loads(self.call("inspect", ROOT / "examples/ticket-triage/evaluation.json").stdout)
        self.assertEqual((result["cases"], result["criteria"], result["categories"], result["gaps"]), (6, 18, 3, 1))
        self.assertEqual(result["review_status"], "partial")

    def test_shipped_tutorial_casebook_matches_standalone_render(self):
        folder = ROOT / "examples" / "ticket-triage"
        output = self.work / "tutorial.html"
        self.call("render", folder / "evaluation.json", "--output", output)
        self.assertEqual(output.read_text(encoding="utf-8"),
                         (folder / "casebook.html").read_text(encoding="utf-8"))

    def test_tutorial_preparation_replays_the_supplied_draft(self):
        folder = ROOT / "examples" / "ticket-triage"
        output = self.work / "tutorial.json"
        self.call("prepare", folder / "authored-draft.json", "--output", output)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")),
                         json.loads((folder / "evaluation.json").read_text(encoding="utf-8")))

    def test_tutorial_policy_is_preserved_in_all_candidates(self):
        folder = ROOT / "examples" / "ticket-triage"
        intake = json.loads((folder / "intake.json").read_text(encoding="utf-8"))
        pack = json.loads((folder / "evaluation.json").read_text(encoding="utf-8"))
        self.assertTrue(all(c["input"]["context"]["policy"] == [intake["sources"][0]["text"]]
                            for c in pack["cases"]))
        self.assertTrue(all(c["review"] == "proposed" for c in pack["criteria"]))

    def test_tutorial_label_expectations_follow_the_authored_policy(self):
        pack = json.loads((ROOT / "examples/ticket-triage/evaluation.json").read_text(encoding="utf-8"))
        criteria = {c["id"]: c for c in pack["criteria"]}
        expected = {"invoice-discrepancy": "billing", "invoice-instructions": "how_to",
                    "explicit-crash": "technical", "insufficient-detail": "needs_review",
                    "ordinary-billing": "billing", "embedded-instruction": "billing"}
        for case, label in expected.items():
            self.assertTrue(criteria[case + "-label"]["statement"].startswith("The label is " + label + ","))

    def test_tutorial_provenance_does_not_claim_an_independent_run(self):
        provenance = json.loads((ROOT / "examples/ticket-triage/provenance.json").read_text())
        self.assertEqual(provenance["kind"], "authored_tutorial")
        self.assertEqual(provenance["provider_calls"], 0)
        self.assertFalse(provenance["blind_generation_claimed"])
        self.assertFalse(provenance["target_executed"])


if __name__ == "__main__":
    unittest.main()
