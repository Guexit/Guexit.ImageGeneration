import json
import unittest
from unittest.mock import MagicMock, patch

from services import config
from services.image_generation_message_handler import ImageGenerationMessageHandler


class TestImageGenerationMessageHandler(unittest.TestCase):
    def setUp(self):
        self.mock_message = {
            "text_to_style": {"style": "general", "seed": 1, "num_images": 2}
        }
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
        self.patcher_call_image_generation_api = patch(
            "services.message_handlers.call_image_generation_api"
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
        self.patcher_service_bus = patch(
            "services.image_generation_message_handler.AzureServiceBus"
        )
        self.patcher_from_connection_string = patch(
            "azure.servicebus.ServiceBusClient.from_connection_string"
        )
        self.patcher_message_factory = patch(
            "services.image_generation_message_handler.MessageFactory"
        )
        self.patcher_message_interface = patch(
            "services.image_generation_message_handler.MessageTypeInterface"
        )
        self.patcher_message_service_bus_class = patch(
            "services.message_service_bus.MessageServiceBusClass"
        )

    def setUpMocks(
        self,
        mock_azure_blob_storage,
        mock_from_connection_string,
        mock_store_images,
        mock_message_factory,
        mock_message_interface,
    ):
        # Create a mock AzureBlobStorage object and set it as the return value of the AzureBlobStorage constructor
        mock_blob_storage = MagicMock()
        mock_azure_blob_storage.return_value = mock_blob_storage

        # Create a mock ServiceBusClient object and set it as the return value of the from_connection_string method
        mock_service_bus_client = MagicMock()
        mock_from_connection_string.return_value = mock_service_bus_client

        # Create a mock MessageTypeInterface object and set the return value of its process method
        mock_message = MagicMock()
        mock_message.process.return_value = MagicMock()
        mock_message_factory.create_message.return_value = mock_message
        mock_message_interface.return_value = mock_message

        # Configure mock return values
        mock_store_images.return_value = (
            ["path/to/image_0.png"],
            [{"model_path": "model_path_test", "style": "style_test"}],
            MagicMock(),
        )
        mock_blob_storage.push_objects.return_value = [
            "https://example.com/image_0.png"
        ]
        return (
            mock_azure_blob_storage,
            mock_from_connection_string,
            mock_store_images,
            mock_blob_storage,
            mock_message,
        )

    def test_handle_valid_message_multiple_images(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )

            # Call the message handler with the mock message
            image_generation_handler = ImageGenerationMessageHandler()

            # Configure mock return values to handle multiple images
            mock_message.process.return_value = (MagicMock(), MagicMock())
            mock_store_images.return_value = (
                ["path/to/image_0.png", "path/to/image_1.png"],
                [MagicMock(), MagicMock()],
                MagicMock(),
            )
            mock_blob_storage.push_objects.return_value = [
                "https://example.com/image_0.png",
                "https://example.com/image_1.png",
            ]

            # Call the message handler again with the mock message
            image_generation_handler.handle_message(self.mock_message)

            # Assert expected function calls
            self.assertEqual(mock_message.process.call_count, 1)
            self.assertEqual(mock_store_images.call_count, 1)
            self.assertEqual(mock_blob_storage.push_objects.call_count, 1)
            self.assertEqual(mock_publish.call_count, 2)

    def test_handle_invalid_message_format(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )

            invalid_message = '{"message": {"invalid_key": {"prompt": {"positive": "test prompt"}, "seed": 1}}}'

            # Here, we expect the MessageFactory.create_message method to raise an Exception when it encounters the invalid key
            mock_message_factory.create_message.side_effect = Exception("Invalid key")

            with self.assertRaises(Exception):
                image_generation_handler = ImageGenerationMessageHandler()
                image_generation_handler.handle_message(invalid_message)

    def test_process_incoming_message(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )

            # Mock response from Message.process
            mock_message_interface = MagicMock()
            mock_message_interface.process.return_value = {"status": "success"}

            # Mock response from MessageFactory.create_message
            mock_message_factory.create_message.return_value = mock_message_interface

            image_generation_handler = ImageGenerationMessageHandler()
            (
                response,
                processed_message,
            ) = image_generation_handler.process_incoming_message(
                {"text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}}
            )

            mock_message_factory.create_message.assert_called_once()
            mock_message_interface.process.assert_called_once()
            self.assertEqual(response, {"status": "success"})
            self.assertEqual(processed_message, mock_message_interface)

    def test_upload_images_to_blob_storage(self):
        # Setup
        mock_message_interface = MagicMock()
        mock_message_interface.get_file_name.return_value = "test_file_0.png"
        mock_store_images = self.patcher_store_zip_images_temporarily.start()
        mock_store_images.return_value = (
            ["path/to/image_0.png"],
            [{"value": 1}],
            MagicMock(),
        )
        mock_blob_storage = self.patcher_azure_blob_storage.start().return_value
        mock_blob_storage.push_objects.return_value = [
            "https://example.com/image_0.png"
        ]
        mock_patcher_service_bus = self.patcher_service_bus.start()

        image_generation_handler = ImageGenerationMessageHandler()

        # Execute
        (
            file_objects,
            metadata_list,
            temp_dir,
        ) = image_generation_handler.upload_images_to_blob_storage(
            {"status": "success"}, mock_message_interface
        )

        # Verify
        mock_store_images.assert_called_once_with({"status": "success"})
        mock_blob_storage.push_objects.assert_called_once()

        self.assertIsInstance(file_objects, list)
        self.assertEqual(len(file_objects), 1)
        self.assertEqual(file_objects[0], "https://example.com/image_0.png")

        self.assertIsInstance(metadata_list, list)
        self.assertEqual(len(metadata_list), 1)
        self.assertEqual(metadata_list[0], {"value": 1})

        self.assertIsInstance(temp_dir, MagicMock)

    def test_get_num_images_from_message(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            message_json = {"text_to_style": {"style": "general", "num_images": 5}}
            num_images = handler.get_num_images_from_message(message_json)
            self.assertEqual(num_images, 5)

    def test_set_num_images_in_message(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            message_json = {"text_to_style": {"style": "general", "num_images": 5}}
            updated_message_json = handler.set_num_images_in_message(message_json, 3)
            self.assertEqual(updated_message_json["text_to_style"]["num_images"], 3)

    def test_handle_message_with_batching(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )

            mock_blob_storage.push_objects.return_value = [
                "https://example.com/image_0.png",
                "https://example.com/image_1.png",
            ]
            mock_store_images.return_value = (
                ["path/to/image_0.png"],
                [
                    {"model_path": "model_path_test", "style": "style_test"},
                    {"model_path": "model_path_test", "style": "style_test"},
                ],
                MagicMock(),
            )

            image_generation_handler = ImageGenerationMessageHandler(batch_size=2)

            # Mocking message with 5 images to test two full batches and one partial batch
            mock_message_copy = self.mock_message.copy()
            mock_message_copy["text_to_style"]["num_images"] = 6
            image_generation_handler.handle_message(mock_message_copy)

            # Expect the process method to be called 3 times due to batching (2, 2, 2)
            self.assertEqual(mock_message.process.call_count, 3)
            # Expect the store_zip_images_temporarily to be called 3 times
            self.assertEqual(mock_store_images.call_count, 3)
            # Assert the publish method is called 6 times (once for each image)
            self.assertEqual(mock_publish.call_count, 6)

    def test_run_generate_on_command(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            handler.handle_message = MagicMock()

            handler.run(generate_on_command=True, total_images=10)
            handler.handle_message.assert_called_once_with(
                {"text_to_style": {"style": "general", "num_images": 10}}
            )

    def test_run_standard_message_handling(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface, self.patcher_service_bus as mock_service_bus:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            mock_service_bus_instance = MagicMock()
            mock_service_bus.return_value = mock_service_bus_instance

            handler = ImageGenerationMessageHandler()
            handler.run(generate_on_command=False)

            mock_service_bus_instance.consume_indefinitely.assert_called_once()

    def test_init_with_invalid_batch_size(self):
        with self.assertRaises(ValueError) as context:
            ImageGenerationMessageHandler(batch_size=1)
        self.assertIn("Batch size must be greater than 1", str(context.exception))

    def test_call_json_decode_error(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface, self.patcher_service_bus as mock_service_bus:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            with self.assertRaises(json.JSONDecodeError):
                invalid_json_message = "invalid JSON"
                handler(invalid_json_message)

    def test_get_num_images_from_message_exception(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface, self.patcher_service_bus as mock_service_bus:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            with self.assertRaises(ValueError) as context:
                handler.get_num_images_from_message({"invalid": "data"})
            self.assertIn(
                "Could not find num_images in message_json", str(context.exception)
            )

    def test_set_num_images_in_message_exception(self):
        with self.patcher_azure_service_bus_connection_string, self.patcher_image_generation_api, self.patcher_azure_storage_container_name, self.patcher_azure_storage_connection_string, self.patcher_azure_service_bus_topic_name, self.patcher_store_zip_images_temporarily as mock_store_images, self.patcher_azure_blob_storage as mock_azure_blob_storage, self.patcher_publish as mock_publish, self.patcher_from_connection_string as mock_from_connection_string, self.patcher_message_factory as mock_message_factory, self.patcher_message_interface as mock_message_interface, self.patcher_service_bus as mock_service_bus:
            (
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_blob_storage,
                mock_message,
            ) = self.setUpMocks(
                mock_azure_blob_storage,
                mock_from_connection_string,
                mock_store_images,
                mock_message_factory,
                mock_message_interface,
            )
            handler = ImageGenerationMessageHandler()
            with self.assertRaises(ValueError) as context:
                handler.set_num_images_in_message({"invalid": "data"}, 3)
            self.assertIn(
                "Could not find num_images in message_json", str(context.exception)
            )


if __name__ == "__main__":
    unittest.main()
