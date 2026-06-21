import importlib
import json
import tempfile
import unittest
from pathlib import Path


class BuildSqliteTagsTests(unittest.TestCase):
    def test_import_does_not_delete_existing_database(self):
        db_path = Path("assets/db/dictionary.db")
        self.assertTrue(db_path.exists(), "dictionary.db must exist before import safety check")
        before_size = db_path.stat().st_size

        importlib.import_module("scripts.build_sqlite")

        self.assertTrue(db_path.exists(), "importing build_sqlite must not delete dictionary.db")
        self.assertEqual(db_path.stat().st_size, before_size)

    def test_load_tag_map_indexes_tags_by_source_id(self):
        module = importlib.import_module("scripts.build_sqlite")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dictionary.tags.json"
            path.write_text(
                json.dumps(
                    [
                        {"source_id": "000001_аав", "tags": ["beginner_candidate", "has_examples"]},
                        {"source_id": "000002_аавин", "tags": ["grammar_form"]},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            tag_map = module.load_tag_map(path)

        self.assertEqual(tag_map["000001_аав"], ["beginner_candidate", "has_examples"])
        self.assertEqual(tag_map["000002_аавин"], ["grammar_form"])


if __name__ == "__main__":
    unittest.main()
