import io
import json
import unittest
import uuid
import zipfile

from PIL import Image

from image_generation.api.utils import (
    construct_filename,
    get_zip_buffer,
    image_to_bytes,
    zip_images,
)


class TestAPIUtils(unittest.TestCase):
    def test_image_to_bytes(self):
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = image_to_bytes(image)

        self.assertIsInstance(image_bytes, io.BytesIO)

        with self.assertRaises(ValueError):
            image_to_bytes("invalid_image")

    def test_image_to_bytes_with_metadata(self):
        image = Image.new("RGB", (100, 100), color="red")
        metadata = {"key": {"nested_key": "nested_value"}}
        image_bytes = image_to_bytes(image, metadata)

        self.assertIsInstance(image_bytes, io.BytesIO)

        with Image.open(image_bytes) as img:
            self.assertEqual(
                json.loads(img.info["key"]), {"nested_key": "nested_value"}
            )

    def test_image_to_bytes_invalid(self):
        with self.assertRaises(ValueError):
            image_to_bytes("invalid_image")

    def test_get_zip_buffer(self):
        images_bytes = [
            ("file1", io.BytesIO(b"mock_image1")),
            ("file2", io.BytesIO(b"mock_image2")),
        ]
        zip_buffer = get_zip_buffer(images_bytes)

        self.assertIsInstance(zip_buffer, io.BytesIO)

        with zipfile.ZipFile(io.BytesIO(zip_buffer.read()), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)
            self.assertIn("file1.png", zip_file.namelist())
            self.assertIn("file2.png", zip_file.namelist())

            self.assertEqual(zip_file.read("file1.png"), b"mock_image1")
            self.assertEqual(zip_file.read("file2.png"), b"mock_image2")

    def test_zip_images(self):
        images = [
            ("file1", Image.new("RGB", (100, 100), color="red"), {"meta1": "data1"}),
            ("file2", Image.new("RGB", (100, 100), color="green"), {"meta2": "data2"}),
        ]
        zip_buffer = zip_images(images)

        self.assertIsInstance(zip_buffer, io.BytesIO)

        with zipfile.ZipFile(io.BytesIO(zip_buffer.read()), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)
            self.assertIn("file1.png", zip_file.namelist())
            self.assertIn("file2.png", zip_file.namelist())

            file1_data = zip_file.read("file1.png")
            file2_data = zip_file.read("file2.png")

            self.assertTrue(file1_data.startswith(b"\x89PNG"))
            self.assertTrue(file2_data.startswith(b"\x89PNG"))

            with Image.open(io.BytesIO(file1_data)) as img:
                self.assertEqual(img.info["meta1"], "data1")
            with Image.open(io.BytesIO(file2_data)) as img:
                self.assertEqual(img.info["meta2"], "data2")

    def test_zip_images_with_different_formats(self):
        images = [
            ("file1", Image.new("RGB", (100, 100), color="red"), {"meta1": "data1"}),
            ("file2", Image.new("L", (50, 50), color="gray"), {"meta2": "data2"}),
        ]
        zip_buffer = zip_images(images)

        self.assertIsInstance(zip_buffer, io.BytesIO)

        with zipfile.ZipFile(io.BytesIO(zip_buffer.read()), "r") as zip_file:
            self.assertEqual(len(zip_file.namelist()), 2)
            self.assertIn("file1.png", zip_file.namelist())
            self.assertIn("file2.png", zip_file.namelist())

            with Image.open(io.BytesIO(zip_file.read("file1.png"))) as img:
                self.assertEqual(img.size, (100, 100))
                self.assertEqual(img.mode, "RGB")

            with Image.open(io.BytesIO(zip_file.read("file2.png"))) as img:
                self.assertEqual(img.size, (50, 50))
                self.assertEqual(img.mode, "L")

    def test_construct_filename(self):
        filename = construct_filename("my_file", 123)
        self.assertTrue(filename.startswith("my_file"))
        self.assertTrue(filename.endswith("123"))

    def test_construct_filename_with_invalid_chars(self):
        filename = construct_filename("my:file?", 123)
        sanitized_filename = "myfile_123"

        self.assertEqual(filename, sanitized_filename)

    def test_construct_filename_with_negative_seed(self):
        filename = construct_filename("my_file", -1)
        self.assertTrue(filename.startswith("my_file_-1_"))

    def test_construct_filename_with_uuid(self):
        filename = construct_filename("my_file", -1)
        uuid_part = filename.split("_-1_")[-1]

        try:
            uuid.UUID(uuid_part, version=4)
        except ValueError:
            self.fail("UUID part of filename is not a valid UUID.")


if __name__ == "__main__":
    unittest.main()
