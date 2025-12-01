import pytest
from main.sql_faiss.print_formatted_results import print_formatted_results


@pytest.fixture
def sample_results():
    return [
        {
            "title": "Deep Learning Thesis",
            "similarity_score": 0.9234,
            "distance": 0.0766,
            "authors": ["Alice", "Bob"],
            "contributors": [
                {"role": "Supervisor", "name": "Dr. Smith"},
                {"role": "Examiner", "name": "Prof. Lee"}
            ],
            "abstract": "This work explores deep learning methods for natural language processing."
        }
    ]


def test_print_no_results(capsys):
    print_formatted_results([])
    captured = capsys.readouterr()
    assert "No results found." in captured.out


def test_print_with_all_fields(capsys, sample_results):
    print_formatted_results(sample_results)
    captured = capsys.readouterr()
    output = captured.out

    # Check that all key sections appear
    assert "Result 1: Deep Learning Thesis" in output
    assert "Similarity: 0.9234" in output
    assert "Distance: 0.0766" in output
    assert "Authors: Alice, Bob" in output
    assert "Contributors:" in output
    assert "Supervisor: Dr. Smith" in output
    assert "Examiner: Prof. Lee" in output
    assert "Abstract: This work explores deep learning" in output


@pytest.mark.parametrize("option", ["show_authors", "show_contributors", "show_abstract", "show_metrics"])
def test_toggle_display_options(capsys, sample_results, option):
    kwargs = {option: False}
    print_formatted_results(sample_results, **kwargs)
    captured = capsys.readouterr()
    output = captured.out

    if option == "show_authors":
        assert "Authors:" not in output
    elif option == "show_contributors":
        assert "Contributors:" not in output
    elif option == "show_abstract":
        assert "Abstract:" not in output
    elif option == "show_metrics":
        assert "Similarity:" not in output and "Distance:" not in output


def test_print_handles_missing_optional_fields(capsys):
    minimal_result = [
        {
            "title": "Untitled Thesis",
            "similarity_score": 0.5,
            "distance": 0.5,
            "authors": [],
            "contributors": [],
            "abstract": None
        }
    ]
    print_formatted_results(minimal_result)
    captured = capsys.readouterr()
    output = captured.out

    assert "No author information available" in output
    assert "No contributor information available" in output
    assert "No abstract available" in output


def test_long_abstract_truncation(capsys):
    long_abstract = "A" * 400
    result = [
        {
            "title": "Long Abstract",
            "similarity_score": 0.9,
            "distance": 0.1,
            "authors": ["Jane"],
            "contributors": [],
            "abstract": long_abstract,
        }
    ]
    print_formatted_results(result)
    captured = capsys.readouterr()
    output = captured.out
    assert len(output) < 500
    assert "..." in output
