import io
import os
import zipfile
from tempfile import TemporaryDirectory

import grequests
from PIL import Image
import torch

from image_generation.custom_logging import set_logger

logger = set_logger("Image Generation Utils")


def call_image_generation_api(host, endpoint, request_object: dict):
    logger.info(f"Calling {host}{endpoint}")
    logger.info(f"Request object: {request_object}")
    # Call Image Generation API
    async_req = grequests.post(f"{host}{endpoint}", json=request_object)
    response = grequests.map([async_req])[0]
    # Check if the request was successful
    if response.status_code == 200:
        # Return the response
        return response
    else:
        raise Exception(f"Request failed with status code {response.status_code}")


def store_zip_images_temporarily(response):
    """
    Store images from a zip file in a temporary folder.
    Returns a list of file paths to the stored images.
    """
    # Extract images from the zip file
    z = zipfile.ZipFile(io.BytesIO(response.content))

    # Create a temporary directory to store images
    temp_dir = TemporaryDirectory()
    file_paths = []

    # Iterate through the files in the zip file
    for file_name in z.namelist():
        if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            # Extract the image data and open it with Pillow
            with z.open(file_name) as image_file:
                img = Image.open(image_file)

                # Save the image to the temporary directory
                file_path = os.path.join(temp_dir.name, os.path.basename(file_name))
                img.save(file_path)
                file_paths.append(file_path)

    return file_paths, temp_dir

def bytesto(bytes, to, bsize=1024):
    """
    Convert bytes to megabytes, etc.
    sample code:
        print('mb= ' + str(bytesto(314575262000000, 'm')))
    sample output: 
        mb= 300002347.946
    """

    a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
    r = float(bytes)
    for i in range(a[to]):
        r = r / bsize

    return(r)

def enough_gpu_memory(minimum_gb=3.0):
    total_memory = torch.cuda.mem_get_info()[1]
    total_memory_gb = bytesto(total_memory, 'g')
    return total_memory_gb >= minimum_gb