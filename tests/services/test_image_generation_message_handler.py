import unittest
from unittest.mock import MagicMock, patch

from services import config
from services.image_generation_message_handler import (
    ImageGenerationMessageHandler,
    create_message_to_send,
)


class TestImageGenerationMessageHandler(unittest.TestCase):
    def setUp(self):
        self.mock_message = '{"message": {"text_to_style": {"style": "general", "seed": 1, "num_images": 2}}}'
        self.patcher_azure_service_bus_connection_string = patch.object(
            config, "AZURE_SERVICE_BUS_CONNECTION_STRING", "mock_connection_string"
        )
        self.patcher_image_generation_api = patch.object(
            config, "IMAGE_GENERATION_API", "http://127.0.0.1:5000"
        )
        self.patcher_azure_storage_container_name = patch.object(
            config, "AZURE_STORAGE_CONTAINER_NAME", "test"
        )
        self.patcher_azure_storage_connection_string = patch.object(
            config, "AZURE_STORAGE_CONNECTION_STRING", "mock_storage_connection_string"
        )
        self.patcher_azure_service_bus_topic_name = patch.object(
            config, "AZURE_SERVICE_BUS_TOPIC_NAME", "guexit-imagegeneration"
        )
        self.patcher_azure_service_bus_message_type = patch.object(
            config,
            "AZURE_SERVICE_BUS_MESSAGE_TYPE",
            "urn:message:Guexit.Game.Messages:ImageGenerated",
        )
        self.patcher_call_image_generation_api = patch(
            "services.image_generation_message_handler.call_image_generation_api"
        )
        self.patcher_store_zip_images_temporarily = patch(
            "services.image_generation_message_handler.store_zip_images_temporarily"
        )
        self.patcher_azure_blob_storage = patch(
            "services.image_generation_message_handler.AzureBlobStorage"
        )
        self.patcher_publish = patch(
            "cloud_manager.azure_service_bus.AzureServiceBus.publish"
        )
        self.patcher_from_connection_string = patch(
            "azure.servicebus.ServiceBusClient.from_connection_string"
        )

    def setUpMocks(
        self,
        mock_azure_blob_storage,
        mock_from_connection_string,
        mock_store_images,
        mock_api_call,
    ):
        # Create a mock AzureBlobStorage object and set it as the return value of the AzureBlobStorage constructor
        mock_blob_storage = MagicMock()
        mock_azure_blob_storage.return_value = mock_blob_storage

        # Create a mock ServiceBusClient object and set it as the return value of the from_connection_string method
        mock_service_bus_client = MagicMock()
        mock_from_connection_string.return_value = mock_service_bus_client

        # Configure mock return values
        mock_api_call.return_value = MagicMock()
        mock_store_images.return_value = (["path/to/image_0.png"], MagicMock())
        mock_blob_storage.push_objects.return_value = [
            "https://example.com/image_0.png"
        ]
        return (
            mock_azure_blob_storage,
            mock_from_connection_string,
            mock_store_images,
            mock_api_call,
            mock_blob_storage,
        )

    def test_handle_valid_message_multiple_images(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_azure_service_bus_message_type, self.patcher_call_image_generation_api as mock_api_call, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
                mock_blob_storage,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
            )

            # Call the message handler with the mock message
            image_generation_handler = ImageGenerationMessageHandler()
            image_generation_handler.handle_message(self.mock_message)

            # Configure mock return values to handle multiple images
            mock_api_call.return_value = MagicMock()
            mock_store_images.return_value = (
                ["path/to/image_0.png", "path/to/image_1.png"],
                MagicMock(),
            )
            mock_blob_storage.push_objects.return_value = [
                "https://example.com/image_0.png",
                "https://example.com/image_1.png",
            ]

            # Call the message handler again with the mock message
            image_generation_handler.handle_message(self.mock_message)

            # Assert expected function calls
            self.assertEqual(mock_api_call.call_count, 2)
            self.assertEqual(mock_store_images.call_count, 2)
            self.assertEqual(mock_blob_storage.push_objects.call_count, 2)
            self.assertEqual(mock_publish.call_count, 3)

    def test_handle_invalid_message_format(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_azure_service_bus_message_type, self.patcher_call_image_generation_api as mock_api_call, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
                mock_blob_storage,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
            )

            invalid_message = '{"message": {"invalid_key": {"prompt": {"positive": "test prompt"}, "seed": 1}}}'

            with self.assertRaises(Exception):
                image_generation_handler = ImageGenerationMessageHandler()
                image_generation_handler.handle_message(invalid_message)

    def test_process_incoming_message(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_azure_service_bus_message_type, self.patcher_call_image_generation_api as mock_api_call, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
                mock_blob_storage,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
            )

            image_generation_handler = ImageGenerationMessageHandler()
            (
                response,
                processed_message,
            ) = image_generation_handler.process_incoming_message(
                {"text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}}
            )

            mock_api_call.assert_called_once()
            self.assertIsInstance(response, MagicMock)
            self.assertEqual(
                processed_message, {"prompt": {"positive": "test prompt"}, "seed": 1}
            )

    def test_upload_images_to_blob_storage(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_azure_service_bus_message_type, self.patcher_call_image_generation_api as mock_api_call, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
                mock_blob_storage,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_api_call,
            )

            image_generation_handler = ImageGenerationMessageHandler()
            (
                file_objects,
                temp_dir,
            ) = image_generation_handler.upload_images_to_blob_storage(
                MagicMock(), {"style": "general", "seed": 1}
            )

            mock_store_images.assert_called_once()
            mock_blob_storage.push_objects.assert_called_once()
            self.assertIsInstance(file_objects, list)
            self.assertIsInstance(temp_dir, MagicMock)

    def test_create_message_to_send(self):
        file_objects = [{"name": "test_file_0.png", "path": "path/to/image_0.png"}]
        message = create_message_to_send(file_objects)

        self.assertIsInstance(message, str)
        self.assertIn('"url":', message)


if __name__ == "__main__":
    unittest.main()
