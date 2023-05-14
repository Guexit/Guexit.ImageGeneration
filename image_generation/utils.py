import io
import os
import time
import zipfile
from tempfile import TemporaryDirectory

import requests
import torch
from PIL import Image

from image_generation.custom_logging import set_logger

logger = set_logger("Image Generation Utils")

TIMEOUT = 60
MINIMUM_MEMORY_GB = 3.0
VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")


def call_image_generation_api(host, endpoint, request_object: dict):
    url = f"{host}{endpoint}"
    logger.info(f"Calling {url}")
    logger.info(f"Request object: {request_object}")
    response = requests.post(url, json=request_object)

    if response.status_code != 200:
        raise Exception(
            f"Request to {url} failed with status code {response.status_code}"
        )

    return response


def wait_for_service(host, endpoint="/healthcheck", timeout=TIMEOUT):
    url = f"{host}{endpoint}"
    logger.info(f"Waiting for the service at {url} to become available")
    start_time = time.time()

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("Service available!")
                break
            else:
                logger.info(
                    f"Service responded with status {response.status_code}. Retrying..."
                )
        except requests.exceptions.RequestException as e:
            logger.info(f"Failed to connect to service: {e}. Retrying...")

        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Timeout waiting for the service at {url} to become available"
            )

        time.sleep(1)


def store_zip_images_temporarily(response):
    z = zipfile.ZipFile(io.BytesIO(response.content))
    temp_dir = TemporaryDirectory()
    file_paths = []

    for file_name in z.namelist():
        if file_name.lower().endswith(VALID_IMAGE_EXTENSIONS):
            with z.open(file_name) as image_file:
                img = Image.open(image_file)
                file_path = os.path.join(temp_dir.name, os.path.basename(file_name))
                img.save(file_path)
                file_paths.append(file_path)

    return file_paths, temp_dir


def enough_gpu_memory(minimum_gb=MINIMUM_MEMORY_GB):
    def convert_bytes_to(bytes, to, bsize=1024):
        a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
        r = float(bytes)
        for i in range(a[to]):
            r = r / bsize
        return r

    total_memory = torch.cuda.mem_get_info()[1]
    total_memory_gb = convert_bytes_to(total_memory, "g")
    logger.info(f"Total GPU memory: {total_memory_gb} GB")
    return total_memory_gb >= minimum_gb
