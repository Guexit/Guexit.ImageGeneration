import argparse
import os
import random

from PIL import Image, ImageDraw, ImageFont
from rich import print

from image_generation.api.models import TextToImage
from image_generation.core.prompt_crafter import PromptCrafter
from image_generation.core.stable_diffusion import StableDiffusionHandler
from image_generation.core.styles import STYLES


class ModelComparisonExperiment:
    """
    Class for running a model comparison experiment.

    Args:
        output_directory (str): Directory to save the comparison images. Defaults to "images/comparison_results".

    Attributes:
        prompt_crafter (PromptCrafter): Instance of PromptCrafter class.
        output_directory (str): Directory to save the comparison images.

    Methods:
        generate_prompts(style, num_comparisons): Generates prompts for the experiment.
        generate_image(prompt, model, model_path): Generates an image for a given prompt and model.
        create_comparison_image(image1, image2, prompt, model_name_1, model_name_2): Creates a comparison image for two given images and prompts.
        save_image(image, file_name): Saves an image to the output directory.
        run_experiment(model_path_1, model_path_2, style, num_comparisons): Runs the model comparison experiment.
    """

    def __init__(self, output_directory="images/comparison_results"):
        self.prompt_crafter = PromptCrafter(STYLES)
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    def generate_prompts(self, style, num_comparisons):
        """
        Generates prompts for the experiment.

        Args:
            style (str): Style of the prompts.
            num_comparisons (int): Number of comparisons to generate.

        Returns:
            list: List of prompts.
        """
        prompts = self.prompt_crafter.generate_prompts(style, num_comparisons)
        # Set a random seed using random instead of -1 for reproducibility
        prompts = [{**prompt, "seed": random.randint(0, 1000)} for prompt in prompts]
        return prompts

    def generate_image(self, prompt, model, model_path):
        """
        Generates an image for a given prompt and model.

        Args:
            prompt (dict): Prompt to generate the image for.
            model (StableDiffusionHandler): Model to use for generating the image.
            model_path (str): Path to the model.

        Returns:
            PIL.Image.Image: Generated image.
        """
        model_prompt = prompt.copy()
        model_prompt["model_path"] = model_path
        image = model.txt_to_img(TextToImage(**model_prompt))[0]
        return image

    def create_comparison_image(
        self, image1, image2, prompt, model_name_1, model_name_2
    ):
        """
        Creates a comparison image for two given images and prompts.

        Args:
            image1 (PIL.Image.Image): First image to compare.
            image2 (PIL.Image.Image): Second image to compare.
            prompt (dict): Prompt used to generate the images.
            model_name_1 (str): Name of the first model.
            model_name_2 (str): Name of the second model.

        Returns:
            PIL.Image.Image: Comparison image.
        """
        margin_top = 80
        combined_width = image1.width + image2.width
        max_height = (
            max(image1.height, image2.height) + margin_top
        )  # 50 pixels for the title

        comparison_image = Image.new("RGB", (combined_width, max_height), "white")
        comparison_image.paste(image1, (0, margin_top))
        comparison_image.paste(image2, (image1.width, margin_top))

        # Create an ImageDraw object
        draw = ImageDraw.Draw(comparison_image)

        # Load a font object
        font = ImageFont.load_default(size=18)  # Using a default font
        font_model = ImageFont.load_default(size=20)  # Using a default font

        # Calculate text size using getbbox()
        prompt_text = prompt["prompt"]["positive"] + " | seed=" + str(prompt["seed"])
        text_width, text_height = draw.textbbox((0, 0), prompt_text, font=font)[2:]

        # Add the prompt_text as a title, centered at the top of the comparison image
        draw.text(
            ((combined_width - text_width) / 2, 10),
            prompt_text,
            font=font,
            fill="black",
        )
        draw.text((15, margin_top - 30), model_name_1, font=font_model, fill="black")
        draw.text(
            (image1.width + 15, margin_top - 30),
            model_name_2,
            font=font_model,
            fill="black",
        )

        return comparison_image

    def save_image(self, image, file_name):
        """
        Saves an image to the output directory.

        Args:
            image (PIL.Image.Image): Image to save.
            file_name (str): Name of the file to save the image as.
        """
        image_path = os.path.join(self.output_directory, file_name)
        image.save(image_path)
        print(f"Saved image: {image_path}")

    def run_experiment(self, model_path_1, model_path_2, style, num_comparisons=1):
        """
        Runs the model comparison experiment.

        Args:
            model_path_1 (str): Path to the first model.
            model_path_2 (str): Path to the second model.
            style (str): Style of the prompts.
            num_comparisons (int): Number of comparisons to generate. Defaults to 1.
        """
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
                image1, image2, prompt, model_path_1, model_path_2
            )
            self.save_image(comparison_image, f"comparison_{i+1}.png")


# Test the class
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a model comparison experiment.")
    parser.add_argument("--model_1", required=True, help="Path to the first model.")
    parser.add_argument("--model_2", required=True, help="Path to the second model.")
    parser.add_argument(
        "--style", default="general", help="Style for generating prompts."
    )
    parser.add_argument(
        "--num_comparisons",
        type=int,
        default=1,
        help="Number of comparisons to perform.",
    )
    args = parser.parse_args()
    # Assuming STYLES is a dictionary containing prompt styles as defined previously
    model_comparison = ModelComparisonExperiment()
    model_comparison.run_experiment(
        model_path_1=args.model_1,
        model_path_2=args.model_2,
        style=args.style,
        num_comparisons=args.num_comparisons,
    )
