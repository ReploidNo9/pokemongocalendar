import json, unittest
from pathlib import Path
from datetime import datetime, date

ROOT = Path(__file__).resolve().parents[1]

class EventDataTests(unittest.TestCase):
    def setUp(self):
        self.items = json.loads((ROOT / "data/events.json").read_text(encoding="utf-8"))

    def test_uids_are_unique(self):
        uids = [x["uid"] for x in self.items]
        self.assertEqual(len(uids), len(set(uids)))

    def test_dates_parse(self):
        for item in self.items:
            if item["all_day"]:
                date.fromisoformat(item["start"])
                date.fromisoformat(item["end"])
            else:
                datetime.fromisoformat(item["start"])
                datetime.fromisoformat(item["end"])

    def test_source_urls_are_official(self):
        for item in self.items:
            self.assertTrue(item["url"].startswith("https://pokemongo.com/"))

if __name__ == "__main__":
    unittest.main()
