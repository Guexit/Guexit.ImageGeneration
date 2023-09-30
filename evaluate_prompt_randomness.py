import math
import random
from collections import Counter
from typing import Dict

from rich import print
from scipy.stats import chisquare

from image_generation.core.prompt_crafter import PromptCrafter
from image_generation.core.styles import STYLES


class DebugPromptCrafter(PromptCrafter):
    def __init__(self, styles):
        super().__init__(styles)
        self.debug_counters = {var: Counter() for var in self.variables.keys()}

    def fill_placeholder(
        self, prompt: str, var: str, singular: str, plural: str
    ) -> str:
        if singular in prompt:
            chosen_value = random.choice(self.variables[var])
            self.debug_counters[var][chosen_value] += 1  # Debug counter
            prompt = prompt.replace(singular, chosen_value)
        if plural in prompt:
            sample_size = min(len(self.variables[var]), random.randint(2, 4))
            chosen_values = random.sample(self.variables[var], sample_size)
            for value in chosen_values:
                self.debug_counters[var][value] += 1  # Debug counter
            prompt = prompt.replace(plural, ", ".join(chosen_values))
        return prompt


def evaluate_prompt_randomness(
    prompt_crafter: PromptCrafter, num_prompts: int = 10000
) -> Dict[str, Counter]:
    """
    Evaluate the randomness of the generated prompts by counting the occurrences of each value for each variable.

    Parameters:
        prompt_crafter (PromptCrafter): The PromptCrafter object used to generate prompts.
        num_prompts (int): The number of prompts to generate for the evaluation. Default is 10,000.

    Returns:
        Dict[str, Counter]: A dictionary where keys are variable names and values are Counters containing the distribution of each value for that variable.
    """
    # Initialize counters for each variable
    counters = {var: Counter() for var in prompt_crafter.variables.keys()}

    # Define a style that uses all variables
    all_var_style = {
        "general": [
            {
                "model_path": "test_model",
                "model_scheduler": "test_scheduler",
                "prompt": {
                    "positive": "{character} {theme}",
                    "negative": "bad quality, text",
                    "guidance_scale": 7,
                },
                "height": 688,
                "width": 512,
                "num_inference_steps": 50,
                "num_images": 1,
                "seed": -1,
            },
            {
                "model_path": "test_model",
                "model_scheduler": "test_scheduler",
                "prompt": {
                    "positive": "{character} {action}",
                    "negative": "bad quality, text",
                    "guidance_scale": 7,
                },
                "height": 688,
                "width": 512,
                "num_inference_steps": 50,
                "num_images": 1,
                "seed": -1,
            },
        ]
    }

    # Use the defined style in the PromptCrafter object
    prompt_crafter.styles = all_var_style

    # Generate prompts
    generated_prompts = prompt_crafter.generate_prompts("general", num_prompts)

    # Count occurrences of each variable value in the generated prompts
    for prompt in generated_prompts:
        for var, values in prompt_crafter.variables.items():
            for value in values:
                if value in prompt["prompt"]["positive"]:
                    counters[var][value] += 1

    return counters


prompt_crafter = PromptCrafter(STYLES)


def test_prompt_randomness(
    prompt_crafter: PromptCrafter, num_prompts: int = 10000, alpha: float = 0.05
):
    """
    Test the randomness and distribution of the generated prompts.

    Parameters:
        prompt_crafter (PromptCrafter): The PromptCrafter object used to generate prompts.
        num_prompts (int): The number of prompts to generate for the evaluation. Default is 10,000.
        alpha (float): Significance level for the chi-squared test. Default is 0.05.
    """
    # Evaluate prompt randomness
    counters = evaluate_prompt_randomness(prompt_crafter, num_prompts)

    for var, counter in counters.items():
        n = len(counter)
        if n == 0:
            print(f"Warning: Variable {var} has no values in the generated prompts.")
            continue

        # Calculate mean and standard deviation
        total = sum(counter.values())
        mean = total / n
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in counter.values()) / n)

        # Calculate mean deviation
        mean_dev = sum(abs(x - mean) for x in counter.values()) / n

        # Perform chi-squared test
        _, p_value = chisquare(list(counter.values()))
        print(counter.values())
        # Assertions
        assert (
            std_dev < mean * 0.2
        ), f"Failed: Standard deviation too high for '{var}'. Current value is {std_dev} and the mean * 0.2 is {mean * 0.2}"
        assert (
            mean_dev < mean * 0.2
        ), f"Failed: Mean deviation too high for '{var}'. Current value is {mean_dev} and the mean * 0.2 is {mean * 0.2}"
        assert (
            p_value > alpha
        ), f"Failed: Chi-squared test for '{var}' (p-value: {p_value}). Current value is {p_value} and the significance level is {alpha}"

        print(f"Passed all checks for '{var}'.")


# Demonstration of the test function
# Using a smaller number of prompts for demonstration
test_prompt_randomness(prompt_crafter, num_prompts=1000)
# Initialize the DebugPromptCrafter
# counters = {var: Counter() for var in prompt_crafter.variables.keys()}

# # Define a style that uses all variables
# all_var_style = {
#     "general": [
#         {
#             "model_path": "test_model",
#             "model_scheduler": "test_scheduler",
#             "prompt": {
#                 "positive": "{theme} {adjective} {setting} with {objects} {context} featuring {characters} and {creatures} doing {actions} about {nouns}",
#                 "negative": "bad quality, text",
#                 "guidance_scale": 7,
#             },
#             "height": 688,
#             "width": 512,
#             "num_inference_steps": 50,
#             "num_images": 1,
#             "seed": -1,
#         }
#     ]
# }

# # Use the defined style in the PromptCrafter object
# prompt_crafter.styles = all_var_style
# debug_prompt_crafter = DebugPromptCrafter(STYLES)

# # Generate a smaller number of prompts for demonstration
# generated_prompts = debug_prompt_crafter.generate_prompts("general", 10000)

# # Show the debug counters for the 'characters' variable
# print(debug_prompt_crafter.debug_counters["characters"])
