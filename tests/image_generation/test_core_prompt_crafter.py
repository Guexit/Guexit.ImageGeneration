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


if __name__ == "__main__":
    unittest.main()
