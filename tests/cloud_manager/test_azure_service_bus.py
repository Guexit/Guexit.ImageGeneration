import time
import unittest
from unittest.mock import MagicMock, call, patch

from azure.servicebus._common.auto_lock_renewer import AutoLockRenewer
from azure.servicebus.exceptions import ServiceBusError

from cloud_manager.azure_service_bus import AzureServiceBus


class TestAzureServiceBus(unittest.TestCase):
    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    def setUp(self, mock_from_connection_string):
        self.connection_string = "mock_connection_string"
        self.mock_service_bus_client = MagicMock()
        mock_from_connection_string.return_value = self.mock_service_bus_client
        self.service_bus = AzureServiceBus(self.connection_string)

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    def test_init(self, mock_from_connection_string):
        AzureServiceBus(self.connection_string)
        mock_from_connection_string.assert_called_once_with(
            self.connection_string, max_lock_renewal_duration=300
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
        message = "test_message"

        mock_sender = MagicMock()
        self.mock_service_bus_client.get_queue_sender.return_value.__enter__.return_value = (
            mock_sender
        )

        self.service_bus.publish(topic, message)

        self.mock_service_bus_client.get_queue_sender.assert_called_once_with(topic)
        mock_sender.send_messages.assert_called_once()
        sent_message = mock_sender.send_messages.call_args[0][0]
        sent_message_body = b"".join(sent_message.body).decode("utf-8")
        self.assertEqual(sent_message_body, message)

    @patch("azure.servicebus.ServiceBusClient.from_connection_string")
    @patch("cloud_manager.azure_service_bus.AutoLockRenewer")
    @patch("cloud_manager.azure_service_bus.logger")
    def test_publish_with_error(
        self, mock_logger, mock_auto_lock_renewer, mock_from_connection_string
    ):
        topic = "test_topic"
        message = "test_message"

        mock_sender = MagicMock()
        mock_sender.send_messages.side_effect = ServiceBusError("Test error")
        self.mock_service_bus_client.get_queue_sender.return_value.__enter__.return_value = (
            mock_sender
        )

        self.service_bus.publish(topic, message)
        mock_logger.error.assert_called_once_with(
            f"Error publishing message to '{topic}': Test error"
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
