from __future__ import annotations

from collections.abc import Callable

from confluent_kafka import Consumer
from django.conf import settings

from domain.ports import EventConsumer

from .producer import RUN_REQUESTED_TOPIC


class KafkaEventConsumer(EventConsumer):
    def __init__(self) -> None:
        self._consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "agent-factory-worker",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        self._consumer.subscribe([RUN_REQUESTED_TOPIC])

    def consume_forever(self, handler: Callable[[str], None]) -> None:
        try:
            while True:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"worker: kafka error: {msg.error()}", flush=True)
                    continue
                project_slug = msg.value().decode("utf-8")
                try:
                    handler(project_slug)
                except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                    # Keep the worker alive: one bad run must not kill the consumer loop.
                    print(f"worker: run for {project_slug!r} raised {exc!r}", flush=True)
                self._consumer.commit(msg)
        finally:
            self._consumer.close()
