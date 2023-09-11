import io
import unittest
import zipfile
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from PIL import Image

from image_generation.api.models import TextToImage, TextToStyle
from image_generation.api.server import app

client = TestClient(app)


class TestServer(unittest.TestCase):
    @patch("image_generation.api.server.get_model")
    def test_healthcheck(self, mock_get_model):
        response = client.get("/healthcheck")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    @patch("image_generation.api.server.get_model")
    def test_text_to_image(self, mock_get_model):
        # Mock the get_model function and the txt_to_img method
        mock_stable_diffusion_handler_instance = MagicMock()
        mock_get_model.return_value = mock_stable_diffusion_handler_instance

        # Create mock PIL Image objects
        mock_image1 = Image.new("RGB", (512, 688), color="red")
        mock_image2 = Image.new("RGB", (512, 688), color="blue")

        mock_stable_diffusion_handler_instance.txt_to_img.return_value = [
            mock_image1,
            mock_image2,
        ]

        text_to_image_data = TextToImage(
            model_path="prompthero/openjourney-v4",
            model_scheduler="euler_a",
            prompt={
                "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                "negative": "bad quality, malformed",
                "guidance_scale": 16.5,
            },
            height=688,
            width=512,
            num_inference_steps=50,
            num_images=2,
            seed=-1,
        )

        response = client.post("/text_to_image", json=text_to_image_data.dict())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Disposition"], "attachment; filename=images.zip"
        )

        # Test if response is a valid zip file
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)

            # Test if the names of the files are different
            file_names = zip_file.namelist()
            self.assertEqual(len(file_names), len(set(file_names)))

    @patch("image_generation.api.server.get_model")
    def test_text_to_image_exception(self, mock_get_model):
        mock_get_model.side_effect = Exception("Some error")
        text_to_image_data = TextToImage(
            model_path="prompthero/openjourney-v4",
            model_scheduler="euler_a",
            prompt={
                "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                "negative": "bad quality, malformed",
                "guidance_scale": 16.5,
            },
            height=688,
            width=512,
            num_inference_steps=50,
            num_images=2,
            seed=-1,
        )
        response = client.post("/text_to_image", json=text_to_image_data.dict())

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred during text_to_image processing."},
        )

    @patch("image_generation.api.server.get_model")
    @patch(
        "image_generation.api.models.STYLES",
        {
            "some_style_name": [
                {
                    "model_path": "prompthero/openjourney-v4",
                    "model_scheduler": "euler_a",
                    "prompt": {
                        "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                        "negative": "bad quality, malformed",
                        "guidance_scale": 16.5,
                    },
                    "height": 688,
                    "width": 512,
                    "num_inference_steps": 50,
                    "num_images": 1,
                    "seed": -1,
                }
            ]
        },
    )
    def test_text_to_style(self, mock_get_model):
        # Mock the get_model function and the txt_to_img method
        mock_stable_diffusion_handler_instance = MagicMock()
        mock_get_model.return_value = mock_stable_diffusion_handler_instance

        # Create mock PIL Image objects
        mock_image1 = Image.new("RGB", (512, 688), color="red")

        mock_stable_diffusion_handler_instance.txt_to_img.return_value = [
            mock_image1,
        ]

        text_to_style_data = TextToStyle(
            num_images=2,
            style="some_style_name",
        )

        response = client.post("/text_to_style", json=text_to_style_data.dict())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Disposition"], "attachment; filename=images.zip"
        )

        # Test if response is a valid zip file
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)

    @patch("image_generation.api.server.get_model")
    @patch(
        "image_generation.api.models.STYLES",
        {
            "some_style_name": [
                {
                    "model_path": "prompthero/openjourney-v4",
                    "model_scheduler": "euler_a",
                    "prompt": {
                        "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                        "negative": "bad quality, malformed",
                        "guidance_scale": 16.5,
                    },
                    "height": 688,
                    "width": 512,
                    "num_inference_steps": 50,
                    "num_images": 1,
                    "seed": -1,
                }
            ]
        },
    )
    def test_text_to_style_exception(self, mock_get_model):
        mock_get_model.side_effect = Exception("Some error")
        text_to_style_data = TextToStyle(
            num_images=2,
            style="some_style_name",
        )

        response = client.post("/text_to_style", json=text_to_style_data.dict())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred during text_to_image_with_style processing."},
        )


if __name__ == "__main__":
    unittest.main()
