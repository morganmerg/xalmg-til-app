import unittest

from scripts.build_learning_targets import (
    TARGET_CATEGORIES,
    build_learning_targets,
    definition_matches_target,
    flatten_targets,
    normalize_russian,
)


class BuildLearningTargetsTests(unittest.TestCase):
    def test_target_categories_are_300_unique_slots(self):
        self.assertEqual(len(TARGET_CATEGORIES), 12)
        self.assertTrue(all(len(words) == 25 for words in TARGET_CATEGORIES.values()))

        targets = flatten_targets(TARGET_CATEGORIES)
        normalized = [normalize_russian(target["target_ru"]) for target in targets]

        self.assertEqual(len(targets), 300)
        self.assertEqual(len(set(normalized)), 300)
        self.assertEqual(targets[0]["id"], "lt_0001")
        self.assertEqual(targets[-1]["id"], "lt_0300")

    def test_definition_matching_uses_words_not_substrings(self):
        self.assertTrue(definition_matches_target("отец, папа", "отец"))
        self.assertTrue(definition_matches_target("чай", "чай"))
        self.assertTrue(definition_matches_target("доброе утро", "доброе утро"))
        self.assertTrue(definition_matches_target("нет, не хочу", "не хочу"))
        self.assertFalse(definition_matches_target("редчайший", "чай"))
        self.assertFalse(definition_matches_target("подниматься", "мать"))
        self.assertFalse(definition_matches_target("нет, не хочу", "хочу"))

    def test_build_learning_targets_matches_best_dictionary_entries(self):
        entries = [
            {
                "id": "001_аав",
                "lemma": "аав",
                "phonetic": "аав",
                "senses": [
                    {
                        "def": "отец, папа",
                        "examples": [{"kal": "аав ирв", "rus": "отец пришёл"}],
                    }
                ],
            },
            {
                "id": "002_чай_noise",
                "lemma": "noise",
                "senses": [{"def": "редчайший", "examples": []}],
            },
            {
                "id": "003_ця",
                "lemma": "ця",
                "senses": [{"def": "чай", "examples": []}],
            },
        ]
        tag_index = {
            "001_аав": {"beginner_candidate", "has_examples", "has_phonetic"},
            "002_чай_noise": {"beginner_candidate"},
            "003_ця": {"beginner_candidate"},
        }
        targets = [
            {"id": "lt_0001", "category": "family_people", "target_ru": "отец"},
            {"id": "lt_0002", "category": "food_drink", "target_ru": "чай"},
            {"id": "lt_0003", "category": "greetings_politeness", "target_ru": "пожалуйста"},
        ]

        rows, stats = build_learning_targets(entries, tag_index, targets)

        self.assertEqual(rows[0]["match_status"], "matched")
        self.assertEqual(rows[0]["source_id"], "001_аав")
        self.assertEqual(rows[0]["lemma"], "аав")
        self.assertEqual(rows[0]["example"], {"kal": "аав ирв", "rus": "отец пришёл"})

        self.assertEqual(rows[1]["match_status"], "matched")
        self.assertEqual(rows[1]["source_id"], "003_ця")

        self.assertEqual(rows[2]["match_status"], "needs_manual_match")
        self.assertIsNone(rows[2]["source_id"])
        self.assertEqual(stats["targets"], 3)
        self.assertEqual(stats["matched"], 2)
        self.assertEqual(stats["needs_manual_match"], 1)

    def test_matched_row_uses_the_matching_definition(self):
        entries = [
            {
                "id": "001_билә",
                "lemma": "билә",
                "senses": [
                    {"def": "1. связка", "examples": []},
                    {"def": "хочу", "examples": [{"kal": "би сурх билә", "rus": "я хочу учиться"}]},
                ],
            }
        ]
        targets = [{"id": "lt_0001", "category": "greetings_politeness", "target_ru": "хочу"}]

        rows, _stats = build_learning_targets(entries, {"001_билә": {"beginner_candidate"}}, targets)

        self.assertEqual(rows[0]["match_status"], "matched")
        self.assertEqual(rows[0]["translation"], "хочу")
        self.assertEqual(rows[0]["example"], {"kal": "би сурх билә", "rus": "я хочу учиться"})

    def test_negative_phrase_does_not_fill_positive_target(self):
        entries = [
            {
                "id": "001_билә",
                "lemma": "билә",
                "senses": [{"def": "нет, не хочу", "examples": []}],
            }
        ]
        tag_index = {"001_билә": {"beginner_candidate"}}
        targets = [
            {"id": "lt_0001", "category": "greetings_politeness", "target_ru": "хочу"},
            {"id": "lt_0002", "category": "greetings_politeness", "target_ru": "не хочу"},
        ]

        rows, stats = build_learning_targets(entries, tag_index, targets)

        self.assertEqual(rows[0]["match_status"], "needs_manual_match")
        self.assertEqual(rows[1]["match_status"], "matched")
        self.assertEqual(stats["matched"], 1)

    def test_wiktionary_source_does_not_auto_match_target(self):
        entries = [
            {
                "id": "001_wikt",
                "lemma": "седнәв",
                "senses": [{"def": "хочу", "examples": []}],
            }
        ]
        targets = [{"id": "lt_0001", "category": "greetings_politeness", "target_ru": "хочу"}]

        rows, stats = build_learning_targets(entries, {"001_wikt": {"source_ruwikt"}}, targets)

        self.assertEqual(rows[0]["match_status"], "needs_manual_match")
        self.assertEqual(stats["matched"], 0)


if __name__ == "__main__":
    unittest.main()
