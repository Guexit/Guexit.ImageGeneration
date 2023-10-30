import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rich import print

from image_generation.api.models import TextToImage
from image_generation.core.prompt_crafter import PromptCrafter
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.core.styles import STYLES


class ModelComparisonExperiment:
    def __init__(self, output_directory="images/comparison_results"):
        self.prompt_crafter = PromptCrafter(STYLES)
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def generate_prompts(self, style, num_comparisons):
        return self.prompt_crafter.generate_prompts(style, num_comparisons)

    def generate_image(self, prompt, model, model_path):
        model_prompt = prompt.copy()
        model_prompt["model_path"] = model_path
        image = model.txt_to_img(TextToImage(**model_prompt))[0]
        return image

    def create_comparison_image(self, image1, image2, prompt):
        combined_width = image1.width + image2.width
        max_height = max(image1.height, image2.height) + 50  # 50 pixels for the title

        comparison_image = Image.new("RGB", (combined_width, max_height), "white")
        comparison_image.paste(image1, (0, 50))
        comparison_image.paste(image2, (image1.width, 50))

        # Create an ImageDraw object
        draw = ImageDraw.Draw(comparison_image)

        # Load a font object
        font = ImageFont.load_default()  # Using a default font

        # Calculate text size using getbbox()
        text_width, text_height = draw.textbbox((0, 0), prompt, font=font)[2:]

        # Add the prompt as a title, centered at the top of the comparison image
        draw.text(
            ((combined_width - text_width) / 2, 10), prompt, font=font, fill="black"
        )

        return comparison_image

    def save_image(self, image, file_name):
        image_path = os.path.join(self.output_directory, file_name)
        image.save(image_path)
        print(f"Saved image: {image_path}")

    def run_experiment(self, model_path_1, model_path_2, style, num_comparisons=1):
        prompts = self.generate_prompts(style, num_comparisons)

        # Generate all 'image1' instances for all prompts
        model = StableDiffusionHandler(model_path_1)
        images1 = [
            self.generate_image(prompt, model, model_path_1) for prompt in prompts
        ]

        # Generate all 'image2' instances for all prompts
        model = StableDiffusionHandler(model_path_2)
        images2 = [
            self.generate_image(prompt, model, model_path_2) for prompt in prompts
        ]

        # Now create all comparison images
        for i, (image1, image2, prompt) in enumerate(zip(images1, images2, prompts)):
            comparison_image = self.create_comparison_image(
                image1, image2, prompt["prompt"]["positive"]
            )
            self.save_image(comparison_image, f"comparison_{i+1}.png")


# Test the class
if __name__ == "__main__":
    # Assuming STYLES is a dictionary containing prompt styles as defined previously
    model_comparison = ModelComparisonExperiment()
    model_comparison.run_experiment(
        model_path_1="digiplay/Juggernaut_final",
        model_path_2="digiplay/Juggernaut_final",
        style="general",
        num_comparisons=1,
    )
