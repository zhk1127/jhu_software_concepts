import pytest

from src.db import load_data


TEST_ID =  "999999001"


def sample_record():
    return {
        "raw_record": {"id": TEST_ID},
        "program": "Computer Science, Johns Hopkins University",
        "comments": "pytest fake record",
        "date_added": "Jun 01, 2026",
        "url": "https://example.com/pytest",
        "status": "Accepted",
        "term": "Fall 2026",
        "US/International": "International",
        "GPA": "3.90",
        "GRE Score": "325",
        "GRE V Score": "160",
        "GRE AW": "4.5",
        "Degree": "PhD",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Johns Hopkins University",
    }


def cleanup_test_record():
    load_data.create_table()

    with load_data.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM applicants WHERE p_id = %s;",
                (TEST_ID,),
            )


@pytest.mark.db
def test_parse_float():
    assert load_data.parse_float("3.90") == 3.90
    assert load_data.parse_float("") is None
    assert load_data.parse_float(None) is None
    assert load_data.parse_float("not-a-number") is None


@pytest.mark.db
def test_parse_date():
    assert str(load_data.parse_date("Jun 01, 2026")) == "2026-06-01"
    assert load_data.parse_date("") is None
    assert load_data.parse_date("bad-date") is None


@pytest.mark.db
def test_record_to_tuple():
    row = load_data.record_to_tuple(sample_record())

    assert row[0] == TEST_ID
    assert row[1] == "Computer Science, Johns Hopkins University"
    assert row[5] == "Accepted"
    assert row[8] == 3.90
    assert row[13] == "Computer Science"


@pytest.mark.db
def test_load_records_inserts_and_avoids_duplicates():
    cleanup_test_record()

    before_count = load_data.get_database_count()

    inserted = load_data.load_records([sample_record()])
    after_count = load_data.get_database_count()

    assert inserted == 1
    assert after_count == before_count + 1

    inserted_again = load_data.load_records([sample_record()])
    final_count = load_data.get_database_count()

    assert inserted_again == 0
    assert final_count == after_count

    cleanup_test_record()


@pytest.mark.db
def test_get_database_count_returns_integer():
    count = load_data.get_database_count()

    assert isinstance(count, int)
    assert count >= 0

from src.worker.etl import pull_new_data


@pytest.mark.db
def test_insert_records_into_database():
    test_id = "999999002"

    conn = pull_new_data.psycopg.connect(**pull_new_data.DB_CONFIG)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM applicants WHERE p_id = %s;",
        (test_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    record = {
        "raw_record": {"id": test_id},
        "program": "pytest program",
        "comments": "pytest",
        "url": "https://example.com",
        "status": "Accepted",
        "term": "Fall 2026",
        "US/International": "International",
        "Degree": "PhD",
        "GPA": "3.9",
        "GRE Score": "325",
        "GRE V Score": "160",
        "GRE AW": "4.5",
        "date_added": "Jun 01, 2026",
    }

    inserted, skipped = (
        pull_new_data.insert_records_into_database(
            [record]
        )
    )

    assert inserted == 1
    assert skipped == 0

    inserted2, skipped2 = (
        pull_new_data.insert_records_into_database(
            [record]
        )
    )

    assert inserted2 == 0
    assert skipped2 == 1

    conn = pull_new_data.psycopg.connect(
        **pull_new_data.DB_CONFIG
    )

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM applicants WHERE p_id = %s;",
        (test_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

@pytest.mark.db
def test_insert_records_skips_missing_id():
    record = {
        "raw_record": {},
        "program": "pytest program",
    }

    inserted, skipped = pull_new_data.insert_records_into_database([record])

    assert inserted == 0
    assert skipped == 1

@pytest.mark.db
def test_load_data_main_with_fakes(monkeypatch, tmp_path):
    fake_file = tmp_path / "fake_data.json"
    fake_file.write_text(
        '[{"raw_record": {"id": 123}, "program": "fake"}]',
        encoding="utf-8",
    )

    calls = []

    monkeypatch.setattr(load_data, "DATA_FILE", str(fake_file))

    def fake_load_records(data):
        calls.append(data)
        return 1

    monkeypatch.setattr(load_data, "load_records", fake_load_records)

    load_data.main()

    assert len(calls) == 1
    assert calls[0][0]["raw_record"]["id"] == 123

import runpy
