import unittest
from unittest.mock import MagicMock, patch

from cloud_manager.azure_blob_storage import AzureBlobStorage


class TestAzureBlobStorage(unittest.TestCase):
    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    def setUp(self, mock_from_connection_string):
        self.connection_string = "mock_connection_string"
        mock_blob_service_client = MagicMock()
        mock_from_connection_string.return_value = mock_blob_service_client
        self.azure_cloud = AzureBlobStorage(self.connection_string)

    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    def test_init(self, mock_from_connection_string):
        AzureBlobStorage(self.connection_string)
        mock_from_connection_string.assert_called_once_with(self.connection_string)

    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_push_objects(self, mock_open, mock_from_connection_string):
        container_name = "test"
        objects = [
            {
                "name": "output_nature_12.jpg",
                "path": "examples/data/output_nature_12.png",
                "metadata": {"type": "nature", "id": "12"},
            },
            {
                "name": "output_time_16.jpg",
                "path": "examples/data/output_time_16.png",
                "metadata": {"type": "time", "id": "16"},
            },
        ]

        mock_container_client = MagicMock()
        mock_blob_service_client = MagicMock()
        mock_from_connection_string.return_value = mock_blob_service_client
        mock_blob_service_client.get_container_client.return_value = (
            mock_container_client
        )

        mock_blob_clients = [
            MagicMock(url=f"https://example.com/blob_url_{i}")
            for i in range(len(objects))
        ]
        for mock_blob_client in mock_blob_clients:
            mock_blob_client.upload_blob = MagicMock()
        mock_container_client.get_blob_client.side_effect = mock_blob_clients

        azure_cloud = AzureBlobStorage(self.connection_string)
        blob_urls = azure_cloud.push_objects(container_name, objects)

        expected_urls = [
            f"https://example.com/blob_url_{i}" for i in range(len(objects))
        ]
        self.assertEqual(blob_urls, expected_urls)

        mock_blob_service_client.get_container_client.assert_called_once_with(
            container_name
        )

        for obj in objects:
            mock_container_client.get_blob_client.assert_any_call(obj["name"])
            mock_open.assert_any_call(obj["path"], "rb")

        for i, mock_blob_client in enumerate(mock_blob_clients):
            mock_blob_client.upload_blob.assert_called_once_with(
                unittest.mock.ANY,  # Data stream
                overwrite=False,
                metadata=objects[i].get("metadata", {}),
            )

    def test_push_objects_empty_list(self):
        container_name = "test"
        objects = []

        blob_urls = self.azure_cloud.push_objects(container_name, objects)

        self.assertEqual(blob_urls, [])

    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_push_objects_file_not_found(self, mock_open, mock_from_connection_string):
        container_name = "test"
        objects = [
            {
                "name": "output_nature_12.jpg",
                "path": "examples/data/non_existent_file.png",
            },
        ]

        mock_open.side_effect = FileNotFoundError()

        azure_cloud = AzureBlobStorage(self.connection_string)
        blob_urls = azure_cloud.push_objects(container_name, objects)

        self.assertEqual(blob_urls, [])

    @patch("azure.storage.blob.BlobServiceClient.from_connection_string")
    def test_invalid_connection_string(self, mock_from_connection_string):
        mock_from_connection_string.side_effect = ValueError(
            "Invalid connection string"
        )

        with self.assertRaises(ValueError):
            AzureBlobStorage("invalid_connection_string")


if __name__ == "__main__":
    unittest.main()
