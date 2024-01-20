import json
import unittest
from unittest.mock import patch

from services.message_service_bus import MessageServiceBusClass


class TestMessageServiceBus(unittest.TestCase):
    """
    Test the MessageServiceBusClass class.
    """

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_without_metadata_or_tags_to_keep(self) -> None:
        """
        Test the create_message_to_send method.
        """
        self.metadata_fields_to_keep = []
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=self.metadata_fields_to_keep,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        metadata = {
            "model_path": "test_model",
            "style": "test_style",
            "other": "other",
        }
        expected_message = json.dumps(
            {
                "url": "https://test.blob.core.windows.net/test/test1.jpg",
                "tags": ["image_generation_version:0.7.2"],
            }
        )
        message = self.message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url, metadata=metadata
        )
        self.assertEqual(message, expected_message)

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_with_metadata_to_keep(self) -> None:
        """
        Test the create_message_to_send method.
        """
        self.metadata_fields_to_keep = ["model_path", "style"]
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=self.metadata_fields_to_keep,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        metadata = {
            "model_path": "test_model",
            "style": "test_style",
            "other": "other",
        }
        expected_message = json.dumps(
            {
                "url": "https://test.blob.core.windows.net/test/test1.jpg",
                "tags": [
                    "model_path:test_model",
                    "style:test_style",
                    "image_generation_version:0.7.2",
                ],
            }
        )
        message = self.message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url, metadata=metadata
        )
        self.assertEqual(message, expected_message)

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_with_metadata_to_keep_and_tags_to_add(self) -> None:
        """
        Test the create_message_to_send method.
        """
        self.metadata_fields_to_keep = ["model_path", "style"]
        self.tags_to_add = {"test": "test"}
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=self.metadata_fields_to_keep,
            tags_to_add=self.tags_to_add,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        metadata = {
            "model_path": "test_model",
            "style": "test_style",
            "other": "other",
        }
        expected_message = json.dumps(
            {
                "url": "https://test.blob.core.windows.net/test/test1.jpg",
                "tags": [
                    "model_path:test_model",
                    "style:test_style",
                    "test:test",
                    "image_generation_version:0.7.2",
                ],
            }
        )
        message = self.message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url, metadata=metadata
        )
        self.assertEqual(message, expected_message)

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_with_tags_to_add(self) -> None:
        """
        Test the create_message_to_send method.
        """
        self.metadata_fields_to_keep = []
        self.tags_to_add = {"test": "test"}
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=self.metadata_fields_to_keep,
            tags_to_add=self.tags_to_add,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        metadata = {
            "model_path": "test_model",
            "style": "test_style",
            "other": "other",
        }
        expected_message = json.dumps(
            {
                "url": "https://test.blob.core.windows.net/test/test1.jpg",
                "tags": [
                    "test:test",
                    "image_generation_version:0.7.2",
                ],
            }
        )
        message = self.message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url, metadata=metadata
        )
        self.assertEqual(message, expected_message)

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_with_tags_to_add_and_no_metadata(self) -> None:
        """
        Test the create_message_to_send method.
        """
        self.metadata_fields_to_keep = []
        self.tags_to_add = {"test": "test"}
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=self.metadata_fields_to_keep,
            tags_to_add=self.tags_to_add,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        expected_message = json.dumps(
            {
                "url": "https://test.blob.core.windows.net/test/test1.jpg",
                "tags": [
                    "test:test",
                    "image_generation_version:0.7.2",
                ],
            }
        )
        message = self.message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url
        )
        self.assertEqual(message, expected_message)

    @patch.object(MessageServiceBusClass, "get_package_version", return_value="0.7.2")
    def test_create_message_to_send_with_version(self, mock_get_package_version):
        """
        Test the create_message_to_send method with package version included.
        """
        metadata_fields_to_keep = ["model_path", "style"]
        tags_to_add = {"test": "test"}
        message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=metadata_fields_to_keep,
            tags_to_add=tags_to_add,
        )
        file_blob_url = "https://test.blob.core.windows.net/test/test1.jpg"
        metadata = {
            "model_path": "test_model",
            "style": "test_style",
            "other": "other",
        }
        expected_tags = [
            "model_path:test_model",
            "style:test_style",
            "test:test",
            "image_generation_version:0.7.2",
        ]
        expected_message = json.dumps(
            {
                "url": file_blob_url,
                "tags": expected_tags,
            }
        )
        message = message_service_bus.create_message_to_send(
            file_blob_url=file_blob_url, metadata=metadata
        )

        self.assertEqual(message, expected_message)
