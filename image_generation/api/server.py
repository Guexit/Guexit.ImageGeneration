import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from image_generation.api.models import TextToImage, TextToStyle
from image_generation.api.utils import construct_filename, zip_images
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.custom_logging import set_logger

logger = set_logger("Image Generation API")
logger.info("--- Image Generation API ---")

app = FastAPI()
_model = None
_model_init_path = os.environ.get("DEFAULT_MODEL_NAME", "prompthero/openjourney-v4")


def get_model(model_init_path: str = _model_init_path) -> StableDiffusionHandler:
    global _model
    if _model is None:
        _model = StableDiffusionHandler(model_init_path)
    return _model


# health check
@app.get("/healthcheck")
async def healthcheck():
    logger.info("Health check")
    return {"status": "healthy"}


# text to image
@app.post("/text_to_image", response_model=None)
async def text_to_image(text_to_image: TextToImage):
    try:
        logger.debug(f"Text to image request: {text_to_image}")
        model = get_model(text_to_image.model_path)
        logger.info("Generating images")
        images = model.txt_to_img(text_to_image)

        logger.info("Zipping images")
        filenames = [
            construct_filename(text_to_image.prompt.positive, text_to_image.seed)
            for _ in range(len(images))
        ]
        metadata = text_to_image.dict()
        images = [
            (filename, image, metadata) for filename, image in zip(filenames, images)
        ]
        images_bytes = zip_images(images)
        response = StreamingResponse(
            images_bytes, media_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=images.zip"
        return response
    except Exception as e:
        logger.error(f"Error during text_to_image: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail="An error occurred during text_to_image processing."
        )


@app.post("/text_to_style", response_model=None)
async def text_to_style(text_to_style: TextToStyle):
    try:
        logger.debug(f"Text to style request: {text_to_style}")
        all_images = []
        logger.info("Generating images")
        for index, text_to_image in enumerate(text_to_style.text_to_images):
            logger.debug(f"Processing prompt {index + 1}: {text_to_image}")
            model = get_model(text_to_image.model_path)
            images = model.txt_to_img(text_to_image)
            metadata = text_to_image.dict()
            filename = construct_filename(
                text_to_image.prompt.positive, text_to_image.seed
            )
            all_images.extend([(filename, image, metadata) for image in images])

        logger.info("Zipping images")
        images_bytes = zip_images(all_images)
        response = StreamingResponse(
            images_bytes, media_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=images.zip"
        return response
    except Exception as e:
        logger.error(f"Error during text_to_image_with_style: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An error occurred during text_to_image_with_style processing.",
        )
