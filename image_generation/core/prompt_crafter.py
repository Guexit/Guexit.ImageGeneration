import copy
import random
from typing import Dict, List

import numpy as np

from image_generation.core.styles import (
    actions,
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
    def __init__(self, styles: Dict[str, List[str]]) -> None:
        """
        Constructor for the PromptCrafter class.

        Args:
            styles (Dict[str, List[str]]): A dictionary containing styles as keys and list of templates as values.
        """
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
            "actions": actions,
        }

    def fill_placeholder(
        self, prompt: str, var: str, singular: str, plural: str
    ) -> str:
        """
        Replace placeholders in the prompt with actual values.

        Args:
            prompt (str): The initial prompt with placeholders.
            var (str): The variable to be replaced in the prompt.
            singular (str): The singular form of the variable.
            plural (str): The plural form of the variable.

        Returns:
            str: The prompt with placeholders replaced with actual values.
        """
        if singular in prompt:
            prompt = prompt.replace(singular, random.choice(self.variables[var]))
        if plural in prompt:
            sample_size = min(len(self.variables[var]), random.randint(2, 4))
            prompt = prompt.replace(
                plural,
                ", ".join(random.sample(self.variables[var], sample_size)),
            )
        return prompt

    def calculate_unique_combinations(self, template: str) -> int:
        unique_combinations = 1
        for var in self.variables.keys():
            count = template.count("{" + var[:-1] + "}")
            unique_combinations *= len(self.variables[var]) ** count
        return unique_combinations

    def generate_prompts(self, style_key: str, num_images: int) -> List[str]:
        """
        Generate a list of prompts based on a specific style.

        Args:
            style_key (str): The style key.
            num_images (int): The number of images for each prompt.

        Returns:
            List[str]: A list of generated prompts.
        """
        if style_key not in self.styles:
            raise ValueError(f"'{style_key}' is not a valid style key.")

        logger.info(f"Generating prompts for style key: {style_key}")
        style_templates = self.styles[style_key]
        prompts = []
        seen_prompts = set()

        for style_template in style_templates:
            template = style_template["prompt"]["positive"]

            unique_combinations = self.calculate_unique_combinations(template)
            if unique_combinations < num_images:
                logger.warning(
                    f"Warning: Not enough unique combinations. Duplicates will be allowed."
                )

            max_iterations = max(10 * num_images, 1000)  # Limit to avoid infinite loop
            generated_count = 0

            for _ in range(max_iterations):
                if generated_count >= num_images:
                    break
                prompt = copy.deepcopy(style_template)
                filled_prompt = prompt["prompt"]["positive"]

                for var in self.variables.keys():
                    filled_prompt = self.fill_placeholder(
                        filled_prompt, var, f"{{{var[:-1]}}}", f"{{{var}}}"
                    )

                if (
                    filled_prompt not in seen_prompts
                    or unique_combinations < num_images
                ):
                    prompt["prompt"]["positive"] = filled_prompt
                    prompts.append(prompt)
                    seen_prompts.add(filled_prompt)
                    generated_count += 1
        return prompts


if __name__ == "__main__":
    from image_generation.core.styles import STYLES

    # Initialize the PromptCrafter
    prompt_crafter = PromptCrafter(STYLES)

    # Specify the number of images and the style
    num_images = 3
    style_key = "general"

    # Generate the prompts
    prompts = prompt_crafter.generate_prompts(style_key, num_images)

    # Print the generated prompts
    for i, prompt in enumerate(prompts, start=1):
        print(f"Prompt {i}: {prompt['prompt']['positive']}")
