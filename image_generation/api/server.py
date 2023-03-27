import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from image_generation.logging import set_logger
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.api.models import TextToImageInput
from image_generation.api.utils import store_images_locally, zip_images
from cloud_manager.azure_blob_storage import AzureBlobStorage

as_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "test")

logger = set_logger("Image Generation API")
logger.info("--- Image Generation API ---")

app = FastAPI()
model = StableDiffusionHandler("stabilityai/stable-diffusion-2-1-base")

azure_cloud = AzureBlobStorage(as_connection_string)


# health check
@app.get("/")
async def root():
    logger.info("Health check")
    return {"status": "healthy"}


# text to image
@app.post("/text_to_image", response_model=None)
async def text_to_image(text_to_image_input: TextToImageInput):
    logger.info(f"Text to image request: {text_to_image_input}")
    images = model.txt_to_img(text_to_image_input.text_to_image)

    if text_to_image_input.upload_images:
        logger.info("Uploading images")
        file_paths, temp_dir = store_images_locally(images)
        file_objects = [
            {"name": f"image_{i}.png", "path": file_path}
            for i, file_path in enumerate(file_paths)
        ]
        blob_urls = azure_cloud.push_objects(container_name, file_objects)
        temp_dir.cleanup()
        logger.info(f"Blob urls: {blob_urls}")
        # TODO: Use Azure Service Bus

    if text_to_image_input.return_images:
        logger.info("Zipping images")
        images_bytes = zip_images(images)
        response = StreamingResponse(
            images_bytes, media_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=images.zip"
        return response
