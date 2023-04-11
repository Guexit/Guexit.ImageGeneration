"""Image Generation API Utils"""

import io
import zipfile
from typing import BinaryIO, List

from PIL import Image


def image_to_bytes(image: Image.Image) -> BinaryIO:
    """
    Convert a PIL Image to a bytes object.

    Args:
        image (Image.Image): A PIL Image object.

    Returns:
        BinaryIO: A bytes object containing the image data.
    """
    img_byte_arr = io.BytesIO()
    try:
        image.save(img_byte_arr, format="PNG")
    except Exception as e:
        raise ValueError("Error converting image to bytes") from e
    img_byte_arr.seek(0)
    return img_byte_arr


def get_zip_buffer(images_bytes: List[BinaryIO]) -> BinaryIO:
    """
    Create a zip file in memory containing images from a list of image bytes objects.

    Args:
        images_bytes (List[BinaryIO]): A list of image bytes objects.

    Returns:
        BinaryIO: A bytes object containing the zip file data.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for idx, data in enumerate(images_bytes):
            data.seek(0)
            zip_file.writestr(f"{idx}.png", data.read())

    zip_buffer.seek(0)
    return zip_buffer


def zip_images(images: List[Image.Image]) -> BinaryIO:
    """
    Create a zip file in memory containing images from a list of PIL Image objects.

    Args:
        images (List[Image.Image]): A list of PIL Image objects.

    Returns:
        BinaryIO: A bytes object containing the zip file data.
    """
    zip_buffer = get_zip_buffer([image_to_bytes(image) for image in images])
    return zip_buffer
