import copy
import random
from typing import Dict, List

from image_generation.core.styles import (
    actions,
    adjectives,
    characters,
    contexts,
    creatures,
    famous_characters,
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
        logger.info("Initializing PromptCrafter...")
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
            "famous_characters": famous_characters,
        }
        logger.debug(f"Loaded styles: {self.styles.keys()}")
        logger.debug(f"Loaded variables: {self.variables.keys()}")

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
        logger.debug(f"Filling placeholders for variable: {var}")
        if singular in prompt:
            prompt = prompt.replace(singular, random.choice(self.variables[var]))
        if plural in prompt:
            sample_size = min(len(self.variables[var]), random.randint(2, 4))
            prompt = prompt.replace(
                plural,
                ", ".join(random.sample(self.variables[var], sample_size)),
            )
        logger.debug(f"Filled prompt: {prompt}")
        return prompt

    def calculate_unique_combinations(self, prompt: str) -> int:
        """
        Calculate the number of unique combinations based on a given prompt string.

        Parameters:
            prompt (str): The prompt string containing variables enclosed in curly braces.

        Returns:
            int: The number of unique combinations.
        """
        logger.info("Calculating unique combinations...")
        unique_combinations = 1
        for var in self.variables.keys():
            count = prompt.count("{" + var[:-1] + "}")
            unique_combinations *= len(self.variables[var]) ** count
        logger.info(f"Unique combinations: {unique_combinations}")
        return unique_combinations

    def evenly_random_sample(self, prompts: List[str], num_images: int) -> List[str]:
        """
        Generates a random sample of prompts from a given list of prompts.

        Args:
            prompts (List[str]): A list of strings representing the prompts.
            num_images (int): The number of images to be randomly sampled.

        Returns:
            List[str]: A list of strings representing the randomly sampled prompts.
        """
        logger.info("Performing evenly random sampling...")
        if len(prompts) == 0 or num_images == 0:
            logger.warning("Empty prompt list or zero images requested.")
            return []

        if num_images >= len(prompts):
            base_count = num_images // len(prompts)
            remainder = num_images % len(prompts)

            # First distribute the numbers evenly
            prompts_output = [
                style_template for style_template in prompts for _ in range(base_count)
            ]

            # Add the remainder, as evenly as possible
            random.shuffle(prompts)
            for i in range(remainder):
                prompts_output.append(prompts[i % len(prompts)])
        else:
            prompts_output = prompts.copy()
            random.shuffle(prompts_output)
            prompts_output = prompts_output[:num_images]

        return prompts_output

    def generate_prompts(self, style_key: str, num_images: int) -> List[dict]:
        """
        Generate a list of prompts based on a specific style.

        Args:
            style_key (str): The style key.
            num_images (int): The number of images for each prompt.

        Returns:
            List[str]: A list of generated prompts.
        """
        logger.info(f"Generating prompts for style key: {style_key}")
        if style_key not in self.styles:
            logger.error(f"'{style_key}' is not a valid style key.")
            raise ValueError(f"'{style_key}' is not a valid style key.")

        style_templates = self.styles[style_key]

        prompts = self.evenly_random_sample(style_templates, num_images)

        # Group prompts
        grouped_prompts = {}
        unique_prompts = {}
        for p in prompts:
            positive_prompt = p["prompt"]["positive"]
            if positive_prompt in grouped_prompts:
                grouped_prompts[positive_prompt].append(p)
            else:
                grouped_prompts[positive_prompt] = [p]
                unique_prompts[positive_prompt] = []

        # Compute unique prompts
        return_prompts = []
        for positive_prompt, prompts in grouped_prompts.items():
            unique_combinations = self.calculate_unique_combinations(positive_prompt)
            num_images_prompt = len(prompts)
            if unique_combinations < num_images_prompt:
                logger.warning(
                    f"Warning: Not enough unique combinations for template '{positive_prompt}'. Duplicates will be allowed."
                )
            for prompt in prompts:
                new_prompt = copy.deepcopy(prompt)
                iterations = 0
                filled_prompt = copy.deepcopy(new_prompt["prompt"]["positive"])
                while iterations < unique_combinations:
                    filled_prompt = copy.deepcopy(new_prompt["prompt"]["positive"])
                    for var in self.variables.keys():
                        filled_prompt = self.fill_placeholder(
                            filled_prompt, var, f"{{{var[:-1]}}}", f"{{{var}}}"
                        )
                    iterations += 1
                    if (
                        filled_prompt not in unique_prompts[positive_prompt]
                        or len(unique_prompts[positive_prompt]) == unique_combinations
                    ):
                        break
                unique_prompts[positive_prompt].append(filled_prompt)
                new_prompt["prompt"]["positive"] = copy.deepcopy(filled_prompt)
                return_prompts.append(new_prompt)

        return return_prompts


if __name__ == "__main__":
    from rich import print

    from image_generation.core.styles import STYLES

    # Initialize the PromptCrafter
    prompt_crafter = PromptCrafter(STYLES)

    # Specify the number of images and the style
    num_images = 28
    style_key = "general"

    # Generate the prompts
    prompts = prompt_crafter.generate_prompts(style_key, num_images)

    # Print the generated prompts
    for i, prompt in enumerate(prompts, start=1):
        print(f"Prompt {i}: {prompt['prompt']['positive']}")
