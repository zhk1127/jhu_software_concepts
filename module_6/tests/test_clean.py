import json
from pathlib import Path

from src.worker.etl.clean import (
    clean_text,
    extract_gpa_from_comments,
    make_llm_program_field,
    clean_record,
    clean_data,
    save_data,
    load_data,
    write_log,
)


def test_clean_text():
    assert clean_text("A\nB\tC") == "A B C"
    assert clean_text(None) is None


def test_extract_gpa():
    assert extract_gpa_from_comments("GPA: 3.91") == "3.91"
    assert extract_gpa_from_comments("hello") is None


def test_program_field():
    assert make_llm_program_field("CS", "MIT") == "CS, MIT"
    assert make_llm_program_field("CS", None) == "CS"


def test_clean_record():
    rec = {
        "program": "Biology",
        "university": "Harvard",
        "comments": "GPA: 3.85",
        "GPA": None,
    }

    out = clean_record(rec)

    assert out["program"] == "Biology, Harvard"
    assert out["gpa_from_comments"] == "3.85"


def test_clean_data():
    records = [{"program": "A", "university": "B"}]
    result = clean_data(records)
    assert len(result) == 1


def test_save_load(tmp_path):
    f = tmp_path / "x.json"

    save_data([{"a": 1}], f)
    assert load_data(f) == [{"a": 1}]


def test_write_log(tmp_path):
    logfile = tmp_path / "log.txt"

    original = [{
        "url": "u",
        "comments": "GPA: 3.8",
        "GPA": None,
    }]

    cleaned = [{
        "url": "u",
        "comments": "GPA: 3.8",
        "GPA": None,
        "gpa_from_comments": "3.8",
    }]

    write_log(original, cleaned, logfile)

    assert logfile.exists()

def test_make_llm_program_field_university_only_and_empty():
    """make_llm_program_field handles university-only and empty cases."""
    assert make_llm_program_field(None, "Stanford") == "Stanford"
    assert make_llm_program_field(None, None) == ""


def test_clean_record_existing_gpa():
    """clean_record does not extract GPA from comments when GPA exists."""
    record = {
        "program": "Biology",
        "university": "Yale",
        "comments": "GPA: 3.99",
        "GPA": "3.5",
    }

    result = clean_record(record)

    assert result["gpa_from_comments"] is None


def test_write_log_without_changed_comments(tmp_path):
    """write_log handles records without examples."""
    logfile = tmp_path / "log.txt"

    original = [{"url": "u", "comments": "same", "GPA": "3.0"}]
    cleaned = [{"url": "u", "comments": "same", "GPA": "3.0", "gpa_from_comments": None}]

    write_log(original, cleaned, logfile)

    assert "Input records: 1" in logfile.read_text(encoding="utf-8")


def test_write_log_changed_comments_without_gpa(tmp_path):
    """write_log counts changed comments without GPA examples."""
    logfile = tmp_path / "log.txt"

    original = [{"url": "u", "comments": "A", "GPA": "3.0"}]
    cleaned = [{"url": "u", "comments": "B", "GPA": "3.0", "gpa_from_comments": None}]

    write_log(original, cleaned, logfile)

    text = logfile.read_text(encoding="utf-8")
    assert "Comment fields changed by text cleaning: 1" in text
