import pytest
import numpy as np
from unittest.mock import MagicMock
from main.sql_faiss.search_utils import (
    get_embedding,
    print_formatted_results,
    update_embeddings_in_batches,
)


def test_get_embedding_returns_none_for_empty_or_none():
    mock_model = MagicMock()
    assert get_embedding("", mock_model) is None
    assert get_embedding(None, mock_model) is None
    mock_model.encode.assert_not_called()


def test_get_embedding_returns_encoded_list():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
    result = get_embedding("hello", mock_model)
    assert result == [0.1, 0.2, 0.3]
    mock_model.encode.assert_called_once_with("hello")


@pytest.fixture
def sample_results():
    return [
        {
            "title": "AI Research Paper",
            "similarity_score": 0.9123,
            "distance": 0.0877,
            "authors": ["Alice", "Bob"],
            "contributors": [
                {"role": "Supervisor", "name": "Dr. Smith"},
                {"role": "Examiner", "name": "Prof. Lee"},
            ],
            "abstract": "Exploring transformer models for AI applications."
        }
    ]


def test_print_formatted_results_empty(capsys):
    print_formatted_results([])
    captured = capsys.readouterr()
    assert "No results found." in captured.out


def test_print_formatted_results_full_output(capsys, sample_results):
    print_formatted_results(sample_results)
    output = capsys.readouterr().out

    assert "Result 1: AI Research Paper" in output
    assert "Similarity: 0.9123" in output
    assert "Distance: 0.0877" in output
    assert "Authors: Alice, Bob" in output
    assert "Contributors:" in output
    assert "Supervisor: Dr. Smith" in output
    assert "Examiner: Prof. Lee" in output
    assert "Abstract: Exploring transformer models" in output


@pytest.mark.parametrize("flag", ["show_authors", "show_contributors", "show_abstract", "show_metrics"])
def test_print_formatted_results_flags(capsys, sample_results, flag):
    kwargs = {flag: False}
    print_formatted_results(sample_results, **kwargs)
    output = capsys.readouterr().out

    if flag == "show_authors":
        assert "Authors:" not in output
    elif flag == "show_contributors":
        assert "Contributors:" not in output
    elif flag == "show_abstract":
        assert "Abstract:" not in output
    elif flag == "show_metrics":
        assert "Similarity:" not in output and "Distance:" not in output


def test_print_formatted_results_missing_info(capsys):
    results = [
        {
            "title": "Empty Fields",
            "similarity_score": 0.5,
            "distance": 0.5,
            "authors": [],
            "contributors": [],
            "abstract": None
        }
    ]
    print_formatted_results(results)
    output = capsys.readouterr().out
    assert "No author information available" in output
    assert "No contributor information available" in output
    assert "No abstract available" in output


def test_print_formatted_results_truncates_long_abstract(capsys):
    results = [
        {
            "title": "Truncated Abstract",
            "similarity_score": 0.9,
            "distance": 0.1,
            "authors": ["John"],
            "contributors": [],
            "abstract": "A" * 400
        }
    ]
    print_formatted_results(results)
    output = capsys.readouterr().out
    assert "..." in output
    assert len(output) < 500


def test_update_embeddings_in_batches_with_no_papers(capsys):
    mock_model = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_db = MagicMock()

    update_embeddings_in_batches(mock_model, mock_cursor, mock_db)
    output = capsys.readouterr().out
    assert "No papers need embeddings" in output
    mock_db.commit.assert_not_called()


def test_update_embeddings_in_batches_processes_batches(capsys):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Title1", "Abstract1"),
        (2, "Title2", "Abstract2"),
    ]

    mock_db = MagicMock()

    update_embeddings_in_batches(
        mock_model, mock_cursor, mock_db, batch_size=1)
    output = capsys.readouterr().out

    assert "Updated embeddings for" in output
    mock_cursor.executemany.assert_called()
    mock_db.commit.assert_called()


def test_update_embeddings_in_batches_rollback_on_error(capsys):
    mock_model = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = Exception("DB error")
    mock_db = MagicMock()

    with pytest.raises(Exception):
        update_embeddings_in_batches(mock_model, mock_cursor, mock_db)
    output = capsys.readouterr().out

    assert "Error during embedding update" in output
    mock_db.rollback.assert_called_once()
