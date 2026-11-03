"""Offline reader-path checks; these do not establish human usability."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def prose(path):
    return re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)


def heading_ids(path):
    text = prose(path)
    counts = Counter()
    result = set(re.findall(r'<a\s+[^>]*?(?:id|name)="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", text, re.M):
        slug = re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        n = counts[slug]
        counts[slug] += 1
        result.add(slug + (f"-{n}" if n else ""))
    return result


class MapDisclosure(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.details = 0
        self.maps = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "details":
            self.details += 1
        attrs = dict(attrs)
        if tag == "img" and "methodology-" in attrs.get("src", ""):
            self.maps.append((self.details, attrs.get("alt", "")))

    def handle_endtag(self, tag):
        if tag == "details":
            self.details -= 1


class ReaderJourneyTests(unittest.TestCase):
    def test_reader_links_and_image_paths_resolve(self):
        paths = [ROOT / "README.md", ROOT / "START_HERE.md", ROOT / "AGENTS.md",
                 ROOT / "CONTRIBUTING.md",
                 ROOT / "assets" / "README.md", ROOT / "packs" / "README.md",
                 *(ROOT / "docs").glob("*.md"),
                 *(ROOT / "examples" / "meeting-actions").glob("*.md")]
        for path in paths:
            text = prose(path)
            targets = re.findall(r"\]\(([^)]+)\)", text)
            targets += re.findall(r'(?:src|srcset)="([^"]+)"', text)
            for target in targets:
                parsed = urlsplit(target)
                if parsed.scheme:
                    continue
                relative, fragment = unquote(parsed.path), unquote(parsed.fragment)
                destination = (path.parent / relative).resolve() if relative else path
                with self.subTest(file=str(path.relative_to(ROOT)), target=target):
                    self.assertTrue(destination.exists())
                    self.assertTrue(destination.is_relative_to(ROOT))
                    if fragment and destination.suffix == ".md":
                        self.assertIn(fragment, heading_ids(destination))

    def test_readme_shows_actual_output_before_method_depth(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(text.index("assets/meeting-actions-case.png"),
                        text.index("## How the cases are designed"))
        self.assertLess(text.index("examples/meeting-actions/README.md"),
                        text.index("## How the cases are designed"))
        self.assertIn("authored fictional", text)
        self.assertIn("authored notes and proposed checks", text)
        self.assertIn("No target model was run.", text)
        headings = re.findall(r"^(#{1,6})\s+", prose(ROOT / "README.md"), re.M)
        for previous, current in zip(headings, headings[1:]):
            self.assertLessEqual(len(current), len(previous) + 1)

    def test_full_method_maps_remain_available_with_disclosure(self):
        readme = MapDisclosure((ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(len(readme.maps), 3)
        self.assertTrue(all(depth > 0 and alt for depth, alt in readme.maps))
        method = MapDisclosure((ROOT / "docs" / "methodology.md").read_text(encoding="utf-8"))
        self.assertEqual(len(method.maps), 3)
        self.assertTrue(all(alt for _, alt in method.maps))

    def test_readme_offers_readable_proof_before_creation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        first_link = re.search(r"\]\(([^)]+)\)", text).group(1)
        self.assertEqual(first_link, "examples/meeting-actions/README.md")
        self.assertLess(text.index("assets/meeting-actions-case.png"), text.index("```"))
        visible = re.sub(r"<details>.*?</details>", "", prose(ROOT / "README.md"), flags=re.S)
        visible = re.sub(r"<[^>]+>", "", visible)
        self.assertLessEqual(len(visible.split()), 500)
        start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## [123]\. (.+)$", start, re.M)
        self.assertEqual(headings, ["Describe the job", "Review the test plan",
                                    "Build and inspect the evaluation"])

    def test_start_keeps_both_messages_and_approval_in_one_guide(self):
        start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("**First message**", start)
        self.assertIn("**Second message**", start)
        self.assertIn("The design is approved for the stated scope.", start)
        self.assertIn("Right rules?", start)
        self.assertIn("Right distinctions?", start)
        self.assertIn("Permitted sources?", start)
        self.assertIn("Python does not enforce it.", start)
        self.assertIn("separately approved process", start)
        self.assertLess(start.index("stop for my review"),
                        start.index("The design is approved"))

    def test_example_is_readable_without_following_an_html_link(self):
        example = ROOT / "examples" / "meeting-actions" / "README.md"
        text = example.read_text(encoding="utf-8")
        self.assertIn("Six cases you can inspect here", text)
        self.assertIn("open it locally", text)
        self.assertIn("casebook.html?raw=1", text)
        self.assertIn("alternative scenarios", text)
        for case in range(1, 7):
            self.assertIn(f"MA-{case:03}", text)
        self.assertIn('"owner": null, "due": "Tuesday"', text)
        self.assertIn("No target model was run.", text.replace("no target model was run.",
                                                             "No target model was run."))

    def test_first_and_repeat_use_boundaries_remain_explicit(self):
        first = (ROOT / "docs" / "first-session.md").read_text(encoding="utf-8")
        repeat = (ROOT / "docs" / "reuse-an-evaluation.md").read_text(encoding="utf-8")
        self.assertIn("stop after `collection-design.md`", first)
        self.assertIn("assisted draft", first)
        self.assertIn("opaque ID", first)
        self.assertIn("software-enforced", first)
        self.assertIn("Target execution is external", repeat)
        self.assertIn("new typed", repeat)
        self.assertIn("authored illustrations", repeat)

    def test_agent_route_states_assisted_and_separated_stage_contracts(self):
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        workflow = (ROOT / "workflows" / "generate.md").read_text(encoding="utf-8")
        self.assertIn("Default: author-assisted in the current conversation.", agent)
        self.assertIn("STOP.", agent)
        self.assertIn("generation_started: false", agent)
        self.assertIn("imported-intake.json", agent)
        self.assertIn("byte-exact", agent)
        self.assertIn("Choose the mode once", workflow)
        self.assertGreaterEqual(workflow.count("**assisted mode**"), 1)
        self.assertGreaterEqual(workflow.count("**separated mode**"), 1)
        self.assertIn("does not require the user to create additional sessions", workflow)
        self.assertIn("withholding the profile inventory", workflow)
        self.assertIn("no blind-derivation claim", workflow)
        self.assertNotIn("For each case, start a fresh context", workflow)

if __name__ == "__main__":
    unittest.main()
