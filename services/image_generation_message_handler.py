import json
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

from cloud_manager.azure_blob_storage import AzureBlobStorage
from cloud_manager.azure_service_bus import AzureServiceBus
from cloud_manager.interfaces.blob_storage import BlobStorageInterface
from cloud_manager.interfaces.service_bus import ServiceBusInterface

from image_generation.custom_logging import set_logger
from image_generation.utils import (
    call_image_generation_api,
    store_zip_images_temporarily,
    wait_for_service,
)
from services import config

logger = set_logger("Image Generation Message Handler")


def get_file_name(style: str, seed: int, idx: int) -> str:
    if seed == -1:
        return f"{style}_{uuid.uuid1()}_{seed}_{idx}.png"
    else:
        return f"{style}_{seed}_{idx}.png"


def create_message_to_send(file_blob_url: List[dict]) -> str:
    message = {
        "destinationAddress": "",
        "headers": {},
        "message": {"url": file_blob_url},
        "messageType": [config.AZURE_SERVICE_BUS_MESSAGE_TYPE],
    }
    return json.dumps(message)


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
            config.AZURE_SERVICE_BUS_CONNECTION_STRING,
            config.AZURE_SERVICE_BUS_MAX_LOCK_RENEWAL_DURATION,
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

        processed_message, message_json = self.process_incoming_message(message_json)
        files_blob_urls, temp_dir = self.upload_images_to_blob_storage(
            processed_message, message_json
        )
        for file_blob_url in files_blob_urls:
            message_to_send = create_message_to_send(file_blob_url)

            logger.info(f"Sending message ImageGenerated: {message_to_send}")
            self.service_bus.publish(
                config.AZURE_SERVICE_BUS_TOPIC_NAME, message_to_send
            )
        temp_dir.cleanup()

    def process_incoming_message(
        self, message_json: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process the incoming message JSON to determine the appropriate endpoint
        and pass the message to the image generation API.

        Args:
            message_json (Dict[str, Any]): The incoming message JSON.

        Returns:
            Dict[str, Any]: The response from the image generation API.
            message_json (Dict[str, Any]): The incoming message JSON.
        """
        if "text_to_style" in message_json:
            endpoint = "/text_to_style"
            message_json = {
                "style": message_json["text_to_style"]["style"],
                "num_images": message_json["text_to_style"]["num_images"],
            }
        elif "text_to_image" in message_json:
            endpoint = "/text_to_image"
            message_json = message_json["text_to_image"]
        else:
            raise Exception(f"Action not supported: {message_json}")

        response = call_image_generation_api(
            config.IMAGE_GENERATION_API, endpoint, message_json
        )
        logger.info(f"Response: {response}")

        return response, message_json

    def upload_images_to_blob_storage(
        self, response: Dict[str, Any], message_json: Dict[str, Any]
    ) -> Tuple[List[Dict[str, str]], TemporaryDirectory]:
        """
        Extract image files from the API response, store them temporarily,
        upload them to Azure Blob Storage, and return a list of URLs and
        a TemporaryDirectory object to clean up the files afterwards.

        Args:
            response (Dict[str, Any]): The response from the image generation API.
            message_json (Dict[str, Any]): The incoming message JSON.

        Returns:
            Tuple[List[Dict[str, str]], TemporaryDirectory]: A tuple containing
            the list of file objects with URLs and a TemporaryDirectory object.
        """
        logger.info("Getting file objects...")
        file_paths, temp_dir = store_zip_images_temporarily(response)
        logger.debug(f"File paths: {file_paths}")
        file_objects = [
            {
                "name": get_file_name(
                    style=message_json["style"],
                    seed=message_json["seed"] if "seed" in message_json else -1,
                    idx=i,
                ),
                "path": str(Path(file_path)),
            }
            for i, file_path in enumerate(file_paths)
        ]
        logger.info(f"File objects: {file_objects}")
        logger.info("Uploading files to blob storage")
        files_blob_urls = self.azure_cloud.push_objects(
            config.AZURE_STORAGE_CONTAINER_NAME, file_objects, overwrite=True
        )
        logger.info(f"Uploaded files to blob storage: {files_blob_urls}")

        return files_blob_urls, temp_dir


def main():
    wait_for_service(config.IMAGE_GENERATION_API, timeout=2260)
    service_bus: ServiceBusInterface = AzureServiceBus(
        config.AZURE_SERVICE_BUS_CONNECTION_STRING
    )
    service_bus.consume_indefinitely(
        config.AZURE_SERVICE_BUS_QUEUE_NAME, ImageGenerationMessageHandler()
    )


if __name__ == "__main__":
    main()
