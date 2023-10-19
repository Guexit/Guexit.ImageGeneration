import contextlib
from typing import Optional

import torch
from diffusers import AutoPipelineForText2Image

from image_generation.api.models import TextToImage
from image_generation.core.schedulers import SchedulerEnum, SchedulerHandler
from image_generation.custom_logging import set_logger
from image_generation.utils import enough_gpu_memory

autocast = contextlib.nullcontext

logger = set_logger("Stable Diffusion Handler")


class StableDiffusionHandler:
    def __init__(self, model_path: str, device: str = None):
        """
        Initializes the StableDiffusionHandler

        :param model_path: Path to the model
        :param device: Device to use for computations (None will choose the best available)
        """
        if device is None:
            if torch.backends.mps.is_available():
                device = torch.device("mps")
                logger.info("Using MPS device")
            elif torch.cuda.is_available() and enough_gpu_memory():
                device = torch.device("cuda")
                logger.info("Using CUDA device")
            else:
                device = torch.device("cpu")
                logger.info("Using CPU device")
        else:
            device = torch.device(device)
        self.device = device
        self._init_model(model_path=model_path)
        self.scheduler_name = None

    def _init_model(self, model_path: str):
        """
        Initializes the model

        :param model_path: Path to the model
        :param scheduler_name: Name of the scheduler to use
        """
        logger.info(f"Loading model from {model_path}")
        self.model_path = model_path
        torch_dtype = (
            torch.float16 if self.device != torch.device("mps") else torch.float32
        )
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            model_path,
            torch_dtype=torch_dtype,
            # revision="fp16",
        )
        # Recommended if computer has < 16 GB of RAM
        if self.device == torch.device("cpu"):
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.enable_attention_slicing(1)
        elif self.device == torch.device("mps"):
            self.pipe.enable_attention_slicing(1)
        else:
            self.pipe.unet = torch.compile(
                self.pipe.unet, mode="reduce-overhead", fullgraph=True
            )
            self.pipe.enable_attention_slicing(1)
            self.pipe.to(self.device)
        # Warm up the model
        self.pipe("", num_inference_steps=1)

    def _set_scheduler(self, scheduler_name: SchedulerEnum):
        self.pipe.scheduler = SchedulerHandler.set_scheduler(
            scheduler_name=scheduler_name, current_scheduler=self.pipe.scheduler
        )
        self.scheduler_name = scheduler_name

    def _set_seed(self, seed: Optional[int]) -> Optional[torch.Generator]:
        """
        Sets the seed for the generator

        :param seed: Seed for the generator
        :return: The initialized generator, or None
        """
        if seed == -1 or seed is None:
            return None
        generator = torch.Generator(device=self.device)
        generator = generator.manual_seed(seed)
        return generator

    def txt_to_img(self, input_data: TextToImage) -> list:
        """
        Converts input text to images

        :param input_data: Input data for generating images
        :return: Generated images
        """
        if input_data.model_path != self.model_path:
            self._init_model(
                model_path=input_data.model_path,
            )
        if input_data.model_scheduler != self.scheduler_name:
            self._set_scheduler(input_data.model_scheduler)
        positive_prompt = input_data.prompt.positive
        negative_prompt = input_data.prompt.negative
        guidance_scale = input_data.prompt.guidance_scale
        height = input_data.height
        width = input_data.width
        num_inference_steps = input_data.num_inference_steps
        num_images = input_data.num_images
        generator = self._set_seed(input_data.seed)
        logger.info("Running inference")
        images = self.pipe(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            num_images_per_prompt=num_images,
            generator=generator,
        ).images
        return images


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="prompthero/openjourney-v4")
    parser.add_argument("--model_scheduler", type=str, default=None)
    parser.add_argument(
        "--positive_prompt",
        type=str,
        default="portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed",
    )
    parser.add_argument(
        "--negative_prompt",
        type=str,
        default="bad quality, malformed",
    )
    parser.add_argument("--guidance_scale", type=float, default=16.5)
    parser.add_argument("--height", type=int, default=688)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    parser.add_argument("--num_images", type=int, default=2)
    parser.add_argument("--seed", type=int, default=57857)
    parser.add_argument("--id", type=str, default=None)
    args = parser.parse_args()

    model = StableDiffusionHandler(args.model_path)
    images = model.txt_to_img(
        TextToImage(
            **{
                "model_path": args.model_path,
                "prompt": {
                    "positive": args.positive_prompt,
                    "negative": args.negative_prompt,
                    "guidance_scale": args.guidance_scale,
                },
                "height": args.height,
                "width": args.width,
                "num_inference_steps": args.num_inference_steps,
                "num_images": args.num_images,
                "seed": args.seed,
            }
        )
    )
    # Save images
    prefix_id = args.id + "_" if args.id is not None else ""
    for i, image in enumerate(images):
        image.save(f"output_{prefix_id}{i}.png")
