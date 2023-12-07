import re
from collections import Counter

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def extract_and_count_variables(prompts, variable_dict, variables_to_evaluate):
    """
    Extracts and counts whole word occurrences of variables from a list of prompts.

    Args:
        prompts (list): A list of prompts, where each prompt is a dictionary with a "prompt" key
            containing a dictionary with "positive" and "negative" keys.
        variable_dict (dict): A dictionary where each key is a variable name and each value is a list
            of possible values for that variable.
        variables_to_evaluate (list): A list of variable names to evaluate.

    Returns:
        dict: A dictionary where each key is a variable name and each value is a Counter object
            containing the counts of each value for that variable.
    """
    # Remove ':' and what's after it from the variable values in variable_dict and variables_to_evaluate
    variable_dict = {
        var_name: [value.split(":")[0] for value in values]
        for var_name, values in variable_dict.items()
    }
    variables_to_evaluate = {
        var_name: [value.split(":")[0] for value in values]
        for var_name, values in variables_to_evaluate.items()
    }

    # Initialize a dictionary to hold counters for each variable
    counters = {var_name: Counter() for var_name in variable_dict}

    # Define a word boundary pattern that allows for hyphens
    standalone_pattern = r"(?:^|\s|[^-\w]){}(?:$|\s|[^-\w])"

    for var_name, values in variable_dict.items():
        # Compile a regular expression pattern for each value to match whole words, including hyphens
        patterns = {
            value: re.compile(standalone_pattern.format(re.escape(value)))
            for value in values
        }
        for prompt in prompts:
            positive_prompt = prompt["prompt"]["positive"]
            # Count occurrences of each whole word value in the current variable
            for value, pattern in patterns.items():
                matches = pattern.findall(positive_prompt)
                counters[var_name][value] += len(matches)

    # Only select variables_to_evaluate
    counters = {var_name: counters[var_name] for var_name in variables_to_evaluate}

    return counters


def plotly_distributions_with_separate_test_results(counters, percentage_threshold=10):
    """
    Creates a series of interactive subplots for the distribution of variables in two columns and a separate test results plot spanning two columns using Plotly, with an increased width.

    Args:
    - counters: A dictionary of Counter objects with counts for each variable occurrence.
    - percentage_threshold: The maximum allowed percentage deviation from the mean count for the test to pass.

    Returns:
    - A Plotly Figure object containing all the subplots and the test results plot.
    """
    num_variables = len(counters)
    cols = 2  # We want two columns of subplots
    rows = (num_variables + cols - 1) // cols  # Calculate rows needed for subplots
    test_results = {}

    # Create a subplot for each variable in two columns and an additional row for the test results
    fig = make_subplots(
        rows=rows + 1,
        cols=cols,  # Add an extra row for test results
        subplot_titles=[f"Distribution of {var}" for var in counters.keys()]
        + ["Test Results"],
        specs=[[{}, {}] for _ in range(rows)]
        + [
            [{"colspan": cols}, None]
        ],  # Span the last row across two columns for test results
    )

    # Plot each variable distribution in the subplots
    for i, (var_name, counter) in enumerate(counters.items(), start=1):
        row = (i - 1) // cols + 1
        col = (i - 1) % cols + 1

        counts = np.array(list(counter.values()))
        mean_count = np.mean(counts)
        percentage_deviations = np.abs((counts - mean_count) / mean_count * 100)
        max_deviation = np.max(percentage_deviations)
        test_passed = max_deviation < percentage_threshold

        # Save the test results
        test_results[var_name] = {
            "test_passed": test_passed,
            "max_deviation": max_deviation,
            "variable": var_name,
        }

        # Add a bar chart to the appropriate subplot
        fig.add_trace(
            go.Bar(x=list(counter.keys()), y=list(counter.values()), name=var_name),
            row=row,
            col=col,
        )

    # Plot the test results in the last row
    fig.add_trace(
        go.Bar(
            x=[result["variable"] for result in test_results.values()],
            y=[result["max_deviation"] for result in test_results.values()],
            name="Max Deviation",
            marker_color=[
                "green" if result["test_passed"] else "red"
                for result in test_results.values()
            ],
        ),
        row=rows + 1,
        col=1,
    )

    # Add a horizontal line indicating the threshold
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(test_results) - 0.5,
        y0=percentage_threshold,
        y1=percentage_threshold,
        line=dict(color="Blue", width=2, dash="dash"),
        row=rows + 1,
        col=1,
    )

    # Update the layout to make the figure wider
    fig.update_layout(
        height=300 * (rows + 1),  # You can adjust height if needed
        width=1400,  # Increased width
        title_text="Variable Distributions and Test Results",
        showlegend=False,
    )

    fig.show()

    return fig


if __name__ == "__main__":
    from image_generation.core.prompt_crafter import PromptCrafter
    from image_generation.core.styles import (
        STYLES,
        characters,
        contexts,
        creatures,
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

    # Define a dictionary with all variable lists
    variable_dict = {
        "themes": themes,
        "characters": characters,
        "settings": settings,
        "contexts": contexts,
        "creatures": creatures,
        "objects": objects,
    }
    variables_to_evaluate = {
        "themes": themes,
        "characters": characters,
        "settings": settings,
        "contexts": contexts,
        "creatures": creatures,
        "objects": objects,
    }

    # Use the function to count occurrences for each variable
    counters = extract_and_count_variables(
        generated_prompts, variable_dict, variables_to_evaluate
    )

    # Plot the distributions and test for variance
    plotly_distributions_with_separate_test_results(counters)

    # # Expanded synthetic examples of what the output of generated prompts could look like
    # synthetic_prompts = [
    #     {"prompt": {"positive": "A wizard in a dark forest", "negative": "No dragons"}},
    #     {
    #         "prompt": {
    #             "positive": "A knight fighting a dragon",
    #             "negative": "No modern setting",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "Elves dancing in the moonlight",
    #             "negative": "No sci-fi elements",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A cyborg in a post-apocalyptic world",
    #             "negative": "No fantasy creatures",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A pirate sailing the high seas",
    #             "negative": "No futuristic weapons",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A detective solving a mystery in a neon-lit city",
    #             "negative": "No supernatural elements",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A vampire lurking in an abandoned mansion",
    #             "negative": "No bright settings",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A scientist discovering a new element",
    #             "negative": "No historical figures",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A mermaid exploring an underwater city",
    #             "negative": "No land animals",
    #         }
    #     },
    #     {
    #         "prompt": {
    #             "positive": "A warrior riding a griffin into battle",
    #             "negative": "No peaceful scenes",
    #         }
    #     },
    #     # ... more examples
    # ]

    # # Expanded synthetic variable list, mimicking the output of the styles structure
    # synthetic_variable_dict = {
    #     "characters": [
    #         "wizard",
    #         "knight",
    #         "elf",
    #         "dragon",
    #         "cyborg",
    #         "pirate",
    #         "detective",
    #         "vampire",
    #         "scientist",
    #         "mermaid",
    #         "warrior",
    #         "griffin",
    #     ],
    #     "settings": [
    #         "dark forest",
    #         "castle",
    #         "moonlit glade",
    #         "post-apocalyptic world",
    #         "high seas",
    #         "neon-lit city",
    #         "abandoned mansion",
    #         "underwater city",
    #         "battlefield",
    #     ],
    #     "actions": [
    #         "fighting",
    #         "dancing",
    #         "sailing",
    #         "solving",
    #         "lurking",
    #         "discovering",
    #         "exploring",
    #         "riding",
    #     ],
    #     "objects": [
    #         "sword",
    #         "spellbook",
    #         "ship",
    #         "magnifying glass",
    #         "cloak",
    #         "laboratory equipment",
    #         "treasure chest",
    #         "armor",
    #     ],
    #     "creatures": [
    #         "dragons",
    #         "fantasy creatures",
    #         "supernatural elements",
    #         "land animals",
    #         "griffin",
    #     ],
    #     # ... more variables
    # }

    # # Define which variables you want to evaluate from the synthetic list
    # variables_to_evaluate = {
    #     "characters": synthetic_variable_dict["characters"],
    #     "settings": synthetic_variable_dict["settings"],
    #     "actions": synthetic_variable_dict["actions"],
    #     "objects": synthetic_variable_dict["objects"],
    #     "creatures": synthetic_variable_dict["creatures"],
    # }

    # # Use the function to count occurrences for each synthetic variable
    # counters = extract_and_count_variables(
    #     synthetic_prompts, synthetic_variable_dict, variables_to_evaluate
    # )

    # # Plot the distributions and test for variance
    # plot_combined_variable_distributions(counters)
