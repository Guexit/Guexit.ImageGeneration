import unittest

from image_generation.api.models import STYLES, Prompt, TextToImage, TextToStyle


class TestModels(unittest.TestCase):
    def test_text_to_image(self):
        prompt_data = {
            "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
            "negative": "bad quality, malformed",
            "guidance_scale": 16.5,
        }
        text_to_image_data = {
            "model_path": "prompthero/openjourney-v4",
            "model_scheduler": "euler_a",
            "prompt": prompt_data,
            "height": 688,
            "width": 512,
            "num_inference_steps": 50,
            "num_images": 2,
            "seed": 57857,
        }

        # Test if the model correctly validates and transforms the data
        text_to_image = TextToImage(**text_to_image_data)
        self.assertEqual(text_to_image.dict(), text_to_image_data)

        # Test if the model correctly validates the prompt
        prompt = Prompt(**prompt_data)
        self.assertEqual(prompt.dict(), prompt_data)

        # Test if the model throws an error for invalid data
        with self.assertRaises(ValueError):
            TextToImage(**{**text_to_image_data, "seed": -2})

    def test_text_to_style(self):
        # Assume we have a style called 'test_style' in STYLES
        STYLES["test_style"] = [
            {
                "model_path": "prompthero/openjourney-v4",
                "model_scheduler": "euler_a",
                "prompt": {
                    "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                    "negative": "bad quality, malformed",
                    "guidance_scale": 16.5,
                },
                "height": 688,
                "width": 512,
                "num_inference_steps": 50,
                "num_images": 1,
                "seed": 57857,
            }
        ]
        text_to_style_data = {
            "num_images": 2,
            "style": "test_style",
        }

        # Test if the model correctly validates and transforms the data
        text_to_style = TextToStyle(**text_to_style_data)
        self.assertEqual(text_to_style.style, text_to_style_data["style"])

        # Test if the model correctly updates the TextToImage objects
        self.assertEqual(len(text_to_style.text_to_images), len(STYLES["test_style"]))

        # Test if the model throws an error for invalid data (non-existent style)
        with self.assertRaises(ValueError):
            TextToStyle(**{**text_to_style_data, "style": "non_existent_style"})

        # Edge case: number of images is less than number of TextToImage objects
        STYLES["test_style"].append(
            STYLES["test_style"][0].copy()
        )  # Now we have 2 TextToImage objects
        text_to_style_data = {
            "num_images": 1,
            "style": "test_style",
        }
        text_to_style = TextToStyle(**text_to_style_data)
        self.assertEqual(len(text_to_style.text_to_images), 1)

        # Edge case: number of images is 0
        text_to_style_data = {
            "num_images": 0,
            "style": "test_style",
        }
        text_to_style = TextToStyle(**text_to_style_data)
        self.assertEqual(len(text_to_style.text_to_images), 0)

        del STYLES["test_style"]


if __name__ == "__main__":
    unittest.main()
