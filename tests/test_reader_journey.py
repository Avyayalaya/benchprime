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
                if urlsplit(target).scheme:
                    continue
                relative, _, fragment = unquote(target).partition("#")
                destination = (path.parent / relative).resolve() if relative else path
                with self.subTest(file=str(path.relative_to(ROOT)), target=target):
                    self.assertTrue(destination.exists())
                    self.assertTrue(destination.is_relative_to(ROOT))
                    if fragment and destination.suffix == ".md":
                        self.assertIn(fragment, heading_ids(destination))

    def test_readme_shows_actual_output_before_method_depth(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(text.index("assets/meeting-actions-case.png"),
                        text.index("## How the evaluation is built"))
        self.assertLess(text.index("examples/meeting-actions/README.md"),
                        text.index("## How the evaluation is built"))
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

    def test_readme_has_one_primary_start_and_early_product_output(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        first_link = re.search(r"\]\(([^)]+)\)", text).group(1)
        self.assertEqual(first_link, "START_HERE.md")
        self.assertLess(text.index("assets/meeting-actions-case.png"), text.index("```"))
        visible = re.sub(r"<details>.*?</details>", "", prose(ROOT / "README.md"), flags=re.S)
        visible = re.sub(r"<[^>]+>", "", visible)
        self.assertLessEqual(len(visible.split()), 450)
        start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## [123]\. (.+)$", start, re.M)
        self.assertEqual(headings, ["Describe the job", "Review the test plan",
                                    "Build and inspect the evaluation"])

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


if __name__ == "__main__":
    unittest.main()
