import unittest
from unittest.mock import MagicMock, patch

from services.message_handlers import (
    MessageFactory,
    TextToImageMessage,
    TextToStyleMessage,
)


class TestMessageFactory(unittest.TestCase):
    def test_create_message_text_to_style(self):
        message_json = {"text_to_style": {"style": "general", "seed": 1}}
        message = MessageFactory.create_message(message_json)
        self.assertIsInstance(message, TextToStyleMessage)

    def test_create_message_text_to_image(self):
        message_json = {
            "text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}
        }
        message = MessageFactory.create_message(message_json)
        self.assertIsInstance(message, TextToImageMessage)

    def test_create_message_invalid(self):
        message_json = {
            "invalid_key": {"prompt": {"positive": "test prompt"}, "seed": 1}
        }
        with self.assertRaises(ValueError):
            MessageFactory.create_message(message_json)


class TestTextToStyleMessage(unittest.TestCase):
    @patch("services.message_handlers.call_image_generation_api")
    def test_process(self, mock_api_call):
        message_json = {"text_to_style": {"style": "general", "seed": 1}}
        message = TextToStyleMessage(message_json)
        response = message.process()
        mock_api_call.assert_called_once()
        self.assertIsInstance(response, MagicMock)

    def test_get_file_name(self):
        message_json = {"text_to_style": {"style": "general", "seed": 1}}
        message = TextToStyleMessage(message_json)
        file_name = message.get_file_name(0)
        self.assertIsInstance(file_name, str)
        self.assertIn("general", file_name)
        self.assertIn("_1_", file_name)

    def test_get_file_name_no_seed(self):
        message_json = {"text_to_style": {"style": "general"}}
        message = TextToStyleMessage(message_json)
        file_name = message.get_file_name(0)
        self.assertIsInstance(file_name, str)
        self.assertIn("general", file_name)
        self.assertIn("_-1_", file_name)


class TestTextToImageMessage(unittest.TestCase):
    @patch("services.message_handlers.call_image_generation_api")
    def test_process(self, mock_api_call):
        message_json = {
            "text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}
        }
        message = TextToImageMessage(message_json)
        response = message.process()
        mock_api_call.assert_called_once()
        self.assertIsInstance(response, MagicMock)

    def test_get_file_name(self):
        message_json = {
            "text_to_image": {"prompt": {"positive": "test prompt"}, "seed": 1}
        }
        message = TextToImageMessage(message_json)
        file_name = message.get_file_name(0)
        self.assertIsInstance(file_name, str)
        self.assertIn("test_prompt", file_name)
        self.assertIn("_1_", file_name)

    def test_get_file_name_no_seed(self):
        message_json = {"text_to_image": {"prompt": {"positive": "test prompt"}}}
        message = TextToImageMessage(message_json)
        file_name = message.get_file_name(0)
        self.assertIsInstance(file_name, str)
        self.assertIn("test_prompt", file_name)
        self.assertIn("_-1_", file_name)


if __name__ == "__main__":
    unittest.main()
