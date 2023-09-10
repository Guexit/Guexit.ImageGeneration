import unittest
from unittest.mock import patch

from image_generation.core.prompt_crafter import PromptCrafter


class TestPromptCrafter(unittest.TestCase):
    def setUp(self):
        self.sample_styles = {
            "style1": [{"prompt": {"positive": "A {character} in a {setting}."}}],
            "style2": [{"prompt": {"positive": "A {creature} with a {object}."}}],
        }

        self.sample_variables = {
            "characters": ["character1", "character2", "character3"],
            "settings": ["setting1", "setting2", "setting3"],
            "objects": ["object1", "object2", "object3"],
            "creatures": ["creature1", "creature2", "creature3"],
            "contexts": ["context1", "context2", "context3"],
            "adjectives": ["adjective1", "adjective2", "adjective3"],
            "nouns": ["noun1", "noun2", "noun3"],
            "themes": ["theme1", "theme2", "theme3"],
        }

        self.prompt_crafter = PromptCrafter(self.sample_styles)
        self.prompt_crafter.variables = self.sample_variables

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

    def test_generate_prompts_invalid_style(self):
        with self.assertRaises(ValueError):
            self.prompt_crafter.generate_prompts("invalid_style", 2)

    def test_generate_prompts_unique(self):
        prompts = self.prompt_crafter.generate_prompts("style1", 4)
        positive_prompts = [prompt["prompt"]["positive"] for prompt in prompts]
        self.assertEqual(len(positive_prompts), len(set(positive_prompts)))

    def test_generate_prompts_not_enough_combinations(self):
        with self.assertLogs(level="WARNING"):
            self.prompt_crafter.generate_prompts("style1", 1000)

    def test_generate_prompts_with_plural_and_singular(self):
        self.sample_styles["style3"] = [
            {"prompt": {"positive": "{characters} and a {creature}."}}
        ]
        self.prompt_crafter.styles = self.sample_styles
        prompts = self.prompt_crafter.generate_prompts("style3", 4)
        positive_prompts = [prompt["prompt"]["positive"] for prompt in prompts]
        self.assertEqual(len(positive_prompts), len(set(positive_prompts)))

    def test_evenly_random_sample(self):
        # Test case 1: empty prompts
        result = self.prompt_crafter.evenly_random_sample([], 5)
        self.assertEqual(result, [])

        # Test case 2: num_images is zero
        result = self.prompt_crafter.evenly_random_sample(["a", "b", "c"], 0)
        self.assertEqual(result, [])

        # Test case 3: num_images is greater than len(prompts)
        result = self.prompt_crafter.evenly_random_sample(["a", "b", "c"], 10)
        self.assertEqual(len(result), 10)
        self.assertTrue(all(elem in ["a", "b", "c"] for elem in result))

        # Test case 4: num_images is less than len(prompts)
        result = self.prompt_crafter.evenly_random_sample(["a", "b", "c", "d"], 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(elem in ["a", "b", "c", "d"] for elem in result))

        # Test case 5: num_images is exactly equal to len(prompts)
        result = self.prompt_crafter.evenly_random_sample(["a", "b", "c"], 3)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(elem in ["a", "b", "c"] for elem in result))

        # Additional: Testing the distribution (you might want to use random.seed for deterministic results)
        result = self.prompt_crafter.evenly_random_sample(["a", "b", "c"], 10)
        count_a = result.count("a")
        count_b = result.count("b")
        count_c = result.count("c")

        self.assertTrue(count_a >= 3 and count_a <= 4)
        self.assertTrue(count_b >= 3 and count_b <= 4)
        self.assertTrue(count_c >= 3 and count_c <= 4)


if __name__ == "__main__":
    unittest.main()
