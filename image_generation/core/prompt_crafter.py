import copy
import random

import numpy as np

from image_generation.core.styles import (
    STYLES,
    adjectives,
    characters,
    contexts,
    creatures,
    nouns,
    objects,
    settings,
    themes,
)
from image_generation.custom_logging import set_logger

logger = set_logger("Prompt Crafter")


class PromptCrafter:
    def __init__(self, styles):
        self.styles = styles
        self.variables = {
            "characters": characters,
            "settings": settings,
            "objects": objects,
            "creatures": creatures,
            "contexts": contexts,
            "adjectives": adjectives,
            "nouns": nouns,
            "themes": themes,
        }

    def fill_placeholder(self, prompt, var, singular, plural):
        if singular in prompt:
            prompt = prompt.replace(singular, random.choice(self.variables[var]))
        if plural in prompt:
            prompt = prompt.replace(
                plural,
                ", ".join(random.sample(self.variables[var], random.randint(2, 4))),
            )
        return prompt

    def generate_prompts(self, style_key, num_images):
        logger.info(f"Generating prompts for style key: {style_key}")

        style_templates = self.styles[style_key]
        prompts = []

        # Calculate the base number of images per template and the remainder
        num_templates = len(style_templates)
        base_images_per_template = num_images // num_templates
        remainder = num_images % num_templates

        # Randomly assign the remainder among the templates
        extra_images = np.zeros(num_templates, dtype=int)
        extra_images[:remainder] = 1
        np.random.shuffle(extra_images)

        for i, style_template in enumerate(style_templates):
            num_images_this_template = base_images_per_template + extra_images[i]

            for _ in range(num_images_this_template):
                prompt = copy.deepcopy(style_template)
                filled_prompt = prompt["prompt"]["positive"]

                for var in self.variables.keys():
                    filled_prompt = self.fill_placeholder(
                        filled_prompt, var, f"{{{var[:-1]}}}", f"{{{var}}}"
                    )

                prompt["prompt"]["positive"] = filled_prompt
                prompts.append(prompt)

        logger.debug(f"Generated {len(prompts)} prompts")
        return prompts
