from typing import Optional

from pydantic import BaseModel, Field, validator


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
