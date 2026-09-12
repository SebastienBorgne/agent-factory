---
name: kafka-integration
description: Messaging conventions for projects that use Kafka — apply when the project's event/message broker is Kafka, covering topic naming, consumer groups, and making handlers safe to retry. Not applicable if the project uses a different broker or no messaging at all.
---

## What I do
I wire Django services to Kafka as producers and consumers: naming topics consistently, grouping consumers correctly, and making message handling idempotent so retries and replays don't corrupt state.

## How to apply
- Name topics with a consistent `<domain>.<entity>.<event>` convention (e.g. `orders.order.created`), never ad hoc per-feature names.
- Assign each logical consumer a stable, descriptive consumer-group id so scaling out adds parallelism instead of duplicating full processing.
- Make every consumer handler idempotent: key writes off the message's unique id (dedupe table or upsert) so at-least-once delivery can't double-apply an event.
- Commit offsets only after the handler's side effects have succeeded, not before.
- Keep message payloads versioned and backward-compatible; don't silently change a field's meaning on an existing topic.
- Log and route unprocessable messages to a dead-letter topic instead of dropping or endlessly retrying them.
- Keep producer calls out of the request/response critical path where possible — fire-and-confirm rather than blocking user-facing latency on broker acks.
