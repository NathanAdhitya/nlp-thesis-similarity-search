import json
import pytest
from unittest.mock import patch
from data_pipeline.processing.step_03_combine_authors import (
    load_canonical_data,
    combine_author_datasets
)


@pytest.fixture
def dummy_dewey_data(tmp_path):
    data = {
        "total_clusters": 2,
        "canonical_mapping": {
            "J. Smith": "John Smith",
            "Jane D.": "Jane Doe"
        }
    }
    file = tmp_path / "dewey.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file


@pytest.fixture
def dummy_scholar_data(tmp_path):
    data = {
        "total_clusters": 2,
        "canonical_mapping": {
            "John S.": "John Smith",
            "J. Doe": "Jane Doe"
        }
    }
    file = tmp_path / "scholar.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file


@pytest.fixture
def dummy_dewey_data_different(tmp_path):
    """Dewey data with names that won't match Scholar data"""
    data = {
        "total_clusters": 2,
        "canonical_mapping": {
            "J. Smith": "John Smith Dewey",      # Different from Scholar
            "Jane D.": "Jane Doe Dewey"          # Different from Scholar
        }
    }
    file = tmp_path / "dewey_diff.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file


@pytest.fixture
def dummy_scholar_data_different(tmp_path):
    """Scholar data with names that won't match Dewey data"""
    data = {
        "total_clusters": 2,
        "canonical_mapping": {
            "John S.": "John Scholar Smith",     # Different from Dewey
            "J. Doe": "Jane Scholar Doe"         # Different from Dewey
        }
    }
    file = tmp_path / "scholar_diff.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file


def test_load_canonical_data_existing(dummy_dewey_data):
    data = load_canonical_data(str(dummy_dewey_data))
    assert "canonical_mapping" in data
    assert data["total_clusters"] == 2


def test_load_canonical_data_missing(tmp_path):
    fake_path = tmp_path / "missing.json"
    data = load_canonical_data(str(fake_path))
    assert data == {}


@patch("data_pipeline.processing.step_03_combine_authors.weighted_name_distance")
def test_combine_author_datasets_basic(mock_distance, dummy_dewey_data, dummy_scholar_data, tmp_path):
    # Mock similarity distances so that only identical canonical names match
    def fake_distance(name1, name2):
        return 0.0 if name1 == name2 else 5.0

    mock_distance.side_effect = fake_distance

    output_file = tmp_path / "combined.json"

    result = combine_author_datasets(
        dewey_file=str(dummy_dewey_data),
        scholar_file=str(dummy_scholar_data),
        output_file=str(output_file),
        cross_match_threshold=2.0
    )

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert "metadata" in saved
    assert "cross_matches" in saved
    assert "combined_mapping" in saved
    assert "cross_reference_clusters" in saved

    # Check metadata
    meta = saved["metadata"]
    assert meta["cross_match_threshold"] == 2.0
    assert meta["cross_matches_found"] == 2  # John Smith, Jane Doe

    # Check cross-reference clusters count
    assert len(saved["cross_reference_clusters"]) == 2

    # Check combined mapping merges both
    combined_map = saved["combined_mapping"]
    assert "J. Smith" in combined_map
    assert "John S." in combined_map
    # Unified under Dewey canonical
    assert combined_map["John S."] == "John Smith"


@patch("data_pipeline.processing.step_03_combine_authors.weighted_name_distance")
def test_combine_author_datasets_no_matches(mock_distance, dummy_dewey_data_different,
                                            dummy_scholar_data_different, tmp_path):
    # Force all names to be non-matching
    mock_distance.return_value = 20.0

    output_file = tmp_path / "combined_no_matches.json"

    result = combine_author_datasets(
        dewey_file=str(dummy_dewey_data_different),
        scholar_file=str(dummy_scholar_data_different),
        output_file=str(output_file),
        cross_match_threshold=2.0
    )

    assert result is not None
    assert result["metadata"]["cross_matches_found"] == 0
    assert len(result["cross_reference_clusters"]) == 0
