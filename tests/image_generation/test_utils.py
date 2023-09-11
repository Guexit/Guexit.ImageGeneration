import io
import unittest
from unittest.mock import MagicMock, patch

import requests

from image_generation import utils


class TestUtils(unittest.TestCase):
    @patch("image_generation.utils.requests.post")
    def test_call_image_generation_api(self, mock_post):
        mock_post.return_value.status_code = 200
        host = "http://localhost:5000"
        endpoint = "/text_to_image"
        request_object = {"model_path": "test_model_path"}

        response = utils.call_image_generation_api(host, endpoint, request_object)

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once_with(f"{host}{endpoint}", json=request_object)

    @patch("image_generation.utils.requests.post")
    def test_call_image_generation_api_failure(self, mock_post):
        mock_post.return_value.status_code = 404  # Simulate failure
        host = "http://localhost:5000"
        endpoint = "/text_to_image"
        request_object = {"model_path": "test_model_path"}

        with self.assertRaises(Exception) as context:
            utils.call_image_generation_api(host, endpoint, request_object)

        self.assertTrue(
            f"Request to {host}{endpoint} failed with status code 404"
            in str(context.exception)
        )

    @patch("image_generation.utils.requests.get")
    def test_wait_for_service(self, mock_get):
        mock_get.return_value.status_code = 200
        host = "http://localhost:5000"
        endpoint = "/healthcheck"

        utils.wait_for_service(host, endpoint)

    @patch("image_generation.utils.requests.get")
    def test_wait_for_service_non_200_status(self, mock_get):
        mock_get.return_value.status_code = 404
        host = "http://localhost:5000"
        endpoint = "/healthcheck"

        with self.assertRaises(TimeoutError):
            utils.wait_for_service(host, endpoint, timeout=1)

    @patch("image_generation.utils.requests.get")
    def test_wait_for_service_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Mocked exception")
        host = "http://localhost:5000"
        endpoint = "/healthcheck"

        with self.assertRaises(TimeoutError):
            utils.wait_for_service(host, endpoint, timeout=1)

    @patch("image_generation.utils.time.time")
    @patch("image_generation.utils.requests.get")
    def test_wait_for_service_timeout(self, mock_get, mock_time):
        mock_get.return_value.status_code = 404  # Simulate service not available
        mock_time.side_effect = iter([0, 0.5, 1, 1.5, 2])  # Simulate elapsed time
        host = "http://localhost:5000"
        endpoint = "/healthcheck"

        with self.assertRaises(TimeoutError):
            utils.wait_for_service(host, endpoint, timeout=1)

    @patch("image_generation.utils.zipfile.ZipFile")
    @patch("image_generation.utils.TemporaryDirectory")
    @patch("image_generation.utils.Image.open")
    def test_store_zip_images_temporarily(
        self, mock_image_open, mock_tmp_dir, mock_zip
    ):
        mock_response = MagicMock()
        mock_response.content = b"dummy_content"
        mock_zip.return_value.namelist.return_value = ["image1.png", "image2.jpg"]

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        file_paths, metadata_list, temp_dir = utils.store_zip_images_temporarily(
            mock_response
        )

        self.assertEqual(len(file_paths), 2)
        self.assertEqual(len(metadata_list), 2)
        self.assertIsInstance(mock_zip.call_args[0][0], io.BytesIO)

    @patch("image_generation.utils.torch.cuda.mem_get_info")
    def test_enough_gpu_memory(self, mock_mem_info):
        mock_mem_info.return_value = [0, 1024 * 1024 * 1024 * 4]  # 4 GB

        self.assertTrue(utils.enough_gpu_memory(minimum_gb=3.0))


if __name__ == "__main__":
    unittest.main()
