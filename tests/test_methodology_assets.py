"""Asset integrity and accessibility checks, not a rating of visual appeal."""
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))


class MethodologyAssetTests(unittest.TestCase):
    def figures(self):
        for name in ("atlas", "depth", "review"):
            for mobile in (False, True):
                stem = "methodology-" + name + ("-mobile" if mobile else "")
                yield stem, mobile, ET.parse(ROOT / "assets" / (stem + ".svg")).getroot()

    def test_paired_assets_have_matching_dimensions_and_accessible_text(self):
        for stem, mobile, root in self.figures():
            with self.subTest(asset=stem):
                width, height = int(root.attrib["width"]), int(root.attrib["height"])
                self.assertEqual(width, 440 if mobile else 1080)
                self.assertEqual(root.attrib["viewBox"], f"0 0 {width} {height}")
                self.assertTrue(root.find(SVG + "title").text)
                self.assertTrue(root.find(SVG + "desc").text)
                png = (ROOT / "assets" / (stem + ".png")).read_bytes()
                self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", png[16:24]), (width, height))
                self.assertFalse(root.findall(".//" + SVG + "script"))
                for element in root.iter():
                    for attr, value in element.attrib.items():
                        if attr.endswith("href"):
                            self.assertTrue(value.startswith("#"))

    def test_text_is_compact_and_has_sufficient_contrast(self):
        for stem, _, root in self.figures():
            with self.subTest(asset=stem):
                texts = root.findall(".//" + SVG + "text")
                visible = " ".join(" ".join(t.itertext()) for t in texts)
                self.assertLessEqual(len(visible.split()), 110)
                self.assertNotIn("opaque ID", visible)
                self.assertNotIn("Criteria writer", visible)
                for text in texts:
                    self.assertGreaterEqual(float(text.attrib["font-size"]), 17)
                    contrast = (luminance("#ffffff") + .05) / (luminance(text.attrib["fill"]) + .05)
                    self.assertGreaterEqual(contrast, 4.5)

    def test_deep_method_and_execution_boundaries_remain_available(self):
        method = (ROOT / "docs" / "methodology.md").read_text(encoding="utf-8")
        self.assertIn("eleven responsibilities", method)
        self.assertIn("opaque ID", method)
        self.assertIn("author-assisted", method)
        self.assertIn("performance results", method)
        self.assertIn("separately approved process", method)

    def test_rubric_matrix_is_scoped_to_the_checked_requirement(self):
        for stem, _, root in self.figures():
            if "review" not in stem:
                continue
            with self.subTest(asset=stem):
                text = " ".join(" ".join(t.itertext())
                                for t in root.findall(".//" + SVG + "text"))
                text = " ".join(text.split())
                self.assertIn("requirement this check covers", text)
                self.assertIn("Meets", text)
                self.assertIn("Violates", text)
                self.assertIn("Other requirements need their own checks.", text)
                self.assertNotIn("Material mistake", text)
        method = (ROOT / "docs" / "methodology.md").read_text(encoding="utf-8")
        self.assertIn("A JSON-format check can", method)
        self.assertIn("the commitment check must catch", method)


if __name__ == "__main__":
    unittest.main()
