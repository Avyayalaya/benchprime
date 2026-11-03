import base64
import copy
import hashlib
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
    def test_bundled_delivery_manifest_matches_all_shipped_bytes(self):
        folder = SAMPLE.parent / "delivery"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(manifest["files"]) | {"manifest.json"})
        for name, expected in manifest["files"].items():
            with self.subTest(path=name):
                path = (folder / name).resolve()
                self.assertTrue(path.is_relative_to(folder.resolve()))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="benchprime-test-", dir=ROOT)
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

    def test_draft_validation_reports_pack_fields_and_prepare_first(self):
        folder = ROOT / "examples" / "meeting-actions"
        draft = folder / "authored-draft.json"
        before = draft.read_bytes()
        result = self.call("validate", draft, success=False)
        self.assertIn("missing pattern_bundle_hash", result.stderr)
        self.assertIn("missing pattern_applications", result.stderr)
        self.assertNotIn("undeclared key cases", result.stderr)
        self.assertNotIn("undeclared key criteria", result.stderr)
        self.assertNotIn("missing target_kind", result.stderr)
        self.assertIn("python -m benchprime prepare", result.stderr)
        self.assertIn(str(draft), result.stderr)
        self.assertIn("new filename", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(draft.read_bytes(), before)
        output = self.work / "prepared.json"
        self.call("prepare", draft, "--output", output)
        checked = self.call("validate", output)
        self.assertEqual(checked.stderr, "")
        self.assertEqual(json.loads(checked.stdout)["status"], "structurally_valid")
        self.assertFalse(json.loads(checked.stdout)["semantic_certification"])

    def test_validate_only_suggests_prepare_when_it_can_fix_the_omissions(self):
        for field in ("pattern_bundle_hash", "pattern_applications"):
            with self.subTest(field=field):
                draft = copy.deepcopy(self.pack)
                del draft[field]
                result = self.call("validate", self.save(draft), success=False)
                self.assertIn("missing " + field, result.stderr)
                self.assertIn("python -m benchprime prepare", result.stderr)
        draft = copy.deepcopy(self.pack)
        del draft["criteria"][0]["evidence"][0]["sha256"]
        result = self.call("validate", self.save(draft), success=False)
        self.assertIn("missing sha256", result.stderr)
        self.assertIn("python -m benchprime prepare", result.stderr)

    def test_validate_never_offers_prepare_as_a_fix_for_authored_or_stale_errors(self):
        drafts = []
        wrong_hash = copy.deepcopy(self.pack)
        wrong_hash["criteria"][0]["evidence"][0]["sha256"] = "wrong"
        drafts.append((wrong_hash, "Stale/wrong evidence text"))
        wrong_pointer = copy.deepcopy(self.pack)
        wrong_pointer["criteria"][0]["evidence"][0]["pointer"] = "/missing"
        drafts.append((wrong_pointer, "missing"))
        malformed = copy.deepcopy(self.pack)
        del malformed["pattern_bundle_hash"]
        malformed["cases"] = "not cases"
        drafts.append((malformed, "$.cases: expected ['array']"))
        no_collection = copy.deepcopy(self.pack)
        del no_collection["collection"]
        drafts.append((no_collection, "Collection-first"))
        missing_authored = copy.deepcopy(self.pack)
        del missing_authored["pattern_bundle_hash"]
        del missing_authored["card"]["job"]
        drafts.append((missing_authored, "$.card: missing job"))
        for draft, error in drafts:
            with self.subTest(error=error):
                result = self.call("validate", self.save(draft), success=False)
                self.assertIn(error, result.stderr)
                self.assertNotIn("python -m benchprime prepare", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_unknown_and_wrong_document_types_are_not_preparation_candidates(self):
        for kind in ("unknown", "evaluation_design_brief", "repeatability_intake", None):
            with self.subTest(kind=kind):
                draft = copy.deepcopy(self.pack)
                draft["document_type"] = kind
                result = self.call("validate", self.save(draft), success=False)
                self.assertNotIn("python -m benchprime prepare", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_output_new_writes_utf8_lf_and_preserves_existing_files(self):
        from benchprime.cli import output_new
        destination = self.work / "lf.txt"
        output_new(destination, "caf\u00e9\nsecond\n")
        self.assertEqual(destination.read_bytes(), b"caf\xc3\xa9\nsecond\n")
        with self.assertRaisesRegex(ValueError, "new filename"):
            output_new(destination, "replacement\n")
        self.assertEqual(destination.read_bytes(), b"caf\xc3\xa9\nsecond\n")

    def test_json_export_is_lf_delimited(self):
        destination = self.work / "candidates.jsonl"
        self.call("export", SAMPLE, "--output", destination)
        payload = destination.read_bytes()
        self.assertNotIn(b"\r", payload)
        self.assertEqual(payload.count(b"\n"), 12)

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

    def test_collection_help_describes_complete_in_place_checks(self):
        output = self.work / "help.html"
        self.call("render", SAMPLE, "--output", output)
        text = output.read_text(encoding="utf-8")
        self.assertIn('including shared rules, are listed above.', text)
        self.assertNotIn('rules listed on <a href="#overview">Overview</a>', text)
        self.assertNotIn("rules listed on Start here.", text)

    def test_legacy_help_uses_the_visible_start_here_label(self):
        from benchprime import design, render
        model = design.project(self.pack)
        model.pop("collection")
        text = render.render_html(model)
        self.assertIn('rules listed on <a href="#overview">Start here</a>', text)

    def test_text_observations_are_readable_and_html_escaped(self):
        from benchprime import design, render
        model = design.project(self.pack)
        observations = model["cases"][0]["input"]["case"]["observations"]
        observations["meeting_notes"] = "First speaker: <script>unsafe</script>\nSecond speaker: agreed."
        observations["extra_values"] = {"number": 2, "label": "<unsafe>"}
        text = render.render_html(model)
        self.assertIn("<h4>Meeting notes</h4><pre>First speaker: &lt;script&gt;unsafe&lt;/script&gt;\nSecond speaker: agreed.</pre>", text)
        self.assertIn("<h4>Extra values</h4><pre>", text)
        self.assertIn("&lt;unsafe&gt;", text)
        self.assertNotIn("<script>unsafe</script>", text)

    def test_markdown_source_notes_include_non_document_observations(self):
        from benchprime import design, render
        model = design.project(self.pack)
        case = model["cases"][0]
        case["input"]["case"]["observations"]["meeting_notes"] = "One: proposed.\nTwo: <agreed>."
        case["input"]["case"]["observations"]["extra_values"] = {"number": 2}
        source_section = render.case_markdown(case).split("## Source notes", 1)[1].split("## Task rules", 1)[0]
        self.assertIn("### Meeting notes\nOne: proposed.\nTwo: &lt;agreed&gt;.", source_section)
        self.assertIn('### Extra values\n{\n  "number": 2\n}', source_section)

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
        self.assertIn("docs/first-session.md", kickoff)
        self.assertIn("STOP after this design checkpoint", kickoff)
        self.assertIn("Do not write cases or criteria until I approve", kickoff)
        self.assertIn("Default to author-assisted provenance", kickoff)
        self.assertIn("not a software-enforced pause or isolation gate", kickoff)

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

    def test_intake_import_preserves_exact_bytes_metadata_and_immutable_retry(self):
        intake = json.loads((ROOT / "examples" / "ticket-triage" / "intake.json").read_text(encoding="utf-8"))
        intake["brief_id"] = "IMPORT-ROUNDTRIP"
        intake["revision"] = "revision-seven"
        intake["target"]["input_shape"] = "A JSON envelope with ticket, locale and a policy revision."
        intake["sources"][0]["provenance"] = "permissioned"
        intake["sources"][0]["authority"]["basis"] = "A declared routing rule, not inferred from examples."
        intake["sources"][0]["rights"]["basis"] = "Processing allowed for this local fictional fixture only."
        intake["sources"][0]["text"] += "\r\nKeep the original caf\u00e9 spelling.\nEnd."
        for bom, line_ending in ((b"", "\n"), (b"\xef\xbb\xbf", "\r\n")):
            with self.subTest(bom=bom, line_ending=line_ending):
                raw = bom + (json.dumps(intake, ensure_ascii=False, indent=3).replace("\n", line_ending)
                             + line_ending).encode("utf-8")
                source = self.work / ("intake-bom.json" if bom else "intake-lf.json")
                source.write_bytes(raw)
                destination = self.work / ("import-bom" if bom else "import-lf")
                result = json.loads(self.call("start", destination, "--from-intake", source).stdout)
                imported = destination / "imported-intake.json"
                self.assertTrue(imported.is_file())
                self.assertEqual(imported.read_bytes(), raw)
                self.assertEqual(result["imported_intake"], str(imported))
                self.assertFalse(result["generation_started"])
                self.assertEqual(result["files_created"],
                                 len([path for path in destination.rglob("*") if path.is_file()]))
                self.assertEqual(result["files_created"], 3 + len(intake["sources"]))
                task_path = destination / "task.md"
                task = task_path.read_text(encoding="utf-8")
                kickoff = (destination / "KICKOFF.md").read_text(encoding="utf-8")
                for text in (task, kickoff):
                    self.assertIn("imported-intake.json", text)
                    self.assertIn("immutable", text)
                    self.assertIn("new current intake", text)
                for value in (intake["brief_id"], intake["revision"], intake["schema_version"],
                              intake["target"]["input_shape"], intake["sources"][0]["provenance"],
                              intake["sources"][0]["authority"]["basis"], intake["sources"][0]["rights"]["basis"]):
                    self.assertIn(value, task)
                sources = sorted((destination / "sources").glob("*.txt"))
                self.assertEqual(sources[0].read_bytes(), intake["sources"][0]["text"].encode("utf-8"))
                task_path.write_bytes(b"# Edited task\nUse a new policy.\n")
                before_retry = {p.relative_to(destination): p.read_bytes()
                                for p in destination.rglob("*") if p.is_file()}
                self.call("start", destination, "--from-intake", source, success=False)
                self.assertEqual(before_retry, {p.relative_to(destination): p.read_bytes()
                                               for p in destination.rglob("*") if p.is_file()})
                self.assertEqual(source.read_bytes(), raw)

    def test_null_input_shape_remains_explicitly_unspecified(self):
        intake = json.loads((ROOT / "examples" / "ticket-triage" / "intake.json").read_text(encoding="utf-8"))
        intake["target"]["input_shape"] = None
        destination = self.work / "unspecified-input"
        self.call("start", destination, "--from-intake", self.save(intake))
        task = (destination / "task.md").read_text(encoding="utf-8")
        self.assertIn("## Input shape", task)
        self.assertIn("null", task)
        self.assertIn("unspecified", task.lower())

    def test_unimported_workspaces_do_not_claim_an_import(self):
        task = self.work / "original.md"
        task.write_bytes(b"# Original\n")
        for name, options in (("blank", ()), ("task", ("--task", task))):
            with self.subTest(name=name):
                destination = self.work / name
                result = json.loads(self.call("start", destination, *options).stdout)
                self.assertEqual(result["files_created"], 2)
                self.assertNotIn("imported_intake", result)
                self.assertFalse((destination / "imported-intake.json").exists())

    def test_help_explains_command_contracts_and_limits(self):
        expected = {
            (): ("AGENTS.md", "no model generation", "structural"),
            ("start",): ("repeatability_intake", "imported-intake.json", "unchanged", "new directory"),
            ("validate",): ("evaluation_design_brief", "evaluation_design_pack", "repeatability_brief",
                            "structural", "semantic", "prepare"),
            ("prepare",): ("evaluation_design_pack", "derived", "new filename"),
            ("freeze",): ("repeatability_intake", "repeatability_brief", "new filename"),
            ("references",): ("repeatability_brief", "authority", "new filename"),
            ("inspect",): ("evaluation_design_pack", "coverage"),
            ("render",): ("evaluation_design_pack", "HTML", "grading", "new filename"),
            ("export",): ("evaluation_design_pack", "one-based", "blocked", "reserved",
                          "JSONL", "input", "target", "case_id", "new filename"),
            ("catalog",): ("patterns", "principles"),
        }
        for command, phrases in expected.items():
            with self.subTest(command=command):
                text = " ".join(self.call(*command, "--help").stdout.split())
                for phrase in (*phrases, "AGENTS.md", "no model generation"):
                    self.assertIn(phrase, text)

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
