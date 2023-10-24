from typing import Optional

import numpy as np
import torch
from diffusers import AutoPipelineForText2Image

from image_generation.api.models import TextToImage
from image_generation.core.schedulers import SchedulerEnum, SchedulerHandler
from image_generation.custom_logging import set_logger
from image_generation.utils import enough_gpu_memory

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
            use_safetensors=True,
        )
        # Recommended if computer has < 16 GB of RAM
        if self.device == torch.device("cpu"):
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.enable_attention_slicing(1)
        else:
            self.pipe.to(self.device)
            self.pipe.enable_attention_slicing(1)
            self.pipe.enable_vae_slicing()
        # Warm up the model
        logger.info("Warming up model")
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

    def _is_black_image(self, image):
        """
        Checks if an image is entirely black.
        """
        image_array = np.array(image)
        return np.all(image_array == 0)

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
        logger.info(f"Running inference on {num_images} images")
        images = []
        max_attempts = 10
        while len(images) < num_images and max_attempts > 0:
            # Generate the remaining images
            num_images_to_generate = num_images - len(images)
            logger.debug(f"Num images to generate: {num_images_to_generate}")
            candidate_images = self.pipe(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=num_images_to_generate,
                generator=generator,
            ).images

            max_attempts -= 1

            for img in candidate_images:
                if not self._is_black_image(img):
                    images.append(img)  # Keep this image if it is not black
                else:
                    logger.info(
                        f"Black image detected. Retrying with {max_attempts} remaining attempts"
                    )
                    logger.debug(
                        f"""Parameters:
                        prompt: {positive_prompt}
                        negative_prompt: {negative_prompt}
                        guidance_scale: {guidance_scale}
                        height: {height}
                        width: {width}
                        num_inference_steps: {num_inference_steps}
                        num_images_per_prompt: {num_images_to_generate}
                        seed: {input_data.seed}
                        """
                    )
                    # Set seed to -1 to generate vary the image generated to avoid black images
                    generator = self._set_seed(-1)

            logger.debug(
                f"Generated {len(images)} non-black images out of {num_images} so far."
            )

        return images
