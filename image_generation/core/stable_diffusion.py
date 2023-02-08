import torch
from diffusers import StableDiffusionPipeline
from image_generation.api.models import TextToImage
from logging.config import dictConfig
import logging
from image_generation.logging import LogConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("Stable Diffusion Handler")


class StableDiffusionHandler:
    def __init__(self, model_path: str, device: torch.device = None):
        if device is None:
            if torch.backends.mps.is_available():
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")
            else:
                device = torch.device("cpu")
        self.device = device
        self._init_model(model_path=model_path)

    def _init_model(self, model_path: str):
        logger.info(f"Loading model from {model_path}")
        self.model_path = model_path
        self.pipe = StableDiffusionPipeline.from_pretrained(model_path)
        self.pipe.to(self.device)
        # Recommended if computer has < 64 GB of RAM
        self.pipe.enable_attention_slicing()
        # Warm up the model
        self.pipe("", num_inference_steps=1)

    def txt_to_img(self, input_data: TextToImage):
        if input_data.model_path != self.model_path:
            self._init_model(model_path=input_data.model_path)
        prompt = input_data.prompt
        guidance_scale = input_data.guidance_scale
        height = input_data.height
        width = input_data.width
        num_inference_steps = input_data.num_inference_steps
        num_images_per_prompt = input_data.num_images_per_prompt
        if self.device.type == "mps":
            logger.info(f"Running inference on MPS device")
            images = []
            for _ in range(num_images_per_prompt):
                images.append(
                    self.pipe(
                        prompt=prompt,
                        guidance_scale=guidance_scale,
                        height=height,
                        width=width,
                        num_inference_steps=num_inference_steps,
                        num_images_per_prompt=1,
                    ).images[0]
                )
        else:
            logger.info(f"Running inference")
            images = self.pipe(
                prompt=prompt,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=num_images_per_prompt,
            ).images
        return images


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--prompt", type=str, default="portrait of an alien astronaut")
    parser.add_argument("--guidance_scale", type=float, default=7.5)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    args = parser.parse_args()

    model = StableDiffusionHandler(args.model_path)
    image = model.txt_to_img(
        {
            "prompt": args.prompt,
            "guidance_scale": args.guidance_scale,
            "height": args.height,
            "width": args.width,
            "num_inference_steps": args.num_inference_steps,
        }
    )
    # Save image
    image.save("output.png")
