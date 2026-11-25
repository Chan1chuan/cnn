import io
import json
import unittest

from audit import audit


HEADER = "speaker\tutterance\ttext\n"


class AuditTest(unittest.TestCase):
    def test_exact_keyword_counts(self):
        rows = ["s\tu1\tGO, go!", "s\tu2\tstopwatch", "s\tu3\tgo stop",
                "s\tu4\tPlease stop.", "s\tu5\tCAFÉ."]
        result = audit(io.StringIO(HEADER + "\n".join(rows)),
                       ["go", "stop", "café"], "example", 0)
        self.assertEqual(result["splits"]["train"], {
            "rows": 5, "unmatched": 1, "ambiguous": 1, "speakers": 1,
            "keywords": {"go": 1, "stop": 1, "café": 1},
        })

    def test_speaker_split_and_input_order(self):
        rows = [f"speaker-{i}\tid-{i}-{j}\tprivate go"
                for i in range(12) for j in range(3)]

        def run(data):
            return audit(io.StringIO(HEADER + "\n".join(data)), ["go"], "example", 50)

        report = run(rows)
        self.assertEqual(report, run(reversed(rows)))
        self.assertEqual(sum(split["speakers"] for split in report["splits"].values()), 12)
        for split in report["splits"].values():
            self.assertGreater(split["speakers"], 0)
            self.assertEqual(split["keywords"]["go"], split["speakers"] * 3)
        for item in ("speaker-0", "id-0-0", "private"):
            self.assertNotIn(item, json.dumps(report))

    def test_malformed_and_duplicate_rows(self):
        with self.assertRaisesRegex(ValueError, "Wrong number of columns"):
            audit(io.StringIO(HEADER + "s\tu"), ["go"], "example", 40)
        with self.assertRaisesRegex(ValueError, "Duplicate utterance ID at line 3"):
            audit(io.StringIO(HEADER + "s\tu\tgo\ns2\tu\tstop"), ["go"], "example", 40)


if __name__ == "__main__":
    unittest.main()
