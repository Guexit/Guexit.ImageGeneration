import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from logging.config import dictConfig
import logging
from image_generation.logging import LogConfig
from stable_diffusion import StableDiffusionHandler
from image_generation.api.models import TextToImageInput
from image_generation.api.utils import zip_images

dictConfig(LogConfig().dict())
logger = logging.getLogger("Image Generation API")
logger.setLevel(os.getenv("LOGGER_LEVEL", logging.ERROR))
logger.info("--- Image Generation API ---")

app = FastAPI()
model = StableDiffusionHandler("stabilityai/stable-diffusion-2-1-base")


# health check
@app.get("/")
async def root():
    logger.info("Health check")
    return {"status": "healthy"}


# text to image
@app.post("/text_to_image", response_model=None)
async def text_to_image(text_to_image_input: TextToImageInput):
    logger.info(f"Text to image request: {text_to_image_input}")
    images = model.txt_to_img(text_to_image_input)

    if text_to_image_input.upload_images:
        logger.warning("Uploading images to the Cloud is not available yet!")

    if text_to_image_input.return_images:
        logger.info("Zipping images")
        images_bytes = zip_images(images)
        response = StreamingResponse(
            images_bytes, media_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=images.zip"
        return response
