from fastapi import FastAPI
from logging.config import dictConfig
import logging
from image_generation.logging import LogConfig
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.api.models import TextToImageInput, TextToImageOutput
from image_generation.api.utils import image_to_bytes

dictConfig(LogConfig().dict())
logger = logging.getLogger("Image Generation API")
logger.info("--- Image Generation API ---")

app = FastAPI()
model = StableDiffusionHandler("stabilityai/stable-diffusion-2-1-base")


# health check
@app.get("/")
async def root():
    logger.info("Health check")
    return {"status": "healthy"}


# text to image
@app.post("/text_to_image", response_model=TextToImageOutput)
async def text_to_image(text_to_image_input: TextToImageInput):
    logger.info(f"Text to image request: {text_to_image_input}")
    images = model.txt_to_img(text_to_image_input)
    if text_to_image_input.upload_images:
        logger.warning("Uploading images to the Cloud is not available yet!")
    if text_to_image_input.return_images:
        images_bytes = [image_to_bytes(image) for image in images]
        return TextToImageOutput(
            images=images_bytes,
        )
