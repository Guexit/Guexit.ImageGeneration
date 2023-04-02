from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple
from gevent import monkey

monkey.patch_all()
import json
from image_generation.custom_logging import set_logger
from image_generation.utils import (
    call_image_generation_api,
    store_zip_images_temporarily,
)
from cloud_manager.azure_blob_storage import AzureBlobStorage
from cloud_manager.interfaces.blob_storage import BlobStorageInterface
from cloud_manager.azure_service_bus import AzureServiceBus
from cloud_manager.interfaces.service_bus import ServiceBusInterface
import uuid
from pathlib import Path

from services import config

logger = set_logger("Image Generation Message Handler")


def get_file_name(prompt: Dict[str, str], seed: int, idx: int) -> str:
    prompt_str = "_".join(prompt["positive"].split(" "))
    if seed == -1:
        return f"{prompt_str}_{uuid.uuid4()}_{seed}_{idx}.png"
    else:
        return f"{prompt_str}_{seed}_{idx}.png"


def create_message_to_send(file_objects: List[Dict[str, str]]) -> str:
    return f"""
    {{
        "destinationAddress": "",
        "headers": {{}},
        "message": {{
            "urls": {file_objects}
        }},
        "messageType": [
            {config.AZURE_SERVICE_BUS_MESSAGE_TYPE}
        ]
    }}
    """


class ImageGenerationMessageHandler:
    """
    A message handler that processes incoming messages to generate images
    and uploads them to Azure Blob Storage, then sends a message with the
    generated image URLs to an Azure Service Bus topic.
    """

    def __init__(self) -> None:
        """
        Initialize the ImageGenerationMessageHandler instance.
        """
        self.azure_cloud: BlobStorageInterface = AzureBlobStorage(
            config.AZURE_STORAGE_CONNECTION_STRING
        )
        self.service_bus: ServiceBusInterface = AzureServiceBus(
            config.AZURE_SERVICE_BUS_CONNECTION_STRING
        )

    def __call__(self, message: str) -> None:
        """
        Process a given message by calling the handle_message method.

        Args:
            message (str): The message to be processed.
        """
        self.handle_message(message)

    def handle_message(self, message: str) -> None:
        """
        Handle the given message by processing the request, generating images,
        uploading them to Azure Blob Storage, and sending a message with the
        generated image URLs to an Azure Service Bus topic.

        Args:
            message (str): The message to be handled.
        """
        logger.info(f"Received message: {message}")
        message_json = json.loads(message)["message"]
        logger.info(f"Message content: {message_json}")

        processed_message = self.process_incoming_message(message_json)
        file_objects, temp_dir = self.upload_images_to_blob_storage(processed_message)
        message_to_send = create_message_to_send(file_objects)

        logger.info(f"Sending message ImageGenerated: {message_to_send}")
        self.service_bus.publish(config.AZURE_SERVICE_BUS_TOPIC_NAME, message_to_send)
        temp_dir.cleanup()

    def process_incoming_message(self, message_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the incoming message JSON to determine the appropriate endpoint
        and pass the message to the image generation API.

        Args:
            message_json (Dict[str, Any]): The incoming message JSON.

        Returns:
            Dict[str, Any]: The response from the image generation API.
        """
        if "text_to_image" in message_json:
            endpoint = "/text_to_image"
            message_json = message_json["text_to_image"]
        else:
            raise Exception(f"Action not supported: {message_json}")

        response = call_image_generation_api(
            config.IMAGE_GENERATION_API, endpoint, message_json
        )
        logger.info(f"Response: {response}")

        return response

    def upload_images_to_blob_storage(
        self, response: Dict[str, Any]
    ) -> Tuple[List[Dict[str, str]], TemporaryDirectory]:
        """
        Extract image files from the API response, store them temporarily,
        upload them to Azure Blob Storage, and return a list of URLs and
        a TemporaryDirectory object to clean up the files afterwards.

        Args:
            response (Dict[str, Any]): The response from the image generation API.

        Returns:
            Tuple[List[Dict[str, str]], TemporaryDirectory]: A tuple containing
            the list of file objects with URLs and a TemporaryDirectory object.
        """
        file_paths, temp_dir = store_zip_images_temporarily(response)
        file_objects = [
            {
                "name": get_file_name(response["prompt"], response["seed"], i),
                "path": str(Path(file_path)),
            }
            for i, file_path in enumerate(file_paths)
        ]
        logger.info(f"File objects: {file_objects}")
        logger.info("Uploading files to blob storage")
        self.azure_cloud.push_objects(
            config.AZURE_STORAGE_CONTAINER_NAME, file_objects, overwrite=True
        )

        return file_objects, temp_dir


def main():
    service_bus: ServiceBusInterface = AzureServiceBus(
        config.AZURE_SERVICE_BUS_CONNECTION_STRING
    )
    service_bus.consume_indefinitely(
        config.AZURE_SERVICE_BUS_QUEUE_NAME, ImageGenerationMessageHandler()
    )


if __name__ == "__main__":
    main()
