"""Image Generation API Utils"""

import io
import json
import uuid
import zipfile
from typing import BinaryIO, List, Tuple

from PIL import Image, PngImagePlugin


def image_to_bytes(image: Image.Image, metadata: dict = None) -> BinaryIO:
    """
    Convert a PIL Image to a bytes object.

    Args:
        image (Image.Image): A PIL Image object.
        metadata (dict): A dictionary containing metadata to add to the image.

    Returns:
        BinaryIO: A bytes object containing the image data.
    """
    img_byte_arr = io.BytesIO()

    if metadata:
        pnginfo = PngImagePlugin.PngInfo()
        for k, v in metadata.items():
            # We store each item in metadata as a string, if it's not a string already, we convert it to JSON.
            # The metadata values must be string type for PNGs.
            if not isinstance(v, str):
                v = json.dumps(v)
            pnginfo.add_text(k, v, zip=True)  # Zip compression for text chunks
        try:
            image.save(img_byte_arr, format="PNG", pnginfo=pnginfo)
        except Exception as e:
            raise ValueError("Error converting image to bytes with metadata") from e
    else:
        try:
            image.save(img_byte_arr, format="PNG")
        except Exception as e:
            raise ValueError("Error converting image to bytes") from e
    img_byte_arr.seek(0)
    return img_byte_arr


def get_zip_buffer(images_data: List[Tuple[str, BinaryIO]]) -> BinaryIO:
    """
    Create a zip file in memory containing images from a list of image bytes objects.

    Args:
        images_data (List[Tuple[str, BinaryIO]]): A list of tuples. Each tuple contains a filename and an image bytes object.

    Returns:
        BinaryIO: A bytes object containing the zip file data.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, data in images_data:  # Unpack the filename and data
            data.seek(0)
            zip_file.writestr(f"{filename}.png", data.read())  # Use the filename here

    zip_buffer.seek(0)
    return zip_buffer


def zip_images(images: List[Tuple[str, Image.Image, dict]]) -> BinaryIO:
    """
    Create a zip file in memory containing images from a list of PIL Image objects.

    Args:
        images (List[Tuple[str, Image.Image]]): A list of tuples. Each tuple contains a filename and a PIL Image object.

    Returns:
        BinaryIO: A bytes object containing the zip file data.
    """
    zip_buffer = get_zip_buffer(
        [
            (filename, image_to_bytes(image, metadata))
            for filename, image, metadata in images
        ]
    )
    return zip_buffer


def construct_filename(filename, seed, max_length=200):
    invalid_chars = '/\\:*?"<>|'  # Characters that are invalid in file names
    for char in invalid_chars:
        filename = filename.replace(char, "")  # Replace invalid characters with nothing
    if seed == -1:
        filename_id = "_-1_{}".format(uuid.uuid4())
    else:
        filename_id = "_{}".format(seed)
    # Truncate the filename to fit within the maximum length
    max_filename_length = max_length - len(filename_id)
    filename = filename[:max_filename_length]

    filename = filename + filename_id
    return filename
