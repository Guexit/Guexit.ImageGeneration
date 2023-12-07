import random
import string
import unittest
from unittest.mock import patch

import numpy as np

from image_generation.core.prompt_crafter import PromptCrafter


class TestPromptCrafter(unittest.TestCase):
    def setUp(self):
        self.sample_styles = {
            "style1": [{"prompt": {"positive": "A {character} in a {setting}."}}],
            "style2": [{"prompt": {"positive": "A {creature} with a {object}."}}],
            "test_style": [
                {"prompt": {"positive": "{adjective} {object} {noun} in {setting}."}},
                {
                    "prompt": {
                        "positive": "{theme} {context} {creature} {action} {object} in {setting}."
                    }
                },
                {
                    "prompt": {
                        "positive": "{theme} {character} {action} {object} in {setting}."
                    }
                },
            ],
        }
        random.seed(12345)

        self.sample_variables = {
            "characters": ["character1", "character2", "character3"],
            "settings": ["setting1", "setting2", "setting3"],
            "objects": ["object1", "object2", "object3"],
            "creatures": ["creature1", "creature2", "creature3"],
            "contexts": ["context1", "context2", "context3"],
            "adjectives": [
                "".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(4)
            ],
            "nouns": [
                "".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(4)
            ],
            "themes": [
                "".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(4)
            ],
            "actions": [
                "".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(4)
            ],
        }

        self.prompt_crafter = PromptCrafter(self.sample_styles, self.sample_variables)

    def test_fill_placeholder(self):
        prompt = "A {character} in a {setting}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        self.assertNotIn("{character}", filled_prompt)
        self.assertIn(filled_prompt.split(" ")[1], self.sample_variables["characters"])

    def test_generate_prompts(self):
        with patch("random.sample", return_value=["character1", "setting1"]):
            prompts = self.prompt_crafter.generate_prompts("style1", 1)
        self.assertEqual(len(prompts), 1)
        self.assertNotIn("{character}", prompts[0]["prompt"]["positive"])
        self.assertNotIn("{setting}", prompts[0]["prompt"]["positive"])

    def test_generate_prompts_invalid_style(self):
        with self.assertRaises(ValueError):
            self.prompt_crafter.generate_prompts("invalid_style", 1)

    def test_generate_prompts_unique(self):
        num_images = 6
        prompts = self.prompt_crafter.generate_prompts("style1", num_images)
        self.assertEqual(len(prompts), num_images)

        # Check that all prompts are unique
        positive_prompts = [prompt["prompt"]["positive"] for prompt in prompts]
        self.assertEqual(len(positive_prompts), len(set(positive_prompts)))

    def test_duplicate_prompts(self):
        num_images = 3
        prompts = self.prompt_crafter.generate_prompts("style1", num_images)
        positive_prompts = [prompt["prompt"]["positive"] for prompt in prompts]
        self.assertEqual(len(positive_prompts), len(set(positive_prompts)))

    def test_plural_forms(self):
        prompt = "Some {characters} and {settings}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        self.assertNotIn("{characters}", filled_prompt)

    def test_multiple_same_placeholders(self):
        prompt = "A {character} and another {character}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        self.assertNotIn("{character}", filled_prompt)

    def test_multiple_different_placeholders(self):
        prompt = "A {character} in a {setting}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        filled_prompt = self.prompt_crafter.fill_placeholder(
            filled_prompt, "settings", "{setting}", "{settings}"
        )
        self.assertNotIn("{character}", filled_prompt)
        self.assertNotIn("{setting}", filled_prompt)

    def test_exceed_unique_combinations(self):
        num_images = 1000  # an arbitrary large number
        prompts = self.prompt_crafter.generate_prompts("style1", num_images)
        self.assertEqual(len(prompts), num_images)

    def test_fill_placeholder_singular(self):
        prompt = "A {character} in a {setting}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        self.assertNotIn("{character}", filled_prompt)

    def test_fill_placeholder_plural(self):
        prompt = "Some {characters} in {settings}."
        filled_prompt = self.prompt_crafter.fill_placeholder(
            prompt, "characters", "{character}", "{characters}"
        )
        self.assertNotIn("{characters}", filled_prompt)

    def test_calculate_unique_combinations(self):
        prompt = "A {character} in a {setting}."
        combinations = self.prompt_crafter.calculate_unique_combinations(prompt)
        self.assertEqual(combinations, 9)  # 3 characters * 3 settings

    def test_generate_prompts_valid_style(self):
        prompts = self.prompt_crafter.generate_prompts("style1", 2)
        self.assertEqual(len(prompts), 2)

    def test_generate_prompts_not_enough_combinations(self):
        with self.assertLogs(level="WARNING"):
            self.prompt_crafter.generate_prompts("style1", 1000)

    def test_minimum_non_duplicate_prompts_after_several_calls(self):
        num_calls = 1
        num_prompts_per_call = 30
        num_prompts = num_calls * num_prompts_per_call
        prompts = []
        prompt_crafter = PromptCrafter(self.sample_styles, self.sample_variables)
        for i in range(num_calls):
            prompt_crafter.set_seed(i)
            prompt = prompt_crafter.generate_prompts("test_style", num_prompts_per_call)
            prompts.append(prompt[0]["prompt"]["positive"])
        num_duplicates = len(prompts) - len(set(prompts))
        assert (
            num_duplicates < num_prompts * 0.01
        ), f"Number of duplicates: {num_duplicates}"

    def test_variable_value_distribution(self):
        num_images = 1000
        prompt_crafter = PromptCrafter(self.sample_styles, self.sample_variables)
        prompt_crafter.set_seed(12345)
        prompts = prompt_crafter.generate_prompts("test_style", num_images)
        percentage_threshold = 17

        def count_occurrences(prompts, variable_value):
            return sum(
                1
                for prompt in prompts
                if variable_value in prompt["prompt"]["positive"]
            )

        for variable_name, variable_values in self.sample_variables.items():
            occurrences = []
            for variable_value in variable_values:
                occurrences.append(count_occurrences(prompts, variable_value))
            counts = np.array(occurrences)
            mean_count = np.mean(counts)
            percentage_deviations = np.abs((counts - mean_count) / mean_count * 100)
            max_deviation = np.max(percentage_deviations)
            test_passed = max_deviation < percentage_threshold
            self.assertTrue(
                test_passed,
                f"Variable: {variable_name}, max deviation: {max_deviation}",
            )

    def test_evenly_random_sample(self):
        prompt_a = {"prompt": {"positive": "a"}}
        prompt_b = {"prompt": {"positive": "b"}}
        prompt_c = {"prompt": {"positive": "c"}}
        prompt_d = {"prompt": {"positive": "d"}}

        # Test case 1: empty prompts
        result = self.prompt_crafter.evenly_random_sample([], 5)
        self.assertEqual(result, [])

        # Test case 2: num_images is zero
        result = self.prompt_crafter.evenly_random_sample(
            [prompt_a, prompt_b, prompt_c], 0
        )
        self.assertEqual(result, [])

        # Test case 3: num_images is greater than len(prompts)
        result = self.prompt_crafter.evenly_random_sample(
            [prompt_a, prompt_b, prompt_c], 10
        )
        self.assertEqual(len(result), 10)
        self.assertTrue(all(elem in [prompt_a, prompt_b, prompt_c] for elem in result))

        # Test case 4: num_images is less than len(prompts)
        result = self.prompt_crafter.evenly_random_sample(
            [prompt_a, prompt_b, prompt_c, prompt_d], 2
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(
            all(elem in [prompt_a, prompt_b, prompt_c, prompt_d] for elem in result)
        )

        # Test case 5: num_images is exactly equal to len(prompts)
        result = self.prompt_crafter.evenly_random_sample(
            [prompt_a, prompt_b, prompt_c], 3
        )
        self.assertEqual(len(result), 3)
        self.assertTrue(all(elem in [prompt_a, prompt_b, prompt_c] for elem in result))

        # Additional: Testing the distribution (you might want to use random.seed for deterministic results)
        result = self.prompt_crafter.evenly_random_sample(
            [prompt_a, prompt_b, prompt_c], 10
        )
        count_a = result.count(prompt_a)
        count_b = result.count(prompt_b)
        count_c = result.count(prompt_c)

        self.assertTrue(count_a >= 3 and count_a <= 4)
        self.assertTrue(count_b >= 3 and count_b <= 4)
        self.assertTrue(count_c >= 3 and count_c <= 4)

    def test_set_seed_with_specific_value(self):
        specific_seed = 12345
        self.prompt_crafter.set_seed(specific_seed)
        # Save the state of the random generator after setting the seed
        state_after_seed = random.getstate()
        # Generate some random choices
        choices_after_seed = [random.choice(range(100)) for _ in range(10)]
        # Reset the seed and state
        self.prompt_crafter.set_seed(specific_seed)
        random.setstate(state_after_seed)
        # Generate choices again and they should be the same
        new_choices_after_seed = [random.choice(range(100)) for _ in range(10)]
        self.assertEqual(
            choices_after_seed,
            new_choices_after_seed,
            "The random choices should be the same after setting the same seed.",
        )

    def test_set_seed_without_value(self):
        self.prompt_crafter.set_seed()
        # Check if the seed is not None which would imply a seed has been set
        self.assertIsNotNone(
            random.getstate(), "Seed should be set even if no value is provided."
        )

    def test_variable_probability_sampling(self):
        sample_variables = {
            "var1": [
                "value1",
                "value2:1",
                "value3:2",
                "value4:4",
                "value5:0.5",  # Adding float probability
            ],
        }
        prompt_crafter = PromptCrafter(self.sample_styles, sample_variables)
        values = prompt_crafter.variable_probability_sampling("var1")

        # Updated expected values based on new input including float probabilities
        expected_values = [
            "value1",  # 2 times
            "value1",
            "value2",  # 2 times
            "value2",
            "value3",  # 4 times
            "value3",
            "value3",
            "value3",
            "value4",  # 8 times
            "value4",
            "value4",
            "value4",
            "value4",
            "value4",
            "value4",
            "value4",  # 8 times
            "value5",  # 1 time
        ]

        self.assertEqual(sorted(values), sorted(expected_values))

    def test_variable_probability_sampling_invalid_variable(self):
        with self.assertRaises(ValueError):
            self.prompt_crafter.variable_probability_sampling("invalid_var")

    def test_refill_and_shuffle(self):
        prompt_crafter = PromptCrafter(self.sample_styles, self.sample_variables)

        var_name = "characters"
        # Empty the variable pool
        while len(prompt_crafter.variables[var_name]) > 0:
            prompt_crafter.variables[var_name].pop()

        self.assertEqual(
            len(prompt_crafter.variables[var_name]),
            0,
            "Variable pool should be empty before refill.",
        )

        # Call refill_and_shuffle
        prompt_crafter.refill_and_shuffle(var_name)

        # Check if the variable pool is refilled
        self.assertNotEqual(
            len(prompt_crafter.variables[var_name]),
            0,
            "Variable pool should be refilled.",
        )
        self.assertEqual(
            len(prompt_crafter.variables[var_name]),
            len(prompt_crafter.original_variables[var_name]),
            "Variable pool should be refilled to its original size.",
        )

    def test_refill_and_shuffle_invalid_variable(self):
        with self.assertRaises(ValueError):
            self.prompt_crafter.refill_and_shuffle("invalid_var")

    def test_variable_random_scatter_sample(self):
        sample_variables = {
            "characters": ["character1", "character2:0.5", "character3:2"],
        }

        prompt_crafter = PromptCrafter(self.sample_styles, sample_variables)

        # Choose a variable for testing
        var_name = "characters"

        # Get the original list of values for the chosen variable
        original_values = prompt_crafter.original_variables[var_name]

        # Call the variable_random_scatter_sample function
        sampled_values = prompt_crafter.variable_random_scatter_sample(var_name)

        # Remove ':' and the probability from the original_values
        original_values = [value.split(":")[0] for value in original_values]

        # Check if the sampled values are in the original list
        self.assertTrue(
            all(value in original_values for value in sampled_values),
            "Sampled values should be from the original list.",
        )

        # Check if there are no consecutive repetitions
        for i in range(1, len(sampled_values)):
            self.assertNotEqual(
                sampled_values[i],
                sampled_values[i - 1],
                "Consecutive values should not be the same.",
            )

        # Check distribution
        expected_distribution = {
            "character1": 2,
            "character2": 1,
            "character3": 3,
        }
        for value in sampled_values:
            expected_distribution[value] -= 1
        self.assertTrue(
            all(value == 0 for value in expected_distribution.values()),
            "The distribution of the sampled values is not correct.",
        )


if __name__ == "__main__":
    unittest.main()
