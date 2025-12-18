import json
import pytest

from data_pipeline.processing.dewey_cleanup import (
    extract_contributor_info,
    is_advisor_role,
    load_thesis_data,
    extract_advisor_names,
    levenshtein_distance,
    keyboard_distance,
    standardize_name,
    weighted_name_distance,
    cluster_names_by_similarity,
    save_canonical_clusters,
)


def test_extract_contributor_info_basic():
    text = "Prof. Dr. John Smith, M.T. (Advisor 1); Jane Doe, S.T., M.Sc. (Examiner)"
    result = extract_contributor_info(text)

    assert len(result) == 2
    assert result[0]['clean_name'] == "John Smith"
    assert result[0]['role'].lower().startswith("advisor")
    assert result[1]['clean_name'] == "Jane Doe"


def test_extract_contributor_info_empty():
    assert extract_contributor_info("") == []


def test_extract_contributor_info_unknown_role():
    text = "Alice Wonderland"
    result = extract_contributor_info(text)
    assert result[0]['role'] == "Unknown"
    assert result[0]['clean_name'] == "Alice Wonderland"


@pytest.mark.parametrize("role,expected", [
    ("Advisor 1", True),
    ("Main Supervisor", True),
    ("Committee", False),
])
def test_is_advisor_role(role, expected):
    assert is_advisor_role(role) == expected


def test_load_thesis_data(tmp_path):
    # Create dummy JSON files
    valid_data = {"title": "Test Thesis", "contributors": "John (Advisor)"}
    invalid_json = tmp_path / "bad.json"
    valid_json = tmp_path / "good.json"

    valid_json.write_text(json.dumps(valid_data))
    invalid_json.write_text("{bad json}")

    data = load_thesis_data(str(tmp_path))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test Thesis"


def test_load_thesis_data_nonexistent(tmp_path):
    non_dir = tmp_path / "no_such_dir"
    assert load_thesis_data(str(non_dir)) == []


def test_extract_advisor_names():
    thesis_data = [
        {"contributors": "John Doe (Advisor 1); Alice (Examiner)"},
        {"contributors": "Dr. Jane (Supervisor)"},
    ]
    result = extract_advisor_names(thesis_data)
    assert "John Doe" in result
    assert "Jane" in result
    assert all(isinstance(x, str) for x in result)


@pytest.mark.parametrize("s1,s2,expected", [
    ("kitten", "sitting", 3),
    ("flaw", "lawn", 2),
    ("", "abc", 3),
])
def test_levenshtein_distance(s1, s2, expected):
    assert levenshtein_distance(s1, s2) == expected


def test_keyboard_distance():
    assert keyboard_distance("a", "s") < 1.1  # adjacent keys
    assert keyboard_distance("a", "p") > 5    # far apart
    assert keyboard_distance("a", "1") == 2.0  # non-keyboard char fallback


def test_standardize_name():
    assert standardize_name("  john   doe  ") == "John Doe"
    assert standardize_name("") == ""


def test_weighted_name_distance_identical():
    assert weighted_name_distance("John Doe", "John Doe") == 0.0


def test_weighted_name_distance_different():
    d = weighted_name_distance("John", "Jon")
    assert 0 < d < 3  # small but non-zero distance


def test_weighted_name_distance_empty_input():
    assert weighted_name_distance("", "John") == float("inf")


def test_cluster_names_by_similarity_simple():
    names = {"John Smith", "Jon Smith", "Alice"}
    clusters = cluster_names_by_similarity(names, max_distance=2.5)

    assert isinstance(clusters, dict)
    # Expect John and Jon to be clustered
    cluster_values = sum(clusters.values(), [])
    assert "John Smith" in cluster_values
    assert "Jon Smith" in cluster_values


def test_save_canonical_clusters(tmp_path):
    clusters = {
        "John Smith": ["John Smith", "Jon Smith"],
        "Alice": ["Alice"]
    }
    output_file = tmp_path / "output" / "canonical.json"

    save_canonical_clusters(clusters, str(output_file))

    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert "canonical_mapping" in data
    assert "merged_clusters" in data
    assert "John Smith" in data["canonical_mapping"]
