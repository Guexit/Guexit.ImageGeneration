import os
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image

from benchmarks.model_comparator import ModelComparisonExperiment
from image_generation.core.stable_diffusion import StableDiffusionHandler


class TestModelComparisonExperiment(unittest.TestCase):
    def setUp(self):
        self.experiment = ModelComparisonExperiment(output_directory="test_images")

    def tearDown(self):
        for file_name in os.listdir("test_images"):
            os.remove(os.path.join("test_images", file_name))

    def test_generate_prompts(self):
        prompts = self.experiment.generate_prompts("general", 2)
        self.assertIsInstance(prompts, list)
        self.assertEqual(len(prompts), 2)
        self.assertIsInstance(prompts[0], dict)
        self.assertIn("prompt", prompts[0])
        self.assertIn("positive", prompts[0]["prompt"])
        self.assertIn("seed", prompts[0])

    @patch("benchmarks.model_comparator.StableDiffusionHandler")
    def test_generate_image(self, MockStableDiffusionHandler):
        # Setup your mock object with your desired return value
        mock_handler_instance = MockStableDiffusionHandler.return_value
        mock_handler_instance.txt_to_img.return_value = [Image.new("RGB", (100, 100))]

        prompt = {
            "prompt": {"positive": "test prompt", "guidance_scale": 7},
            "height": 688,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": 1,
        }

        model = MockStableDiffusionHandler("model_path")
        image, time_taken = self.experiment.generate_image(prompt, model, "model_path")

        self.assertIsInstance(image, Image.Image)
        self.assertIsInstance(time_taken, float)

        # Check model params update
        model_params = {"height": "512"}

        # Expected prompt after update
        expected_prompt = {
            "prompt": {"positive": "test prompt", "guidance_scale": 7},
            "height": 512,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": 1,
        }

        # Call the function with model parameters
        self.experiment.generate_image(prompt, model, "model_path", model_params)

        # Check if the internal prompt within the function gets updated correctly
        actual_prompt = model.txt_to_img.call_args[0][0]
        for key, value in expected_prompt.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == "guidance_scale":
                        v = float(v)
                        av = float(actual_prompt.dict()[key][k])
                        self.assertEqual(v, av)
                    else:
                        self.assertEqual(str(v), str(actual_prompt.dict()[key][k]))
            else:
                self.assertEqual(str(value), str(actual_prompt.dict()[key]))

        ### TEST 2 ###
        # Test with model_params that have 'prompt' key
        model_params = {"height": "512", "prompt": {"positive": "test prompt 2"}}
        expected_prompt = {
            "prompt": {"positive": "test prompt 2", "guidance_scale": 7},
            "height": 512,
            "width": 512,
            "num_inference_steps": 35,
            "num_images": 1,
            "seed": 1,
        }

        self.experiment.generate_image(prompt, model, "model_path", model_params)

        actual_prompt = model.txt_to_img.call_args[0][0]
        for key, value in expected_prompt.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == "guidance_scale":
                        v = float(v)
                        av = float(actual_prompt.dict()[key][k])
                        self.assertEqual(v, av)
                    else:
                        self.assertEqual(str(v), str(actual_prompt.dict()[key][k]))
            else:
                self.assertEqual(str(value), str(actual_prompt.dict()[key]))

    def test_create_comparison_image(self):
        image1 = Image.new("RGB", (100, 100), "red")
        image2 = Image.new("RGB", (100, 100), "blue")
        prompt = {"prompt": {"positive": "test prompt"}, "seed": 1}
        model_name_1 = "model1"
        model_name_2 = "model2"
        time1 = 1.0
        time2 = 2.0
        params1 = {"height": 512}
        params2 = {"width": 512}
        comparison_image = self.experiment.create_comparison_image(
            image1,
            image2,
            time1,
            time2,
            prompt,
            model_name_1,
            model_name_2,
            params1,
            params2,
        )
        self.assertIsInstance(comparison_image, Image.Image)

    def test_save_image(self):
        image = Image.new("RGB", (100, 100), "red")
        file_name = "test_image.png"
        self.experiment.save_image(image, file_name)
        self.assertTrue(os.path.exists(os.path.join("test_images", file_name)))

    @patch("benchmarks.model_comparator.StableDiffusionHandler")
    def test_run_experiment(self, mock_handler):
        mock_handler.return_value.txt_to_img.return_value = [
            Image.new("RGB", (100, 100))
        ]
        model_path_1 = "model_path_1"
        model_path_2 = "model_path_2"
        style = "general"
        num_comparisons = 2
        self.experiment.run_experiment(
            model_path_1, model_path_2, style, num_comparisons
        )
        self.assertEqual(len(os.listdir("test_images")), num_comparisons)
