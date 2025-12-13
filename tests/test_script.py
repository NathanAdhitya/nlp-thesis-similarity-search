import pytest
import numpy as np
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_engine():
    with patch("main.main.search_engine.SearchEngine") as MockSearchEngineClass:
        mock_instance = MagicMock()
        MockSearchEngineClass.return_value = mock_instance

        # Import script ahead of time to prevent huggingface downloading anything
        import script
        yield mock_instance


def test_search_thesis(mock_engine):
    import script
    mock_engine.search_thesis.return_value = {
        "score": np.float32(0.95),
        "items": [{"id": np.int64(10)}]
    }

    result = script.search("deep learning", thesis=True)

    mock_engine.search_thesis.assert_called_once_with(
        query="deep learning",
        top_k=10,
        option="bgem3"
    )

    assert isinstance(result, dict)
    assert result["score"] == pytest.approx(0.95, abs=1e-2)
    assert result["items"][0]["id"] == 10


def test_search_advisor(mock_engine):
    import script
    mock_engine.search_advisor_3.return_value = [
        {"advisor_id": np.int32(5), "score": np.float64(0.88)}
    ]

    result = script.search(
        "machine learning", thesis=False, program_ids=[1, 2])

    mock_engine.search_advisor_3.assert_called_once_with(
        query="machine learning",
        top_k=10,
        option="bgem3",
        program_ids=[1, 2]
    )

    assert result == [{"advisor_id": 5, "score": 0.88}]


def test_get_all_programs(mock_engine):
    import script
    mock_engine.get_all_programs.return_value = ["A", "B", "C"]

    result = script.get_all_programs()

    mock_engine.get_all_programs.assert_called_once()
    assert result == ["A", "B", "C"]


def test_convert_to_json_serializable_nested():
    import script
    data = {
        "a": np.float32(1.2),
        "b": [np.int64(7), {"c": np.float64(3.14)}]
    }

    result = script.convert_to_json_serializable(data)

    assert isinstance(result, dict)
    assert result["a"] == pytest.approx(1.2, abs=1e-5)
    assert result["b"][1]["c"] == pytest.approx(3.14, abs=1e-5)

    assert isinstance(result["a"], float)
    assert isinstance(result["b"][0], int)
