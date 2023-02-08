from pydantic import BaseModel


class TextToImage(BaseModel):
    model_path: str = "stabilityai/stable-diffusion-2-1-base"
    prompt: str
    guidance_scale: float
    height: int
    width: int
    num_inference_steps: int
    num_images_per_prompt: int


class TextToImageInput(TextToImage):
    return_images: bool = True
    upload_images: bool = False


class TextToImageOutput(BaseModel):
    images: list = None
    images_url_paths: list = None
