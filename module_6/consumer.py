"""RabbitMQ worker consumer for GradCafe background tasks."""

import json
import os
import time

import pika

from src import pull_new_data
from src.query_data import get_analysis_results

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"


def connect_with_retry():
    """Connect to RabbitMQ with retries."""
    url = os.environ["RABBITMQ_URL"]

    for attempt in range(10):
        try:
            return pika.BlockingConnection(pika.URLParameters(url))
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready, retrying... attempt {attempt + 1}", flush=True)
            time.sleep(2)

    raise RuntimeError("Could not connect to RabbitMQ")


def declare_entities(channel):
    """Declare durable RabbitMQ exchange, queue, and binding."""
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)
    channel.basic_qos(prefetch_count=1)


def handle_scrape_new_data(payload):
    """Run the existing GradCafe scrape-and-insert workflow."""
    print(f"Handling scrape_new_data with payload={payload}", flush=True)
    pull_new_data.main()


def handle_recompute_analytics(payload):
    """Recompute analytics by running existing SQL queries."""
    print(f"Handling recompute_analytics with payload={payload}", flush=True)
    get_analysis_results()


TASK_HANDLERS = {
    "scrape_new_data": handle_scrape_new_data,
    "recompute_analytics": handle_recompute_analytics,
}


def callback(channel, method, properties, body):
    """Route one RabbitMQ task message to the correct handler."""
    try:
        message = json.loads(body.decode("utf-8"))
        kind = message.get("kind")
        payload = message.get("payload", {})

        if kind not in TASK_HANDLERS:
            raise ValueError(f"Unknown task kind: {kind}")

        TASK_HANDLERS[kind](payload)

        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Task completed and acknowledged: {kind}", flush=True)

    except Exception as exc:
        print(f"Task failed: {exc}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    """Start the long-running RabbitMQ worker."""
    connection = connect_with_retry()
    channel = connection.channel()
    declare_entities(channel)

    channel.basic_consume(queue=QUEUE, on_message_callback=callback)

    print("Worker waiting for tasks...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()