import unittest

from scripts.classify_dictionary import classify_entries, classify_entry


class ClassifyDictionaryTests(unittest.TestCase):
    def test_simple_word_with_example_is_beginner_candidate(self):
        entry = {
            "id": "000100_нарн",
            "lemma": "нарн",
            "phonetic": "нарна",
            "pos": None,
            "senses": [
                {
                    "num": 1,
                    "def": "солнце",
                    "examples": [{"kal": "нарн һарв", "rus": "солнце взошло"}],
                }
            ],
            "aliases": [],
        }

        tags = classify_entry(entry)

        self.assertIn("beginner_candidate", tags)
        self.assertIn("has_examples", tags)
        self.assertIn("has_phonetic", tags)
        self.assertNotIn("grammar_form", tags)

    def test_grammar_reference_is_not_beginner_candidate(self):
        entry = {
            "id": "000200_аавин",
            "lemma": "аавин",
            "phonetic": None,
            "pos": "род. п. от",
            "senses": [{"num": 1, "def": "род. п. от аав", "examples": []}],
            "aliases": [],
        }

        tags = classify_entry(entry)

        self.assertIn("grammar_form", tags)
        self.assertNotIn("beginner_candidate", tags)

    def test_cultural_markers_are_detected(self):
        entry = {
            "id": "000300_әәл",
            "lemma": "әәл",
            "phonetic": None,
            "pos": "посл.",
            "senses": [
                {
                    "num": 1,
                    "def": "аул, хотон, селение",
                    "examples": [
                        {"kal": "әәл улсин цоорг негн болдг", "rus": "у соседей прорубь бывает одна <посл.>"},
                        {"kal": "Алтн Чееҗ келв", "rus": "сказал Алтан Чеджи <Джангар>"},
                        {"kal": "хур орлһн", "rus": "дождь <загадка>"},
                        {"kal": "тенд әмтә юмн уга", "rus": "там не было ничего живого <фольк.>"},
                    ],
                }
            ],
            "aliases": [],
        }

        tags = classify_entry(entry)

        self.assertIn("proverb", tags)
        self.assertIn("dzhangar", tags)
        self.assertIn("riddle", tags)
        self.assertIn("folklore", tags)
        self.assertIn("cultural_candidate", tags)

    def test_multiword_and_wiktionary_source_are_detected(self):
        entry = {
            "id": "022900_Әрәсән Федерац",
            "lemma": "Әрәсән Федерац",
            "phonetic": None,
            "pos": "proper noun",
            "senses": [{"num": 1, "def": "Российская Федерация", "examples": []}],
            "aliases": [],
            "source": "ruwikt",
        }

        tags = classify_entry(entry)

        self.assertIn("multiword_lemma", tags)
        self.assertIn("source_ruwikt", tags)

    def test_classify_entries_returns_tag_records_and_counts(self):
        entries = [
            {
                "id": "1",
                "lemma": "нарн",
                "phonetic": None,
                "pos": None,
                "senses": [{"num": 1, "def": "солнце", "examples": []}],
                "aliases": [],
            },
            {
                "id": "2",
                "lemma": "аавин",
                "phonetic": None,
                "pos": "род. п. от",
                "senses": [{"num": 1, "def": "род. п. от аав", "examples": []}],
                "aliases": [],
            },
        ]

        records, stats = classify_entries(entries)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["source_id"], "1")
        self.assertIn("beginner_candidate", records[0]["tags"])
        self.assertEqual(stats["entries"], 2)
        self.assertEqual(stats["tag_counts"]["grammar_form"], 1)


if __name__ == "__main__":
    unittest.main()
