from __future__ import annotations

from confluent_kafka import Producer
from django.conf import settings

from domain.ports import EventPublisher

RUN_REQUESTED_TOPIC = "run.requested"


class KafkaEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self._producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})

    def publish_run_requested(self, project_slug: str) -> None:
        self._producer.produce(RUN_REQUESTED_TOPIC, key=project_slug, value=project_slug)
        self._producer.flush(timeout=10)
