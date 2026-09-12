#!/usr/bin/env python
"""Entrypoint for the `worker` container: consumes run.requested events from
Kafka and drives `opencode run` for the target project's PM agent."""

import os
import sys
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()

    from application.use_cases.handle_run_result import handle_run_result
    from infrastructure.django_app.repositories import (
        DjangoProjectRepository,
        DjangoRunLogRepository,
    )
    from infrastructure.kafka.consumer import KafkaEventConsumer
    from infrastructure.opencode_cli.runner import OpenCodeRunner

    project_repo = DjangoProjectRepository()
    run_log_repo = DjangoRunLogRepository()
    runner = OpenCodeRunner()

    def handle(project_slug: str) -> None:
        project = project_repo.get(project_slug)
        run_log = runner.run_project_manager(project)
        handle_run_result(
            run_log_repo,
            project_slug=project_slug,
            status=run_log.status,
            log_tail=run_log.log_tail,
        )

    consumer = KafkaEventConsumer()
    print("worker: listening for run.requested events...", flush=True)
    consumer.consume_forever(handle)


if __name__ == "__main__":
    main()
