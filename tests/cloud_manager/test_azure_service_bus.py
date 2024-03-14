import asyncio
import time
import unittest
from unittest.mock import MagicMock, call, patch

from azure.servicebus import ServiceBusMessage, ServiceBusMessageBatch
from azure.servicebus._common.auto_lock_renewer import AutoLockRenewer
from azure.servicebus.exceptions import ServiceBusError

from cloud_manager.azure_service_bus import AzureServiceBus


class TestAzureServiceBusAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.patcher1 = patch(
            "azure.servicebus.aio.ServiceBusClient.from_connection_string"
        )
        self.patcher2 = patch(
            "azure.servicebus.ServiceBusClient.from_connection_string"
        )
        self.mock_async_from_connection_string = self.patcher1.start()
        self.mock_from_connection_string = self.patcher2.start()

        # Mock for the asynchronous client
        self.mock_async_service_bus_client = MagicMock()
        self.mock_async_from_connection_string.return_value = (
            self.mock_async_service_bus_client
        )

        # Mock for the synchronous client
        self.mock_service_bus_client = MagicMock()
        self.mock_from_connection_string.return_value = self.mock_service_bus_client

        self.service_bus = AzureServiceBus("mock_connection_string")

    async def asyncTearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    @patch("cloud_manager.azure_service_bus.logger")
    async def test_publish_async(self, mock_logger):
        topic = "test_topic_async"
        messages = ["async_message1", "async_message2"]

        mock_sender = MagicMock()
        mock_batch = MagicMock(spec=ServiceBusMessageBatch)
        mock_batch.__len__.return_value = len(messages)
        mock_sender.create_message_batch = MagicMock(return_value=asyncio.Future())
        mock_sender.create_message_batch.return_value.set_result(mock_batch)
        mock_sender.send_messages = MagicMock()

        self.mock_async_service_bus_client.get_queue_sender.return_value.__aenter__.return_value = (
            mock_sender
        )

        await self.service_bus.publish_async(topic, messages)

        # Verify a batch was created and messages were added
        mock_sender.create_message_batch.assert_called_once()
        self.assertEqual(mock_batch.add_message.call_count, len(messages))

        # Verify the batch was sent
        mock_sender.send_messages.assert_called_once_with(mock_batch)

    @patch("cloud_manager.azure_service_bus.logger")
    async def test_publish_async_with_error(self, mock_logger):
        topic = "test_topic_async_error"
        messages = ["async_message_error1", "async_message_error2"]

        mock_sender = MagicMock()
        mock_batch = MagicMock(spec=ServiceBusMessageBatch)
        mock_batch.add_message.side_effect = ServiceBusError("Async publish test error")
        mock_sender.create_message_batch = MagicMock(return_value=asyncio.Future())
        mock_sender.create_message_batch.return_value.set_result(mock_batch)

        self.mock_async_service_bus_client.get_queue_sender.return_value.__aenter__.return_value = (
            mock_sender
        )

        await self.service_bus.publish_async(topic, messages)

        mock_logger.error.assert_called_with(
            f"Service Bus specific error async publishing messages to '{topic}': Async publish test error"
        )


class TestAzureServiceBus(unittest.TestCase):
    @patch("azure.servicebus.aio.ServiceBusClient.from_connection_string")
    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    def setUp(
        self, mock_sync_from_connection_string, mock_async_from_connection_string
    ):
        self.connection_string = "mock_connection_string"
        self.mock_service_bus_client = MagicMock()
        self.mock_async_service_bus_client = MagicMock()
        mock_sync_from_connection_string.return_value = self.mock_service_bus_client
        mock_async_from_connection_string.return_value = (
            self.mock_async_service_bus_client
        )
        self.service_bus = AzureServiceBus(self.connection_string)

    @patch("azure.servicebus.aio.ServiceBusClient.from_connection_string")
    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    def test_init(
        self, mock_sync_from_connection_string, mock_async_from_connection_string
    ):
        AzureServiceBus(self.connection_string)
        mock_sync_from_connection_string.assert_called_once_with(
            self.connection_string, max_lock_renewal_duration=300
        )
        mock_async_from_connection_string.assert_called_once_with(
            self.connection_string
        )

    @patch(
        "cloud_manager.azure_service_bus.ServiceBusClient.from_connection_string",
        side_effect=ValueError("Invalid Connection String"),
    )
    def test_invalid_connection_string(self, mock_from_connection_string):
        with self.assertRaises(ValueError):
            AzureServiceBus("Invalid_Connection_String")

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    def test_publish(self, mock_auto_lock_renewer, mock_from_connection_string):
        topic = "test_topic"
        messages = ["test_message1", "test_message2"]

        # Mocks for message batching
        mock_sender = MagicMock()
        mock_batch = MagicMock(spec=ServiceBusMessageBatch)
        mock_batch.__len__.return_value = len(messages)
        mock_sender.create_message_batch.return_value = mock_batch

        self.mock_service_bus_client.get_queue_sender.return_value.__enter__.return_value = (
            mock_sender
        )

        # Execute the publish method
        self.service_bus.publish(topic, messages)

        # Verify get_queue_sender was called correctly
        self.mock_service_bus_client.get_queue_sender.assert_called_once_with(topic)

        # Verify a batch was created and messages were added
        mock_sender.create_message_batch.assert_called_once()
        self.assertEqual(mock_batch.add_message.call_count, len(messages))

        # Verify the batch was sent
        mock_sender.send_messages.assert_called_once_with(mock_batch)

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch("cloud_manager.azure_service_bus.logger")
    def test_publish_with_error(
        self, mock_logger, mock_auto_lock_renewer, mock_from_connection_string
    ):
        topic = "test_topic"
        messages = ["test_message1", "test_message2"]

        mock_sender = MagicMock()
        mock_batch = MagicMock(spec=ServiceBusMessageBatch)
        mock_batch.add_message.side_effect = ServiceBusError("Test error")
        mock_sender.create_message_batch.return_value = mock_batch
        self.mock_service_bus_client.get_queue_sender.return_value.__enter__.return_value = (
            mock_sender
        )

        self.service_bus.publish(topic, messages)
        mock_logger.error.assert_called_once_with(
            f"Service Bus specific error publishing messages to '{topic}': Test error"
        )

        # Reset mock_logger before the next part of the test
        mock_logger.reset_mock()

        # Setup for the second part of the test
        mock_sender.reset_mock()  # Resetting mock_sender if it's reused
        mock_batch = MagicMock(spec=ServiceBusMessageBatch)
        mock_batch.add_message.side_effect = Exception("Test error")
        mock_sender.create_message_batch.return_value = mock_batch
        self.mock_service_bus_client.get_queue_sender.return_value.__enter__.return_value = (
            mock_sender
        )

        self.service_bus.publish(topic, messages)
        mock_logger.error.assert_called_once_with(
            f"General error publishing messages to '{topic}': Test error"
        )

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    def test_consume(self, mock_auto_lock_renewer, mock_from_connection_string):
        queue = "test_queue"
        messages = ["message1", "message2"]

        mock_receiver = MagicMock()
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        mock_receiver.__iter__.return_value = messages

        callback = MagicMock()
        self.service_bus.consume(queue, callback)

        self.mock_service_bus_client.get_queue_receiver.assert_called_once()
        call_args = self.mock_service_bus_client.get_queue_receiver.call_args
        self.assertEqual(call_args[0][0], queue)
        self.assertEqual(call_args[1]["auto_lock_renew"], True)
        self.assertIsInstance(call_args[1]["auto_lock_renewer"], AutoLockRenewer)

        callback.assert_has_calls([call("message1"), call("message2")])

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch("cloud_manager.azure_service_bus.logger")
    def test_consume_with_error(
        self, mock_logger, mock_auto_lock_renewer, mock_from_connection_string
    ):
        queue = "test_queue"
        mock_receiver = MagicMock()
        mock_receiver.__iter__.side_effect = ServiceBusError("Test error")
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume(queue, callback)
        mock_logger.error.assert_called_once_with(
            f"Error consuming messages from '{queue}': Test error"
        )

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch.object(time, "sleep")  # this is to speed up tests
    def test_consume_indefinitely(
        self, mock_sleep, mock_auto_lock_renewer, mock_from_connection_string
    ):
        queue = "test_queue"
        messages = ["message1", "message2"]

        mock_receiver = MagicMock()
        mock_receiver.__iter__.return_value = iter(messages)
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume_indefinitely(queue, callback, max_number_messages=2)

        callback.assert_has_calls([call("message1"), call("message2")])

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch.object(time, "sleep")  # this is to speed up tests
    @patch("logging.Logger.error")
    def test_consume_indefinitely_with_error(
        self,
        mock_logger_error,
        mock_sleep,
        mock_auto_lock_renewer,
        mock_from_connection_string,
    ):
        queue = "test_queue"

        mock_receiver = MagicMock()
        mock_receiver.__iter__.side_effect = ServiceBusError("Test error")
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume_indefinitely(queue, callback, max_retries=1)

        mock_logger_error.assert_called_with("ServiceBusError encountered: Test error")

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch("time.sleep")  # this is to speed up tests
    @patch("logging.Logger.error")
    def test_consume_indefinitely_with_service_bus_error(
        self,
        mock_logger_error,
        mock_sleep,
        mock_auto_lock_renewer,
        mock_from_connection_string,
    ):
        queue = "test_queue"
        mock_receiver = MagicMock()
        mock_receiver.__iter__.side_effect = ServiceBusError("Test ServiceBusError")
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume_indefinitely(queue, callback, max_retries=1)

        mock_logger_error.assert_called_with(
            "ServiceBusError encountered: Test ServiceBusError"
        )
        mock_sleep.assert_called_once_with(
            5 * (2**1)
        )  # Checking the exponential backoff

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch("time.sleep")  # this is to speed up tests
    @patch("logging.Logger.error")
    def test_consume_indefinitely_with_generic_exception(
        self,
        mock_logger_error,
        mock_sleep,
        mock_auto_lock_renewer,
        mock_from_connection_string,
    ):
        queue = "test_queue"
        mock_receiver = MagicMock()
        mock_receiver.__iter__.side_effect = Exception("Generic Exception")
        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume_indefinitely(queue, callback, max_retries=1)

        mock_logger_error.assert_called_with(
            "Unexpected error encountered: Generic Exception"
        )
        mock_sleep.assert_called_once_with(
            5 * (2**1)
        )  # Checking the exponential backoff

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch.object(time, "sleep")  # this is to speed up tests
    def test_consume_indefinitely_successful_after_failure(
        self, mock_sleep, mock_auto_lock_renewer, mock_from_connection_string
    ):
        queue = "test_queue"

        mock_receiver = MagicMock()
        mock_receiver.__iter__.side_effect = [
            iter(
                [ServiceBusError("Test ServiceBusError")]
            ),  # First iteration raises an error
            iter(["message1"]),  # Second iteration returns a message
        ]

        self.mock_service_bus_client.get_queue_receiver.return_value.__enter__.return_value = (
            mock_receiver
        )

        callback = MagicMock()
        self.service_bus.consume_indefinitely(queue, callback, max_retries=2)

        callback.assert_called_once_with("message1")


if __name__ == "__main__":
    unittest.main()
