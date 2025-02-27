import copy
import datetime
import random
import re
from collections import Counter
from fractions import Fraction
from typing import Dict, List, Optional

import numpy as np

from image_generation.core.styles import (
    actions,
    adjectives,
    characters,
    contexts,
    creatures,
    objects,
    settings,
    themes,
)
from image_generation.custom_logging import set_logger

logger = set_logger("Prompt Crafter")


def lcm(denominators):
    return np.lcm.reduce(denominators)


class PromptCrafter:
    def __init__(self, styles: Dict[str, List[str]], variables: dict = None) -> None:
        """
        Constructor for the PromptCrafter class.

        Args:
            styles (Dict[str, List[str]]): A dictionary containing styles as keys and list of templates as values.
            variables (dict, optional): A dictionary containing variables as keys and lists of values as values. Defaults to None and will use the default variables.
        """
        logger.info("Initializing PromptCrafter...")
        self.styles = styles
        if variables is None:
            self.original_variables = {
                "characters": characters,
                "settings": settings,
                "objects": objects,
                "creatures": creatures,
                "contexts": contexts,
                "adjectives": adjectives,
                "themes": themes,
                "actions": actions,
            }
        else:
            self.original_variables = variables
        self.variables = {
            var: self.variable_random_scatter_sample(var)
            for var in self.original_variables.keys()
        }
        logger.debug(f"Loaded styles: {self.styles.keys()}")
        logger.debug(f"Loaded variables: {self.variables.keys()}")

    def set_seed(self, seed: Optional[int] = None) -> None:
        """
        Set the seed for the random number generator.

        Args:
            seed (Optional[int]): The seed to use for the random number generator.
        """
        if seed is None:
            current_time = datetime.datetime.now()
            seed = int(current_time.timestamp())
        random.seed(seed)
        logger.info(f"Set seed: {seed}")

    def variable_random_scatter_sample(self, var: str) -> List[str]:
        """
        Sample the variable randomly and scatterly using probabilities.

        Args:
            var (str): The variable to sample.

        Returns:
            List[str]: A list of sampled values.
        """
        # Sample the variable with the given probability
        probability_sampled = self.variable_probability_sampling(var)

        # Sample randomly and scatterly, avoiding consecutive repetitions
        sample_size = len(probability_sampled)
        shuffled_lst = probability_sampled[:]
        random.shuffle(shuffled_lst)

        scattered_sample = []
        for value in shuffled_lst:
            if not scattered_sample or value != scattered_sample[-1]:
                scattered_sample.append(value)
                if len(scattered_sample) == sample_size:
                    break

        return scattered_sample

    def variable_probability_sampling(self, var: str) -> List[str]:
        """
        If the variable value has a ':p' suffix, sample the variable with the given 'probability'.
        Valid values for 'probability' are 0.25, 0.5, 1, 2, 3, 4, 5, etc.
        Setting float values less than 1 will result in the rest of the values being present at least more than once.
        For simplicity, we will just copy-paste that variable value that many times.

        Args:
            var (str): The variable to sample.

        Returns:
            List[str]: A list of sampled values.
        """
        logger.debug(f"Performing variable probability sampling for: {var}")

        if var not in self.original_variables:
            logger.error(f"'{var}' is not a valid variable.")
            raise ValueError(f"'{var}' is not a valid variable.")

        # Parse probabilities and convert them to fractions
        probabilities = []
        for value in self.original_variables[var]:
            match = re.search(r":([\d\.]+)$", value)
            if match:
                prob = Fraction(match.group(1))
                probabilities.append(prob)
            else:
                probabilities.append(Fraction(1))

        # Calculate LCM of denominators
        lcm_denominator = lcm([prob.denominator for prob in probabilities])

        # Scale probabilities
        scaled_probs = [int(prob * lcm_denominator) for prob in probabilities]

        # Sampling
        new_values = []
        for idx, value in enumerate(self.original_variables[var]):
            scaled_prob = scaled_probs[idx]
            base_value = value.split(":")[0]
            new_values.extend([base_value] * scaled_prob)

        logger.debug(f"Performed variable probability sampling for: {var}")
        return new_values

    def refill_and_shuffle(self, var: str) -> None:
        """
        Refill and shuffle the variable pool when it's empty.

        Args:
            var (str): The variable to refill and shuffle.
        """
        if var not in self.original_variables:
            logger.error(f"'{var}' is not a valid variable.")
            raise ValueError(f"'{var}' is not a valid variable.")
        self.variables[var] = self.variable_random_scatter_sample(var)
        logger.debug(f"Refilled and shuffled variable pool for: {var}")

    def fill_placeholder(
        self, prompt: str, var: str, singular: str, plural: str
    ) -> str:
        """
        Fill a placeholder in a prompt string with a random value from a variable pool.

        Args:
            prompt (str): The prompt string containing variables enclosed in curly braces.
            var (str): The variable to fill.
            singular (str): The singular placeholder to replace.
            plural (str): The plural placeholder to replace.

        Returns:
            str: The filled prompt string.
        """
        logger.debug(f"Filling placeholders for variable: {var}")
        if singular in prompt:
            if len(self.variables[var]) == 0:
                self.refill_and_shuffle(var)
            choice = self.variables[var].pop()
            prompt = prompt.replace(singular, choice)
        if plural in prompt:
            choices = []
            sample_size = min(len(self.original_variables[var]), random.randint(2, 4))
            for _ in range(sample_size):
                if len(self.variables[var]) == 0:
                    self.refill_and_shuffle(var)
                choices.append(self.variables[var].pop())
            prompt = prompt.replace(plural, ", ".join(choices))
        logger.debug(f"Filled prompt: {prompt}")
        return prompt

    def calculate_unique_combinations(self, prompt: str) -> int:
        """
        Calculate the number of unique combinations based on a given prompt string.

        Args:
            prompt (str): The prompt string containing variables enclosed in curly braces.

        Returns:
            int: The number of unique combinations.
        """
        logger.info("Calculating unique combinations...")
        unique_combinations = 1
        for var in self.original_variables.keys():
            count = prompt.count("{" + var[:-1] + "}")
            unique_combinations *= len(self.original_variables[var]) ** count
        logger.info(f"Unique combinations: {unique_combinations}")
        return unique_combinations

    def evenly_random_sample(self, prompts: List[dict], num_images: int) -> List[dict]:
        """
        Generates a random sample of template prompts from a given list of template prompts given a number of images.

        Args:
            prompts (List[dict]): A list of template prompts.
            num_images (int): The number of images to generate.

        Returns:
            List[dict]: A list of template prompts.
        """
        logger.info("Performing evenly random sampling...")

        if len(prompts) == 0 or num_images == 0:
            logger.warning("Empty prompt list or zero images requested.")
            return []

        template_counter = Counter()  # To keep track of how often each template is used

        if num_images >= len(prompts):
            base_count = num_images // len(prompts)
            remainder = num_images % len(prompts)

            # First distribute the numbers evenly
            prompts_output = [
                style_template for style_template in prompts for _ in range(base_count)
            ]
            template_counter.update(
                prompt["prompt"]["positive"] for prompt in prompts_output
            )

            # Add the remainder, as evenly as possible
            random.shuffle(prompts)
            for i in range(remainder):
                prompts_output.append(prompts[i % len(prompts)])
            template_counter.update(
                prompts[i % len(prompts)]["prompt"]["positive"]
                for i in range(remainder)
            )
        else:
            prompts_output = prompts.copy()
            random.shuffle(prompts_output)
            prompts_output = prompts_output[:num_images]
            template_counter.update(
                prompt["prompt"]["positive"] for prompt in prompts_output
            )

        # Log the usage count of each template
        logger.info(f"Template usage counts: {template_counter}")

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
                    f"Warning: Not enough unique combinations for template '{positive_prompt}': {unique_combinations}. Duplicates will be allowed."
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
                    else:
                        logger.debug(
                            f"Duplicate prompt: {filled_prompt} for template: {positive_prompt}"
                        )
                unique_prompts[positive_prompt].append(filled_prompt)
                new_prompt["prompt"]["positive"] = copy.deepcopy(filled_prompt)
                return_prompts.append(new_prompt)
        return return_prompts


if __name__ == "__main__":
    from rich import print

    from image_generation.core.styles import STYLES

    prompt_crafter = PromptCrafter(STYLES)
    prompt_crafter.set_seed(42)

    # Generate prompts
    print(prompt_crafter.variables)
    style_key = "general"
    num_images = 120
    prompts = prompt_crafter.generate_prompts(style_key, num_images)
    # print([p["prompt"]["positive"] for p in prompts])
