"""Tests for transactional insert behavior in pull_new_data."""

import pytest

from src.worker.etl import pull_new_data


class FakeCursor:
    """Cursor that raises during insert to trigger rollback."""

    rowcount = 0

    def execute(self, query, params=None):
        raise RuntimeError("insert failed")

    def close(self):
        pass


class FakeConnection:
    """Connection that records rollback and close calls."""

    def __init__(self):
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return FakeCursor()

    def commit(self):
        raise AssertionError("commit should not be called on failure")

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_insert_records_rolls_back_on_error(monkeypatch):
    """insert_records_into_database rolls back and re-raises on insert failure."""
    fake_conn = FakeConnection()

    monkeypatch.setattr(
        pull_new_data.psycopg,
        "connect",
        lambda **kwargs: fake_conn,
    )

    records = [
        {
            "raw_record": {"id": 123},
            "program": "CS",
        }
    ]

    with pytest.raises(RuntimeError, match="insert failed"):
        pull_new_data.insert_records_into_database(records)

    assert fake_conn.rolled_back is True
    assert fake_conn.closed is True
