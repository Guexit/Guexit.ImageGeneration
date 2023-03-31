from pydantic import BaseModel


class Prompt(BaseModel):
    positive: str
    negative: str = ""
    guidance_scale: float


class TextToImage(BaseModel):
    model_path: str = "prompthero/openjourney-v2"
    model_scheduler: str = None
    prompt: Prompt
    height: int
    width: int
    seed: int = -1
    num_inference_steps: int
    num_images: int

    class Config:
        schema_extra = {
            "example": {
                "model_path": "prompthero/openjourney-v2",
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


class TextToImageOutput(BaseModel):
    images_zip_file: str = None
    image_url_path: str = None
