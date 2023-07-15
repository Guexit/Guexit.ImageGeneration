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
            "characters": ["character1", "character2"],
            "settings": ["setting1", "setting2"],
            "objects": ["object1", "object2"],
            "creatures": ["creature1", "creature2"],
            "contexts": ["context1", "context2"],
            "adjectives": ["adjective1", "adjective2"],
            "nouns": ["noun1", "noun2"],
            "themes": ["theme1", "theme2"],
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


if __name__ == "__main__":
    unittest.main()
