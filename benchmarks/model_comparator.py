import argparse
import json
import os
import random
import time

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

    def generate_image(
        self,
        prompt: dict,
        model: StableDiffusionHandler,
        model_path: str,
        model_params: dict = {},
    ):
        """
        Generates an image for a given prompt and model.

        Args:
            prompt (dict): Prompt to generate the image for.
            model (StableDiffusionHandler): Model to use for generating the image.
            model_path (str): Path to the model.
            model_params (dict): Additional parameters for image generation (like height, width, etc.).

        Returns:
            PIL.Image.Image: Generated image.
        """
        model_prompt = prompt.copy()
        model_prompt["model_path"] = model_path
        model_params_copy = model_params.copy()
        if "prompt" in model_params:
            print("HOLA HOLA")
            model_prompt["prompt"].update(model_params_copy["prompt"])
            del model_params_copy["prompt"]
        model_prompt.update(model_params_copy)

        start_time = time.time()
        image = model.txt_to_img(TextToImage(**model_prompt))[0]
        end_time = time.time()

        time_taken = end_time - start_time
        return image, time_taken

    def create_comparison_image(
        self,
        image1: Image.Image,
        image2: Image.Image,
        time1: float,
        time2: float,
        prompt: dict,
        model_name_1: str,
        model_name_2: str,
        params1: dict = {},
        params2: dict = {},
    ):
        """
        Creates a comparison image for two given images and prompts.

        Args:
            image1 (PIL.Image.Image): First image to compare.
            image2 (PIL.Image.Image): Second image to compare.
            time1 (float): Time taken to generate the first image.
            time2 (float): Time taken to generate the second image.
            prompt (dict): Prompt used to generate the images.
            model_name_1 (str): Name of the first model.
            model_name_2 (str): Name of the second model.
            params1 (dict): Parameters used to generate the first image.
            params2 (dict): Parameters used to generate the second image.

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

        # Add model parameter information
        param_text_1 = ", ".join([f"{k}: {v}" for k, v in params1.items()])
        param_text_2 = ", ".join([f"{k}: {v}" for k, v in params2.items()])

        # Add time information
        time_text_1 = f"Time: {time1:.2f}s"
        time_text_2 = f"Time: {time2:.2f}s"

        # Function to draw text with a background box
        def draw_text_with_background(
            draw, text_lines, position, font, text_color, bg_color
        ):
            text_width = max(
                draw.textbbox((0, 0), line, font=font)[2] for line in text_lines
            )
            text_height = (
                sum(draw.textbbox((0, 0), line, font=font)[3] for line in text_lines)
                + len(text_lines) * 5
            )
            bg_position = (
                position[0] - 5,
                position[1] - 5,
                position[0] + text_width + 10,
                position[1] + text_height + 5,
            )
            draw.rectangle(bg_position, fill=bg_color)
            current_height = position[1]
            for line in text_lines:
                draw.text(
                    (position[0], current_height), line, font=font, fill=text_color
                )
                current_height += draw.textbbox((0, 0), line, font=font)[3] + 5

        # White semi-transparent background
        bg_color = (255, 255, 255, 128)

        # Prepare parameter and time information for image1
        if params1 != {}:
            param_text_1 = ", ".join([f"{k}: {v}" for k, v in params1.items()])
            time_text_1 = f"Time: {time1:.2f}s"
            info_lines_1 = [param_text_1, time_text_1]
        else:
            info_lines_1 = [time_text_1]

        # Prepare parameter and time information for image2
        if params2 != {}:
            param_text_2 = ", ".join([f"{k}: {v}" for k, v in params2.items()])
            time_text_2 = f"Time: {time2:.2f}s"
            info_lines_2 = [param_text_2, time_text_2]
        else:
            info_lines_2 = [time_text_2]

        # Draw parameter and time information for image1
        draw_text_with_background(
            draw,
            info_lines_1,
            (5, image1.height + margin_top - 55),
            font,
            "black",
            bg_color,
        )

        # Draw parameter and time information for image2
        draw_text_with_background(
            draw,
            info_lines_2,
            (image1.width + 5, image2.height + margin_top - 55),
            font,
            "black",
            bg_color,
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

    def run_experiment(
        self,
        model_path_1,
        model_path_2,
        style,
        num_comparisons=1,
        model_1_params=None,
        model_2_params=None,
    ):
        """
        Runs the model comparison experiment.

        Args:
            model_path_1 (str): Path to the first model.
            model_path_2 (str): Path to the second model.
            style (str): Style of the prompts.
            num_comparisons (int): Number of comparisons to generate. Defaults to 1.
            model_1_params (dict): Parameters for the first model.
            model_2_params (dict): Parameters for the second model.
        """
        prompts = self.generate_prompts(style, num_comparisons)

        # Default to empty dictionary if no parameters provided
        if model_1_params is None:
            model_1_params = {}
        if model_2_params is None:
            model_2_params = {}

        # Generate all 'image1' instances for all prompts
        model = StableDiffusionHandler(model_path_1)
        images1, times1 = zip(
            *[
                self.generate_image(prompt, model, model_path_1, model_1_params)
                for prompt in prompts
            ]
        )
        del model

        # Generate all 'image2' instances for all prompts
        model = StableDiffusionHandler(model_path_2)
        images2, times2 = zip(
            *[
                self.generate_image(prompt, model, model_path_2, model_2_params)
                for prompt in prompts
            ]
        )

        # Now create all comparison images
        for i, (image1, image2, time1, time2, prompt) in enumerate(
            zip(images1, images2, times1, times2, prompts)
        ):
            comparison_image = self.create_comparison_image(
                image1,
                image2,
                time1,
                time2,
                prompt,
                model_path_1,
                model_path_2,
                model_1_params,
                model_2_params,
            )
            self.save_image(comparison_image, f"comparison_{i+1}.png")


# Test the class
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a model comparison experiment.")
    parser.add_argument("--model_1", required=True, help="Path to the first model.")
    parser.add_argument("--model_2", required=True, help="Path to the second model.")
    parser.add_argument(
        "--model_1_params",
        type=str,
        default="{}",
        help='JSON string of parameters for the first model. E.g., \'{"height": 688, "width": 512}\'',
    )
    parser.add_argument(
        "--model_2_params",
        type=str,
        default="{}",
        help='JSON string of parameters for the second model. E.g., \'{"height": 560, "width": 416}\'',
    )
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

    # Convert JSON strings to dictionaries
    model_1_params = json.loads(args.model_1_params)
    model_2_params = json.loads(args.model_2_params)

    model_comparison = ModelComparisonExperiment()
    model_comparison.run_experiment(
        model_path_1=args.model_1,
        model_path_2=args.model_2,
        model_1_params=model_1_params,
        model_2_params=model_2_params,
        style=args.style,
        num_comparisons=args.num_comparisons,
    )
