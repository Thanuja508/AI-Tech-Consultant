import unittest

from app.knowledge_base import search_knowledge_base


class TestKnowledgeBrain(unittest.TestCase):

    def test_email_forwarding_returns_results(self):
        results = search_knowledge_base(
            "How do I configure email forwarding?", 3
        )
        self.assertGreater(
            len(results), 0,
            "Expected relevant articles for email forwarding."
        )

    def test_results_have_source_fields(self):
        results = search_knowledge_base(
            "How do I change the color set of my website?", 3
        )

        self.assertGreater(len(results), 0)

        for result in results:
            self.assertIn("title", result)
            self.assertIn("url", result)
            self.assertIn("content", result)
            self.assertTrue(result["title"])
            self.assertTrue(result["url"])

    def test_unrelated_dolphin_question_returns_no_results(self):
        results = search_knowledge_base(
            "How do I train a dolphin to paint a portrait?", 3
        )
        self.assertEqual(
            results, [],
            "Unrelated questions should not return documentation."
        )

    def test_empty_query_returns_no_results(self):
        self.assertEqual(search_knowledge_base(""), [])

    def test_whitespace_query_returns_no_results(self):
        self.assertEqual(search_knowledge_base("   "), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)