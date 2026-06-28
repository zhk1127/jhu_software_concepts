"""Tests for RabbitMQ publisher helpers."""

import json

import pytest

from src.web import publisher


class FakeChannel:
    """Minimal fake RabbitMQ channel."""

    def __init__(self):
        self.exchange_declared = False
        self.queue_declared = False
        self.bound = False
        self.published = None

    def exchange_declare(self, exchange, exchange_type, durable):
        self.exchange_declared = (exchange, exchange_type, durable)

    def queue_declare(self, queue, durable):
        self.queue_declared = (queue, durable)

    def queue_bind(self, exchange, queue, routing_key):
        self.bound = (exchange, queue, routing_key)

    def basic_publish(self, exchange, routing_key, body, properties, mandatory=False):
        self.published = {
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body,
            "properties": properties,
            "mandatory": mandatory,
        }


class FakeConnection:
    """Minimal fake RabbitMQ connection."""

    def __init__(self):
        self.fake_channel = FakeChannel()
        self.closed = False

    def channel(self):
        return self.fake_channel

    def close(self):
        self.closed = True


@pytest.mark.unit
def test_open_channel_declares_durable_entities(monkeypatch):
    """_open_channel declares durable RabbitMQ entities."""
    fake_connection = FakeConnection()

    def fake_blocking_connection(_params):
        return fake_connection

    monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    monkeypatch.setattr(publisher.pika, "BlockingConnection", fake_blocking_connection)

    connection, channel = publisher._open_channel()

    assert connection is fake_connection
    assert channel.exchange_declared == ("tasks", "direct", True)
    assert channel.queue_declared == ("tasks_q", True)
    assert channel.bound == ("tasks", "tasks_q", "tasks")


@pytest.mark.unit
def test_publish_task_sends_persistent_json_message(monkeypatch):
    """publish_task publishes a persistent compact JSON message and closes the connection."""
    fake_connection = FakeConnection()

    def fake_open_channel():
        return fake_connection, fake_connection.fake_channel

    monkeypatch.setattr(publisher, "_open_channel", fake_open_channel)

    publisher.publish_task("scrape_new_data", payload={"source": "test"})

    published = fake_connection.fake_channel.published
    message = json.loads(published["body"].decode("utf-8"))

    assert published["exchange"] == "tasks"
    assert published["routing_key"] == "tasks"
    assert published["mandatory"] is False
    assert published["properties"].delivery_mode == 2
    assert message["kind"] == "scrape_new_data"
    assert message["payload"] == {"source": "test"}
    assert "ts" in message
    assert fake_connection.closed is True
