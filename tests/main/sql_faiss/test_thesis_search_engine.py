import pytest
import numpy as np
import json
from unittest.mock import MagicMock
from main.sql_faiss.thesis_search_engine import ThesisSimilaritySearch, SearchEngine


@pytest.fixture
def mock_model():
    mock = MagicMock()
    mock._modules = {'0': MagicMock()}
    mock._modules['0'].auto_model.config.name_or_path = "sentence-transformers/test-model"
    return mock


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    embedding = np.array([0.1, 0.2, 0.3]).tolist()

    cursor.fetchall.side_effect = [
        [("p1", "Title A", "Abstract A", json.dumps(embedding))],  # papers
        [("p1", "Author A")],  # authors
        [("p1", "Contributor A", "Editor")],  # contributors
    ]

    return cursor


def test_load_index_and_search(monkeypatch, mock_model, mock_cursor):
    # Patch get_embedding WHERE IT'S USED, not where it's defined
    monkeypatch.setattr(
        "main.sql_faiss.thesis_search_engine.get_embedding",  # Changed this line
        lambda text, model: [0.1, 0.2, 0.3]
    )

    # Initialize and load FAISS index
    search_engine = ThesisSimilaritySearch(model=mock_model)
    index = search_engine.load_index(mock_cursor)

    # Check index integrity
    assert index is not None
    assert search_engine.index.ntotal == 1
    assert search_engine.paper_ids == ["p1"]

    metadata = search_engine.paper_metadata["p1"]
    assert metadata["title"] == "Title A"
    assert metadata["authors"] == ["Author A"]
    assert metadata["contributors"][0]["name"] == "Contributor A"

    # Search results
    results = search_engine.search("test query", top_k=1)
    assert isinstance(results, list)
    assert len(results) == 1

    result = results[0]
    assert result["id"] == "p1"
    assert "similarity_score" in result
    assert result["similarity_score"] > 0
    assert isinstance(result["distance"], float)


def test_load_and_reload(monkeypatch, mock_model, mock_cursor):
    monkeypatch.setattr(
        "main.sql_faiss.thesis_search_engine.get_embedding",  # Changed this line
        lambda text, model: [0.1, 0.2, 0.3]
    )

    # Reset side_effect for multiple loads
    embedding = np.array([0.1, 0.2, 0.3]).tolist()
    mock_cursor.fetchall.side_effect = [
        # First load
        [("p1", "Title A", "Abstract A", json.dumps(embedding))],
        [("p1", "Author A")],
        [("p1", "Contributor A", "Editor")],
        # Reload
        [("p1", "Title A", "Abstract A", json.dumps(embedding))],
        [("p1", "Author A")],
        [("p1", "Contributor A", "Editor")],
    ]

    engine = SearchEngine(mock_model, mock_cursor)
    loaded = engine.load()
    assert isinstance(loaded, ThesisSimilaritySearch)
    assert engine.search_engine is loaded

    # Cached load (should not rebuild)
    cached = engine.load()
    assert cached is loaded

    # Force reload
    reloaded = engine.reload()
    assert isinstance(reloaded, ThesisSimilaritySearch)


def test_search_by_people_and_topic(monkeypatch, mock_model, mock_cursor):
    monkeypatch.setattr(
        "main.sql_faiss.thesis_search_engine.get_embedding",  # Changed this line
        lambda text, model: [0.1, 0.2, 0.3]
    )

    embedding = np.array([0.1, 0.2, 0.3]).tolist()
    mock_cursor.fetchall.side_effect = [
        [("p1", "Title A", "Abstract A", json.dumps(embedding))],
        [("p1", "Author A")],
        [("p1", "Contributor A", "Editor")],
    ]

    engine = SearchEngine(mock_model, mock_cursor)
    engine.load()

    # Mock internal search to return multiple fake results
    engine.search_engine.search = MagicMock(return_value=[
        {
            "id": "p1",
            "title": "Test Paper",
            "authors": ["John Doe"],
            "contributors": [{"name": "Jane Smith", "role": "Editor"}],
            "similarity_score": 0.9,
            "distance": 0.1,
        },
        {
            "id": "p2",
            "title": "Another Paper",
            "authors": ["Alice"],
            "contributors": [{"name": "Bob", "role": "Reviewer"}],
            "similarity_score": 0.8,
            "distance": 0.2,
        },
    ])

    # Filter by author
    results = engine.search_by_people_and_topic("query", author_name="john")
    assert len(results) == 1
    assert all("john" in a.lower() for r in results for a in r["authors"])

    # Filter by contributor name
    results = engine.search_by_people_and_topic(
        "query", contributor_name="jane")
    assert len(results) == 1
    assert all(any("jane" in c["name"].lower()
               for c in r["contributors"]) for r in results)

    # Filter by contributor role
    results = engine.search_by_people_and_topic(
        "query", contributor_role="reviewer")
    assert len(results) == 1
    assert all(any("reviewer" in c["role"].lower()
               for c in r["contributors"]) for r in results)
