import io
import unittest
import zipfile

from PIL import Image

from image_generation.api.utils import get_zip_buffer, image_to_bytes, zip_images


class TestUtils(unittest.TestCase):
    def test_image_to_bytes(self):
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = image_to_bytes(image)

        self.assertIsInstance(image_bytes, io.BytesIO)

        with self.assertRaises(ValueError):
            image_to_bytes("invalid_image")

    def test_get_zip_buffer(self):
        images_bytes = [io.BytesIO(b"mock_image1"), io.BytesIO(b"mock_image2")]
        zip_buffer = get_zip_buffer(images_bytes)

        self.assertIsInstance(zip_buffer, io.BytesIO)

        with zipfile.ZipFile(io.BytesIO(zip_buffer.read()), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)

    def test_zip_images(self):
        images = [
            Image.new("RGB", (100, 100), color="red"),
            Image.new("RGB", (100, 100), color="green"),
        ]
        zip_buffer = zip_images(images)

        self.assertIsInstance(zip_buffer, io.BytesIO)

        with zipfile.ZipFile(io.BytesIO(zip_buffer.read()), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)


if __name__ == "__main__":
    unittest.main()
