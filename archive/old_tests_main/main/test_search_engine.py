import unittest
from unittest.mock import patch, MagicMock
from src.search_engine import SearchEngine


class TestSearchEngine(unittest.TestCase):

    @patch("src.search_engine.GoogleTranslator")
    @patch("src.search_engine.SentenceTransformer")
    @patch("src.search_engine.BGEM3FlagModel")
    def setUp(self, mock_bgem3, mock_sentence_transformer, mock_translator):
        # Mock BGEM3 model
        self.mock_bgem3_instance = MagicMock()
        mock_bgem3.return_value = self.mock_bgem3_instance

        # Mock SentenceTransformer
        self.mock_sentence_instance = MagicMock()
        mock_sentence_transformer.return_value = self.mock_sentence_instance

        # Mock Translator
        self.mock_translator_instance = MagicMock()
        mock_translator.return_value = self.mock_translator_instance

        # Initialize SearchEngine
        self.engine = SearchEngine(device="cpu")

        # Mock the internal methods for tests
        self.engine._search = MagicMock(return_value=[
            {
                'id': 1,
                'title': 'AI Thesis',
                'abstract': 'About deep learning',
                'authors': ['John Doe', 'Jane Doe'],
                'distance': 0.2,
                'url': 'http://example.com'
            }
        ])

    def test_search_thesis_valid_option(self):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        result = self.engine.search_thesis(
            "deep learning", top_k=1, option="bgem3")
        self.engine._encode_query.assert_called_once()
        self.engine._search.assert_called_once()
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['title'], 'AI Thesis')

    def test_search_thesis_invalid_option(self):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        with self.assertRaises(ValueError):
            self.engine.search_thesis("test", option="invalid")

    def test_search_advisor_grouping_and_sorting(self):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        # _search returns 2 publications with same authors
        self.engine._search.return_value = [
            {'id': 1, 'title': 'Thesis 1', 'authors': [
                'John'], 'distance': 0.2, 'url': 'url1'},
            {'id': 2, 'title': 'Thesis 2', 'authors': [
                'John'], 'distance': 0.1, 'url': 'url2'}
        ]
        advisors = self.engine.search_advisor("AI")
        self.assertTrue(any(a['name'] == 'John' for a in advisors))
        self.assertGreaterEqual(advisors[0]['publication_count'], 1)

    def test_search_advisor_2_similarity_calculation(self):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        self.engine._search.return_value = [
            {'id': 1, 'title': 'Paper 1', 'authors': [
                'Alice'], 'distance': 0.5, 'url': 'x'},
            {'id': 2, 'title': 'Paper 2', 'authors': [
                'Bob'], 'distance': 0.1, 'url': 'x'}
        ]
        results = self.engine.search_advisor_2("test")
        self.assertIsInstance(results, list)
        self.assertIn('relevance_score', results[0])
        self.assertLessEqual(results[0]['relevance_score'], 100)

    @patch("src.search_engine.sqlite3.connect")
    def test_search_advisor_3_combined_score(self, mock_connect):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        # Mock DB connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Scholar", "John", None, None, "url", None)]

        self.engine._get_author_data = MagicMock(
            return_value={'url_picture': 'pic_url'})
        self.engine._search.return_value = [
            {'id': 1, 'title': 'Paper', 'authors': [
                'John'], 'distance': 0.5, 'url': 'url'}
        ]

        results = self.engine.search_advisor_3("AI")
        self.assertTrue(any("combined_score" in r for r in results))
        self.assertEqual(results[0]['url_picture'], 'pic_url')

    @patch("src.search_engine.sqlite3.connect")
    def test_get_all_programs(self, mock_connect):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 'CS', 'url1'), (2, 'IT', 'url2')]

        result = self.engine.get_all_programs()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'CS')

    @patch("src.search_engine.sqlite3.connect")
    def test_get_author_data_custom_url(self, mock_connect):
        self.engine._encode_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "sid", "Liliana", None, None, None, None)]

        result = self.engine._get_author_data("Liliana")
        self.assertIn("url_picture", result)
        self.assertTrue(result["url_picture"].startswith(
            "https://informatics.petra.ac.id/"))

    def test_encode_query_with_bgem3(self):
        mock_model = self.mock_bgem3_instance
        mock_model.encode.return_value = {'dense_vecs': [[0.5, 0.5]]}
        output = self.engine._encode_query("test", mock_model)
        self.assertEqual(output, [0.5, 0.5])


if __name__ == '__main__':
    unittest.main()
