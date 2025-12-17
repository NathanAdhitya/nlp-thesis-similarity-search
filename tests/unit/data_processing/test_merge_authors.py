import csv
import json
from unittest.mock import patch
from data_pipeline.processing.step_04_merge_authors import (
    load_scholar_authors,
    load_combined_authors,
    merge_authors,
)


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x.lower())
def test_load_scholar_authors(mock_std, tmp_path, capsys):
    csv_file = tmp_path / "authors.csv"
    rows = [
        {"name": "Alice", "scholar_id": "S1",
            "affiliation": "Uni", "email_domain": "a.com"},
        {"name": "Bob", "scholar_id": "S2",
            "affiliation": "Lab", "email_domain": "b.com"},
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    authors = load_scholar_authors(str(csv_file))
    assert "Alice" in authors
    assert authors["Alice"]["scholar_id"] == "S1"
    assert "Bob" in authors
    assert "Loaded 2" in capsys.readouterr().out


def test_load_scholar_authors_missing_file(tmp_path, capsys):
    csv_file = tmp_path / "missing.csv"
    result = load_scholar_authors(str(csv_file))
    assert result == {}
    assert "does not exist" in capsys.readouterr().out


def test_load_combined_authors(tmp_path, capsys):
    json_file = tmp_path / "combined.json"
    data = {"canonical_mapping": {"Alice": "Alicia"}}
    json_file.write_text(json.dumps(data))
    result = load_combined_authors(str(json_file))
    assert result == {"Alice": "Alicia"}
    assert "Loaded 1" in capsys.readouterr().out


def test_load_combined_authors_missing(tmp_path, capsys):
    f = tmp_path / "nope.json"
    result = load_combined_authors(str(f))
    assert result == {}
    assert "does not exist" in capsys.readouterr().out


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x.strip().lower())
def test_merge_authors_basic(mock_std, tmp_path, capsys):
    scholar_authors = {
        "alice": {"scholar_id": "S1", "affiliation": "Uni", "email_domain": "a.com"},
        "bob": {"scholar_id": "S2", "affiliation": "Lab", "email_domain": "b.com"},
    }
    combined_mapping = {"Alice": "Alicia"}
    output = tmp_path / "out" / "merged.csv"
    result = merge_authors(scholar_authors, combined_mapping, str(output))
    assert output.exists()
    with open(output, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert any(r["name"] == "Alicia" for r in rows)
    assert ("Alice" in result) or ("Alicia" in result)
    assert "Total merged authors" in capsys.readouterr().out


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x)
def test_merge_authors_handles_empty_and_duplicates(mock_std, tmp_path):
    scholar_authors = {"": {"scholar_id": "S1"}}
    combined_mapping = {"": ""}
    output = tmp_path / "out" / "merged.csv"
    result = merge_authors(scholar_authors, combined_mapping, str(output))
    assert isinstance(result, dict)
    assert output.exists()
