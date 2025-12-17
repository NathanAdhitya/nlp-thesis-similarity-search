import csv
import json
import pytest
from unittest.mock import patch
from data_pipeline.processing.step_02_scholar_cleanup import (
    load_scholar_authors,
    clean_scholar_name,
    analyze_scholar_authors,
)


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x.lower())
def test_load_scholar_authors_valid(mock_std, tmp_path, capsys):
    csv_file = tmp_path / "authors.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name"])
        writer.writeheader()
        writer.writerow({"name": "Dr. Alice"})
        writer.writerow({"name": "Bob - University"})
        writer.writerow({"name": "Charlie (MIT)"})
    result = load_scholar_authors(str(csv_file))
    out = capsys.readouterr().out
    assert "Successfully loaded" in out
    assert "alice" not in result  # cleaned name not standardized yet
    assert any("Alice" in n or "Bob" in n or "Charlie" in n for n in result)
    assert isinstance(result, set)
    assert len(result) == 3


def test_load_scholar_authors_missing_file(tmp_path, capsys):
    csv_file = tmp_path / "nope.csv"
    result = load_scholar_authors(str(csv_file))
    out = capsys.readouterr().out
    assert "does not exist" in out
    assert result == set()


@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("Dr. Alice", "Alice"),
        ("Prof. Bob, PhD.", "Bob"),
        ("Charlie - MIT", "Charlie"),
        ("Dave (Harvard)", "Dave"),
        ("someone@email.com", ""),
        ("   .,.,Eve.,.,", "Eve"),
    ],
)
def test_clean_scholar_name(input_name, expected):
    assert clean_scholar_name(input_name) == expected


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x.strip().lower())
@patch("data_pipeline.processing.step_01_dewey_cleanup.cluster_names_by_similarity", return_value={"alice": ["alice", "alise"]})
@patch("data_pipeline.processing.step_01_dewey_cleanup.weighted_name_distance", side_effect=lambda a, b: 1.0)
def test_analyze_scholar_authors_creates_output(mock_dist, mock_cluster, mock_std, tmp_path, capsys):
    csv_file = tmp_path / "authors.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name"])
        writer.writeheader()
        writer.writerow({"name": "Alice"})
        writer.writerow({"name": "Alise"})
    output_dir = tmp_path / "data"
    output_dir.mkdir(exist_ok=True)

    real_open = open

    def selective_open(filename, mode='r', *args, **kwargs):
        filename_str = str(filename)
        if 'canonical_scholar.json' in filename_str and 'w' in mode:
            redirected_path = output_dir / "canonical_scholar.json"
            return real_open(redirected_path, mode, *args, **kwargs)
        else:
            return real_open(filename, mode, *args, **kwargs)
    with patch("builtins.open", side_effect=selective_open):
        result = analyze_scholar_authors(
            str(csv_file), max_distance=2.0, save_canonical=True
        )

    out = capsys.readouterr().out
    assert "Scholar canonical clusters saved to" in out
    assert "Reduction" in out
    assert "Cluster 1" in out
    assert isinstance(result, dict)

    canonical_file = output_dir / "canonical_scholar.json"
    assert canonical_file.exists()

    data = json.loads(canonical_file.read_text())
    assert data["source"] == "google_scholar"
    assert "canonical_mapping" in data


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", return_value="")
def test_analyze_scholar_authors_no_data(mock_std, tmp_path, capsys):
    csv_file = tmp_path / "empty.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name"])
        writer.writeheader()
    analyze_scholar_authors(str(csv_file))
    out = capsys.readouterr().out
    assert "No scholar data found!" in out
