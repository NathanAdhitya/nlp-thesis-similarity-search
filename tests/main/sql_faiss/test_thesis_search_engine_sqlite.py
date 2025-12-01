import pytest
import numpy as np
import json
from unittest.mock import MagicMock
from main.sql_faiss.thesis_search_engine_sqlite import ThesisSimilaritySearch


@pytest.fixture
def mock_model():
    mock = MagicMock()
    mock._modules = {'0': MagicMock()}
    mock._modules['0'].auto_model.config.name_or_path = "sentence-transformers/test-model"

    # IMPORTANT: Mock the encode method that get_embedding calls
    mock.encode.return_value = np.array([0.1, 0.2, 0.3])

    return mock


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()

    # Embedding for one paper (3 dimensions)
    embedding = np.array([0.1, 0.2, 0.3]).tolist()

    # Mock the queries in order: papers, authors, contributors
    cursor.fetchall.side_effect = [
        [("p1", "Title A", "Abstract A", json.dumps(embedding))],  # Papers
        [("p1", "Author A")],  # Authors
        [("p1", "Contributor A", "Editor")]  # Contributors
    ]
    return cursor


def test_load_index_and_search(monkeypatch, mock_model, mock_cursor):
    # Patch get_embedding in the SQLITE module where it's imported
    monkeypatch.setattr(
        "main.sql_faiss.thesis_search_engine_sqlite.get_embedding",
        lambda text, model: np.array([0.1, 0.2, 0.3])  # Return numpy array
    )

    # Initialize and load index
    search_engine = ThesisSimilaritySearch(model=mock_model)
    index = search_engine.load_index(mock_cursor)

    assert index is not None
    assert search_engine.index.ntotal == 1
    assert search_engine.paper_ids == ["p1"]
    assert "p1" in search_engine.paper_metadata
    assert search_engine.paper_metadata["p1"]["authors"] == ["Author A"]
    assert search_engine.paper_metadata["p1"]["contributors"][0]["name"] == "Contributor A"

    # Run a search query
    results = search_engine.search("test query", top_k=1)

    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert result["id"] == "p1"
    assert result["similarity_score"] > 0
    assert "distance" in result
