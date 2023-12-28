import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict

from image_generation.utils import call_image_generation_api
from services import config


class MessageTypeInterface(ABC):
    """
    Abstract base class for different types of messages.
    """

    def __init__(self, message_json: Dict[str, Any], key: str):
        """
        Initialize a MessageTypeInterface instance.

        Args:
            message_json (Dict[str, Any]): The JSON message to process.
            key (str): The key to use to extract the relevant part of the message.

        Raises:
            ValueError: If the key is not found in the JSON message.
        """
        try:
            self.message_json = message_json[key]
        except KeyError:
            raise ValueError(f"Key {key} not found in message_json")

    @abstractmethod
    def process(self) -> Any:
        """
        Process the message. This method should be overridden in subclasses.
        """
        pass

    def get_file_name(self, name: str) -> str:
        """
        Get the last part of the file name.

        Parameters:
            name (str): The full file name including the path.

        Returns:
            str: The last part of the file name without the extension.
        """
        return name.split("/")[-1]


class TextToStyleMessage(MessageTypeInterface):
    """
    Class to process "text to style" messages.
    """

    def __init__(self, message_json: Dict[str, Any]):
        """
        Initialize a TextToStyleMessage instance.

        Args:
            message_json (Dict[str, Any]): The JSON message to process.
        """
        super().__init__(message_json, "text_to_style")

    def process(self) -> Any:
        """
        Process the message by calling the image generation API.

        Returns:
            Any: The response from the image generation API.
        """
        return call_image_generation_api(
            config.IMAGE_GENERATION_API, "/text_to_style", self.message_json
        )

    def get_file_name(self, file_path: str) -> str:
        """
        Generate a file name based on the style in the message and a unique index.

        Args:
            idx (int): A unique index to append to the file name.

        Returns:
            str: The generated file name.
        """
        return super().get_file_name(file_path)


class TextToImageMessage(MessageTypeInterface):
    """
    Class to process "text to image" messages.
    """

    def __init__(self, message_json: Dict[str, Any]):
        """
        Initialize a TextToImageMessage instance.

        Args:
            message_json (Dict[str, Any]): The JSON message to process.
        """
        super().__init__(message_json, "text_to_image")

    def process(self) -> Any:
        """
        Process the message by calling the image generation API.

        Returns:
            Any: The response from the image generation API.
        """
        return call_image_generation_api(
            config.IMAGE_GENERATION_API, "/text_to_image", self.message_json
        )

    def get_file_name(self, file_path: str) -> str:
        """
        Generate a file name based on the style in the message and a unique index.

        Args:
            idx (int): A unique index to append to the file name.

        Returns:
            str: The generated file name.
        """
        return super().get_file_name(file_path)


class MessageFactory:
    """
    Factory class to create MessageTypeInterface instances.
    """

    message_classes = {
        "text_to_style": TextToStyleMessage,
        "text_to_image": TextToImageMessage,
    }

    @classmethod
    def create_message(cls, message_json: Dict[str, Any]) -> MessageTypeInterface:
        """
        Create and return an appropriate MessageTypeInterface instance based on the contents of message_json.
        Raise an Exception if an appropriate class can't be found.

        Args:
            message_json (Dict[str, Any]): A dictionary containing the JSON message.

        Returns:
            MessageTypeInterface: An instance of a class that implements the MessageTypeInterface.

        Raises:
            Exception: If an action in the message_json is not supported.
        """
        for key, MessageClass in cls.message_classes.items():
            if key in message_json:
                return MessageClass(message_json)
        raise ValueError(f"Unsupported action in message_json: {message_json}")
