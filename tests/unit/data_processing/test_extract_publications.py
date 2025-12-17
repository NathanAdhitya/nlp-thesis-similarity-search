import json
import csv
import pytest
from unittest.mock import patch
from data_pipeline.processing.step_05_extract_publications import (
    extract_year_from_source,
    load_merged_authors,
    extract_dewey_thesis_data,
    extract_publication_data,
)


@pytest.mark.parametrize("source,expected", [
    ("No.003/EP-IHM/2001", "2001"),
    ("/2020, Some Source", "2020"),
    ("36020756/MAN/2020", "2020"),
    ("invalid text 1890", None),
    ("", None),
])
def test_extract_year_from_source(source, expected):
    assert extract_year_from_source(source) == expected


def test_load_merged_authors(tmp_path):
    csv_file = tmp_path / "merged.csv"
    rows = [
        {"name": "Alice", "dewey_id": "D1", "scholar_id": "S1",
            "original_names": "A. Lice; Alicee"},
        {"name": "Bob", "dewey_id": "D2", "scholar_id": "", "original_names": ""},
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    dewey_map, scholar_map = load_merged_authors(str(csv_file))

    assert dewey_map["Alice"] == "D1"
    assert "Alicee" in dewey_map
    assert scholar_map["Alice"] == "S1"
    assert "Bob" in dewey_map and "Bob" not in scholar_map


def test_load_merged_authors_missing_file(tmp_path, capsys):
    csv_file = tmp_path / "missing.csv"
    result = load_merged_authors(str(csv_file))
    assert result == ({}, {})
    assert "not found" in capsys.readouterr().out


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x)
@patch("data_pipeline.processing.step_01_dewey_cleanup.extract_contributor_info")
@patch("data_pipeline.processing.step_01_dewey_cleanup.is_advisor_role", return_value=True)
def test_extract_dewey_thesis_data(mock_role, mock_info, mock_std, tmp_path):
    data_dir = tmp_path / "data"
    output_file = tmp_path / "out" / "cleaned.csv"
    data_dir.mkdir()

    thesis_json = {
        "title": "Sample Thesis",
        "abstract": "Some abstract",
        "source": "/2022, Something",
        "contributors": "John (Advisor)"
    }
    file_path = data_dir / "1.json"
    file_path.write_text(json.dumps(thesis_json))

    mock_info.return_value = [{"clean_name": "John", "role": "Advisor"}]
    name_map = {"John": "D100"}

    extract_dewey_thesis_data(str(data_dir), name_map, str(output_file))

    assert output_file.exists()
    with open(output_file, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["dewey_thesis_id"] == "1"
    assert rows[0]["year"] == "2022"
    assert rows[0]["dewey_ids"] == "D100"


def test_extract_dewey_thesis_data_missing_dir(tmp_path, capsys):
    extract_dewey_thesis_data(str(tmp_path / "nope"),
                              {}, str(tmp_path / "out.csv"))
    assert "does not exist" in capsys.readouterr().out


def test_extract_dewey_thesis_data_invalid_json(tmp_path, capsys):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "bad.json").write_text("{bad json}")
    out = tmp_path / "out.csv"
    extract_dewey_thesis_data(str(data_dir), {}, str(out))
    assert "Error reading" in capsys.readouterr().out


@patch("data_pipeline.processing.step_01_dewey_cleanup.standardize_name", side_effect=lambda x: x)
def test_extract_publication_data(mock_std, tmp_path):
    pub_dir = tmp_path / "pubs"
    pub_dir.mkdir()
    file = pub_dir / "S123.jsonl"
    pub_content = {
        "bib": {
            "title": "My Paper",
            "abstract": "This is abs",
            "author": "Alice and Bob",
            "pub_year": "2021"
        },
        "pub_url": "http://example.com"
    }
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(pub_content) + "\n")

    name_to_scholar_id = {"Alice": "S123", "Bob": "S456"}
    out = tmp_path / "out" / "pub.csv"

    extract_publication_data(str(pub_dir), name_to_scholar_id, str(out))

    with open(out, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows[0]["title"] == "My Paper"
    assert "S123" in rows[0]["scholar_ids"]


def test_extract_publication_data_missing_dir(tmp_path, capsys):
    extract_publication_data(str(tmp_path / "nope"),
                             {}, str(tmp_path / "out.csv"))
    assert "does not exist" in capsys.readouterr().out


def test_extract_publication_data_bad_json(tmp_path, capsys):
    pub_dir = tmp_path / "pubs"
    pub_dir.mkdir()
    f = pub_dir / "S1.jsonl"
    f.write_text("{bad json}")
    out = tmp_path / "out.csv"
    extract_publication_data(str(pub_dir), {}, str(out))
    assert "Error parsing" in capsys.readouterr().out
