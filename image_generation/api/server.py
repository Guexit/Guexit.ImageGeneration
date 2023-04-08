import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from image_generation.api.models import TextToImage
from image_generation.api.utils import zip_images
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.custom_logging import set_logger

logger = set_logger("Image Generation API")
logger.info("--- Image Generation API ---")

app = FastAPI()
model = StableDiffusionHandler("prompthero/openjourney-v2")


# health check
@app.get("/healthcheck")
async def healthcheck():
    logger.info("Health check")
    return {"status": "healthy"}


# text to image
@app.post("/text_to_image", response_model=None)
async def text_to_image(text_to_image: TextToImage):
    logger.info(f"Text to image request: {text_to_image}")
    images = model.txt_to_img(text_to_image)

    logger.info("Zipping images")
    images_bytes = zip_images(images)
    response = StreamingResponse(
        images_bytes, media_type="application/x-zip-compressed"
    )
    response.headers["Content-Disposition"] = "attachment; filename=images.zip"
    return response
