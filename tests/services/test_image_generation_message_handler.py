import unittest
from unittest.mock import MagicMock, patch
from services.image_generation_message_handler import ImageGenerationMessageHandler
from services import config


class TestImageGenerationMessageHandler(unittest.TestCase):
    def test_handle_valid_message(self):
        # Create a mock message with the required data
        mock_message = '{"message": {"text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}}}'

        # Mock external functions and environment variables
        with patch.object(
            config, "AZURE_SERVICE_BUS_CONNECTION_STRING", "mock_connection_string"
        ), patch.object(
            config, "IMAGE_GENERATION_API", "http://127.0.0.1:5000"
        ), patch.object(
            config, "AZURE_STORAGE_CONTAINER_NAME", "test"
        ), patch.object(
            config, "AZURE_STORAGE_CONNECTION_STRING", "mock_storage_connection_string"
        ), patch.object(
            config, "AZURE_SERVICE_BUS_TOPIC_NAME", "guexit-imagegeneration"
        ), patch.object(
            config,
            "AZURE_SERVICE_BUS_MESSAGE_TYPE",
            "urn:message:Guexit.Game.Messages:ImageGenerated",
        ), patch(
            "services.image_generation_message_handler.call_image_generation_api"
        ) as mock_api_call, patch(
            "services.image_generation_message_handler.store_zip_images_temporarily"
        ) as mock_store_images, patch(
            "services.image_generation_message_handler.AzureBlobStorage"
        ) as mock_azure_blob_storage, patch(
            "cloud_manager.azure_service_bus.AzureServiceBus.publish"
        ) as mock_publish, patch(
            "azure.servicebus.ServiceBusClient.from_connection_string"
        ) as mock_from_connection_string:
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

            # Call the message handler with the mock message
            image_generation_handler = ImageGenerationMessageHandler()
            image_generation_handler.handle_message(mock_message)

            # Assert expected function calls
            mock_api_call.assert_called_once()
            mock_store_images.assert_called_once()
            mock_blob_storage.push_objects.assert_called_once()
            mock_publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()
