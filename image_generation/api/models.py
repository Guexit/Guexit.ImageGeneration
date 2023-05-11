from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator

from image_generation.core.styles import STYLES


class Prompt(BaseModel):
    positive: str
    negative: str = ""
    guidance_scale: float


class TextToImage(BaseModel):
    model_path: str = "prompthero/openjourney-v4"
    model_scheduler: Optional[str]
    prompt: Prompt
    height: int = Field(..., gt=0)
    width: int = Field(..., gt=0)
    seed: int = -1
    num_inference_steps: int = Field(..., gt=0)
    num_images: int = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "model_path": "prompthero/openjourney-v4",
                "model_scheduler": "euler_a",
                "prompt": {
                    "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                    "negative": "bad quality, malformed",
                    "guidance_scale": 16.5,
                },
                "height": 688,
                "width": 512,
                "num_inference_steps": 50,
                "num_images": 2,
                "seed": 57857,
            }
        }

    @validator("seed", pre=True)
    def validate_seed(cls, seed):
        if seed < -1:
            raise ValueError("Seed must be greater than or equal to -1")
        return seed


class TextToStyle(BaseModel):
    """
    Text to Style: List of TextToImage that can be used to generate a style.
    """

    model_path: Optional[str]
    model_scheduler: Optional[str]
    height: Optional[int]
    width: Optional[int]
    seed: Optional[int]
    num_inference_steps: Optional[int]
    num_images: Optional[int]
    style: str

    @root_validator
    def update_text_to_image_objects(cls, values):
        style_name = values.get("style")
        style_json = STYLES.get(style_name)

        if style_json is None:
            raise ValueError("Style not found")

        style = [TextToImage(**text_to_image_json) for text_to_image_json in style_json]
        updated_style = []

        total_text_to_image_objects = len(style)

        for index, text_to_image in enumerate(style):
            updated_text_to_image = text_to_image.copy()

            if values.get("model_path"):
                updated_text_to_image.model_path = values["model_path"]
            if values.get("model_scheduler"):
                updated_text_to_image.model_scheduler = values["model_scheduler"]
            if values.get("height") is not None:
                updated_text_to_image.height = values["height"]
            if values.get("width") is not None:
                updated_text_to_image.width = values["width"]
            if values.get("seed") is not None:
                updated_text_to_image.seed = values["seed"]
            if values.get("num_inference_steps") is not None:
                updated_text_to_image.num_inference_steps = values[
                    "num_inference_steps"
                ]
            if values.get("num_images") is not None:
                base_num_images = values["num_images"] // total_text_to_image_objects
                extra_images = (
                    1
                    if index < values["num_images"] % total_text_to_image_objects
                    else 0
                )
                updated_text_to_image.num_images = base_num_images + extra_images

            # Only add to updated_style if num_images > 0
            if updated_text_to_image.num_images > 0:
                updated_style.append(updated_text_to_image)

        values["text_to_images"] = updated_style
        return values
