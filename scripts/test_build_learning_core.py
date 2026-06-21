import unittest

from scripts.build_learning_core import (
    build_learning_core,
    category_for_entry,
    is_learning_candidate,
    load_tag_index,
)


class BuildLearningCoreTests(unittest.TestCase):
    def test_load_tag_index_uses_source_id(self):
        records = [
            {"source_id": "001_нарн", "tags": ["beginner_candidate", "has_examples"]},
            {"source_id": "002_аавин", "tags": ["grammar_form"]},
        ]

        index = load_tag_index(records)

        self.assertEqual(index["001_нарн"], {"beginner_candidate", "has_examples"})
        self.assertEqual(index["002_аавин"], {"grammar_form"})

    def test_rejects_non_learning_entries(self):
        grammar_entry = {
            "id": "001_аавин",
            "lemma": "аавин",
            "senses": [{"def": "род. п. от аав", "examples": []}],
        }
        archaic_entry = {
            "id": "002_әвә",
            "lemma": "әвә",
            "senses": [{"def": "устаревшее слово", "examples": []}],
        }

        self.assertFalse(is_learning_candidate(grammar_entry, {"beginner_candidate", "grammar_form"}))
        self.assertFalse(is_learning_candidate(archaic_entry, {"beginner_candidate", "archaic"}))
        self.assertFalse(is_learning_candidate(grammar_entry, {"has_examples"}))

    def test_assigns_category_from_russian_definition(self):
        family_entry = {
            "id": "003_аав",
            "lemma": "аав",
            "senses": [{"def": "отец, папа", "examples": []}],
        }
        food_entry = {
            "id": "004_ця",
            "lemma": "ця",
            "senses": [{"def": "чай", "examples": []}],
        }

        self.assertEqual(category_for_entry(family_entry), "family_people")
        self.assertEqual(category_for_entry(food_entry), "food_drink")

    def test_cultural_candidate_can_still_enter_core_with_note(self):
        entry = {
            "id": "005_нарн",
            "lemma": "нарн",
            "phonetic": "нарна",
            "senses": [
                {
                    "def": "солнце",
                    "examples": [{"kal": "нарн һарв", "rus": "солнце взошло"}],
                }
            ],
        }
        tags = {"beginner_candidate", "cultural_candidate", "has_examples", "has_phonetic"}

        core, stats = build_learning_core([entry], {"005_нарн": tags}, target_max=10)

        self.assertEqual(len(core), 1)
        self.assertEqual(core[0]["id"], "lc_0001")
        self.assertEqual(core[0]["source_id"], "005_нарн")
        self.assertEqual(core[0]["category"], "steppe_nature")
        self.assertEqual(core[0]["review_status"], "candidate")
        self.assertEqual(core[0]["audio_status"], "needed")
        self.assertIn("has_cultural_markers", core[0]["notes"])
        self.assertEqual(stats["selected"], 1)

    def test_build_learning_core_is_capped_and_grouped(self):
        entries = []
        tag_index = {}
        for i in range(8):
            source_id = f"{i:03d}_нарн{i}"
            entries.append(
                {
                    "id": source_id,
                    "lemma": f"нарн{i}",
                    "senses": [{"def": "солнце", "examples": []}],
                    "aliases": [],
                }
            )
            tag_index[source_id] = {"beginner_candidate"}

        core, stats = build_learning_core(entries, tag_index, target_max=5)

        self.assertEqual(len(core), 5)
        self.assertEqual(stats["selected"], 5)
        self.assertEqual(stats["by_category"]["steppe_nature"], 5)
        self.assertTrue(all(item["category"] == "steppe_nature" for item in core))


if __name__ == "__main__":
    unittest.main()
