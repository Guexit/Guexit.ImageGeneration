"""Image Generation API Utils"""

import io
from typing import List
import zipfile
from PIL import Image


def image_to_bytes(image: Image.Image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr

def get_zip_buffer(images_bytes: List[bytes]):
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for idx, data in enumerate(images_bytes):
            zip_file.writestr(f"{idx}.png", data.read())

    zip_buffer.seek(0)
    return zip_buffer

def zip_images(images: List[Image.Image]):
    zip_buffer = get_zip_buffer(
        [image_to_bytes(image) for image in images]
    )
    return zip_buffer