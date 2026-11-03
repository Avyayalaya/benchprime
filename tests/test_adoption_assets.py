"""Verify demo meaning and asset integrity; audience impact remains unmeasured."""
import base64
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"


class AdoptionAssetsTests(unittest.TestCase):
    def figure(self, name):
        return ET.parse(ROOT / "assets" / (name + ".svg")).getroot()

    def text(self, name):
        return " ".join(" ".join(t.itertext())
                        for t in self.figure(name).findall(".//" + SVG + "text"))

    def test_shareable_frames_preserve_attribution_and_dimensions(self):
        for name in [*(f"meeting-demo-{i:02}" for i in range(1, 6)), "social-preview"]:
            with self.subTest(asset=name):
                root = self.figure(name)
                expected = (1280, 640) if name == "social-preview" else (1080, 1080)
                self.assertEqual((int(root.attrib["width"]), int(root.attrib["height"])), expected)
                self.assertTrue(root.find(SVG + "title").text)
                self.assertTrue(root.find(SVG + "desc").text)
                text = self.text(name)
                self.assertIn("BenchPrime", text)
                self.assertIn("Fictional authored example", text)
                self.assertIn("No target run", text)
                png = (ROOT / "assets" / (name + ".png")).read_bytes()
                self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", png[16:24]), expected)
                self.assertFalse(root.findall(".//" + SVG + "script"))
                for element in root.iter():
                    for attr, value in element.attrib.items():
                        if attr.endswith("href") and not value.startswith("#"):
                            self.assertTrue(value.startswith("data:image/png;base64,"))
                            decoded = base64.b64decode(value.split(",", 1)[1], validate=True)
                            self.assertEqual(decoded[:8], b"\x89PNG\r\n\x1a\n")

    def test_demo_preserves_the_policy_backed_distinction_and_invariants(self):
        self.assertIn("Could we send the pricing brief Friday?", self.text("meeting-demo-01"))
        self.assertIn("I'll check the cost figures by Thursday.", self.text("meeting-demo-01"))
        self.assertIn("The first case includes Leo's task.",
                      " ".join(self.text("meeting-demo-02").split()))
        self.assertIn("Owner: Leo     Due: Thursday", self.text("meeting-demo-02"))
        self.assertIn("I'll send the pricing brief Friday.", self.text("meeting-demo-03"))
        self.assertIn("Maya | Friday", self.text("meeting-demo-03"))
        self.assertIn("Leo | Thursday", self.text("meeting-demo-03"))
        self.assertIn("Alternative excerpt.", self.text("meeting-demo-03"))
        for phrase in ("Check the cost figures", "Verify the cost figures",
                       "Owner: Leo.", "Deadline: Thursday."):
            self.assertIn(phrase, self.text("meeting-demo-04"))
        self.assertIn("Conditional commitments need more cases.", self.text("meeting-demo-05"))
        self.assertIn("Excerpt from the actual casebook", self.text("meeting-demo-05"))


if __name__ == "__main__":
    unittest.main()
