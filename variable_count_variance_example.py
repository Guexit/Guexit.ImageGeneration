import copy
import random
import re
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np

from image_generation.core.prompt_crafter import PromptCrafter
from image_generation.core.styles import (
    STYLES,
    actions,
    characters,
    contexts,
    creatures,
    famous_characters,
    objects,
    settings,
    themes,
)

# Instantiate the PromptCrafter class using the STYLES dictionary
prompt_crafter = PromptCrafter(STYLES)

# Generate prompts using the "general" style key
style_key = "general"
num_images = 100000  # Adjust the number as needed for your analysis
generated_prompts = prompt_crafter.generate_prompts(style_key, num_images)


# Function to extract and count the occurrences of variables
def extract_and_count_variables(prompts, variable_dict, variables_to_evaluate):
    # Initialize a dictionary to hold counters for each variable
    counters = {var_name: Counter() for var_name in variables_to_evaluate}
    # Create a combined list of all values across variables for overlap checking
    all_values = sorted(
        {value for values in variable_dict.values() for value in values},
        key=len,
        reverse=True,
    )

    for var_name, values in variables_to_evaluate.items():
        # Sort the values for the current variable by length
        sorted_values = sorted(values, key=len, reverse=True)
        for prompt in prompts:
            positive_prompt = prompt["prompt"]["positive"]
            # Count occurrences of each value in the current variable
            for value in sorted_values:
                if value in positive_prompt:
                    counters[var_name][value] += 1

        # Adjust counts for overlaps within the same variable
        for longer_value in sorted_values:
            for shorter_value in sorted_values:
                if shorter_value in longer_value and shorter_value != longer_value:
                    counters[var_name][shorter_value] -= counters[var_name][
                        longer_value
                    ]

        # Adjust counts based on overlaps from all other values
        for other_value in all_values:
            if other_value in sorted_values:
                continue  # Skip if this is a value within the current variable
            for value in sorted_values:
                if value in other_value:
                    counters[var_name][value] -= counters[var_name][other_value]

        # Ensure no negative counts in the current variable's counter
        for value in counters[var_name]:
            if counters[var_name][value] < 0:
                counters[var_name][value] = 0

    return counters


# Define a dictionary with all variable lists
variable_dict = {
    "themes": themes,
    "famous_characters": famous_characters,
    "characters": characters,
    "settings": settings,
    "contexts": contexts,
    "creatures": creatures,
    "objects": objects,
    "actions": actions,
}
variables_to_evaluate = {
    "characters": characters,
}

# Use the function to count occurrences for each variable
counters = extract_and_count_variables(
    generated_prompts, variable_dict, variables_to_evaluate
)


def test_small_variance_in_variable_counts(variable_counts, percentage_threshold=10):
    """
    Test if the variance in the counts of variable occurrences is small, based on a percentage threshold.

    Args:
    - variable_counts: A Counter object with the counts of each variable occurrence.
    - percentage_threshold: The maximum allowed percentage deviation from the mean count for the test to pass.

    Returns:
    - A boolean indicating whether the test passed and the maximum deviation percentage.
    """

    counts = np.array(list(variable_counts.values()))
    mean_count = np.mean(counts)
    # Calculate the percentage deviation from the mean for each count
    percentage_deviations = np.abs((counts - mean_count) / mean_count * 100)
    max_deviation = np.max(percentage_deviations)

    # Check if the maximum deviation is within the percentage threshold
    test_passed = max_deviation < percentage_threshold

    return test_passed, max_deviation


# Apply the test with a percentage threshold
percentage_threshold = 10  # Allowing up to 10% deviation from the mean count

# Now you can test each variable individually
for var_name, counter in counters.items():
    test_passed, max_dev_percentage = test_small_variance_in_variable_counts(
        counter, percentage_threshold
    )
    print(
        f"Variable: {var_name}, Test passed: {test_passed}, Max deviation percentage: {max_dev_percentage}"
    )
    plt.figure(figsize=(12, 6))
    plt.bar(counter.keys(), counter.values())
    plt.title(f"Distribution of {var_name} in Generated Prompts")
    plt.xticks(rotation=90)
    plt.ylabel("Frequency")
    plt.xlabel(f"{var_name}")
    plt.tight_layout()
    plt.show()

# test_passed, max_dev_percentage = test_small_variance_in_variable_counts(
#     variable_counts, percentage_threshold
# )
# print(f"Test passed: {test_passed}")
# print(f"Maximum deviation percentage: {max_dev_percentage}")
