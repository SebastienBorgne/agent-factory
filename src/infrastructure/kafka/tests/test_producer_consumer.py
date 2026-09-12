from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from infrastructure.kafka.producer import RUN_REQUESTED_TOPIC, KafkaEventPublisher


class KafkaEventPublisherTests(SimpleTestCase):
    @patch("infrastructure.kafka.producer.Producer")
    def test_publish_run_requested_produces_and_flushes(self, mock_producer_cls):
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        KafkaEventPublisher().publish_run_requested("acme")

        mock_producer.produce.assert_called_once_with(RUN_REQUESTED_TOPIC, key="acme", value="acme")
        mock_producer.flush.assert_called_once()


class _StopPolling(Exception):
    """Sentinel to break out of consume_forever's infinite poll loop in tests."""


class KafkaEventConsumerTests(SimpleTestCase):
    @patch("infrastructure.kafka.consumer.Consumer")
    def test_consume_forever_decodes_and_dispatches_then_commits(self, mock_consumer_cls):
        from infrastructure.kafka.consumer import KafkaEventConsumer

        mock_consumer = MagicMock()
        mock_consumer_cls.return_value = mock_consumer

        msg = MagicMock()
        msg.error.return_value = None
        msg.value.return_value = b"acme"
        mock_consumer.poll.side_effect = [msg, _StopPolling()]

        calls = []
        consumer = KafkaEventConsumer()
        with self.assertRaises(_StopPolling):
            consumer.consume_forever(calls.append)

        self.assertEqual(calls, ["acme"])
        mock_consumer.commit.assert_called_once_with(msg)
        mock_consumer.close.assert_called_once()

    @patch("infrastructure.kafka.consumer.Consumer")
    def test_handler_exception_is_swallowed_and_offset_still_committed(self, mock_consumer_cls):
        from infrastructure.kafka.consumer import KafkaEventConsumer

        mock_consumer = MagicMock()
        mock_consumer_cls.return_value = mock_consumer

        msg = MagicMock()
        msg.error.return_value = None
        msg.value.return_value = b"acme"
        mock_consumer.poll.side_effect = [msg, _StopPolling()]

        def blowing_up(_slug):
            raise RuntimeError("opencode not found")

        with self.assertRaises(_StopPolling):
            KafkaEventConsumer().consume_forever(blowing_up)

        mock_consumer.commit.assert_called_once_with(msg)
