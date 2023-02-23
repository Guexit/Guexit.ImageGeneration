from diffusers import StableDiffusionPipeline
from typing import Callable, List, Optional, Union
import os

import torch


class StableDiffusionPipelineMock(StableDiffusionPipeline):
    def __init__(
        self,
        vae,
        text_encoder,
        tokenizer,
        unet,
        scheduler,
        safety_checker,
        feature_extractor,
        requires_safety_checker,
    ):
        pass

    @classmethod
    def from_pretrained(
        cls, pretrained_model_name_or_path: Optional[Union[str, os.PathLike]], **kwargs
    ):
        return StableDiffusionPipelineMock(
            vae="fake_vae",
            text_encoder="fake_text_encoder",
            tokenizer="fake_tokenizer",
            unet="fake_unet",
            scheduler="fake_scheduler",
            safety_checker="fake_safety_checker",
            feature_extractor="fake_feature_extractor",
            requires_safety_checker=False,
        )

    def to(self, torch_device: Optional[Union[str, torch.device]] = None):
        pass

    def enable_attention_slicing(self, slice_size: Optional[Union[str, int]] = "auto"):
        pass

    def __call__(
        self,
        prompt: Union[str, List[str]] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[Union[str, List[str]]] = None,
        num_images_per_prompt: Optional[int] = 1,
        eta: float = 0,
        generator: Optional[Union[torch.Generator, List[torch.Generator]]] = None,
        latents: Optional[torch.FloatTensor] = None,
        prompt_embeds: Optional[torch.FloatTensor] = None,
        negative_prompt_embeds: Optional[torch.FloatTensor] = None,
        output_type: Optional[str] = "pil",
        return_dict: bool = True,
        callback: Optional[Callable[[int, int, torch.FloatTensor], None]] = None,
        callback_steps: Optional[int] = 1,
    ):
        pass
