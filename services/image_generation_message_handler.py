import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

from cloud_manager.azure_blob_storage import AzureBlobStorage
from cloud_manager.azure_service_bus import AzureServiceBus
from cloud_manager.interfaces.blob_storage import BlobStorageInterface
from cloud_manager.interfaces.service_bus import ServiceBusInterface
from image_generation.custom_logging import set_logger
from image_generation.utils import store_zip_images_temporarily, wait_for_service
from services import config
from services.message_handlers import MessageFactory, MessageTypeInterface
from services.message_service_bus import MessageServiceBusClass

logger = set_logger("Image Generation Message Handler")


class ImageGenerationMessageHandler:
    """
    A message handler that processes incoming messages to generate images
    and uploads them to Azure Blob Storage, then sends a message with the
    generated image URLs to an Azure Service Bus topic.
    """

    def __init__(self, tags_to_add: dict = None) -> None:
        """
        Initialize the ImageGenerationMessageHandler instance.
        """
        self.azure_cloud: BlobStorageInterface = AzureBlobStorage(
            config.AZURE_STORAGE_CONNECTION_STRING
        )

        logger.info(
            f"Using Azure Service Bus Max Lock Renewal Duration: {config.AZURE_SERVICE_BUS_MAX_LOCK_RENEWAL_DURATION}"
        )
        self.service_bus: ServiceBusInterface = AzureServiceBus(
            config.AZURE_SERVICE_BUS_CONNECTION_STRING,
            config.AZURE_SERVICE_BUS_MAX_LOCK_RENEWAL_DURATION,
        )
        metadata_fields_to_keep = [
            "model_path",
            "style",
        ]
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=metadata_fields_to_keep, tags_to_add=tags_to_add
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
        try:
            logger.info(f"Received message: {message}")
            message_json = json.loads(message)["message"]
            logger.info(f"Message content: {message_json}")

            processed_message, message = self.process_incoming_message(message_json)
            (
                files_blob_urls,
                metadata_list,
                temp_dir,
            ) = self.upload_images_to_blob_storage(processed_message, message)
            for file_blob_url, metadata in zip(files_blob_urls, metadata_list):
                message_to_send = self.message_service_bus.create_message_to_send(
                    file_blob_url, metadata
                )

                logger.info(f"Sending message ImageGenerated: {message_to_send}")
                self.service_bus.publish(
                    config.AZURE_SERVICE_BUS_TOPIC_NAME, message_to_send
                )
            temp_dir.cleanup()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            raise

    def process_incoming_message(
        self, message_json: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], MessageTypeInterface]:
        """
        Process the incoming message JSON to determine the appropriate endpoint
        and pass the message to the image generation API.

        Args:
            message_json (Dict[str, Any]): The incoming message JSON.

        Returns:
            Tuple[Dict[str, Any], MessageInterface]: The response from the image generation API and the processed message.
        """
        try:
            message = MessageFactory.create_message(message_json)
            response = message.process()
            logger.info(f"Response: {response}")
            return response, message
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    def upload_images_to_blob_storage(
        self, response: Dict[str, Any], message: MessageTypeInterface
    ) -> Tuple[List[Dict[str, str]], TemporaryDirectory]:
        """
        Extract image files from the API response, store them temporarily,
        upload them to Azure Blob Storage, and return a list of URLs and
        a TemporaryDirectory object to clean up the files afterwards.

        Args:
            response (Dict[str, Any]): The response from the image generation API.
            message (MessageInterface): The processed message.

        Returns:
            Tuple[List[Dict[str, str]], TemporaryDirectory]: A tuple containing
            the list of file objects with URLs and a TemporaryDirectory object.
        """
        logger.info("Getting file objects...")
        try:
            file_paths, metadata_list, temp_dir = store_zip_images_temporarily(response)
            logger.debug(f"File paths: {file_paths}")
            file_objects = [
                {
                    "name": message.get_file_name(file_path),
                    "path": str(Path(file_path)),
                    "metadata": metadata,
                }
                for file_path, metadata in zip(file_paths, metadata_list)
            ]
            logger.info(f"File objects: {file_objects}")
            logger.info(
                f"Uploading files to blob storage '{config.AZURE_STORAGE_CONTAINER_NAME}'"
            )
            files_blob_urls = self.azure_cloud.push_objects(
                config.AZURE_STORAGE_CONTAINER_NAME, file_objects, overwrite=True
            )
            logger.info(f"Uploaded files to blob storage: {files_blob_urls}")
            return files_blob_urls, metadata_list, temp_dir
        except Exception as e:
            logger.error(f"Error uploading images to blob storage: {e}")
            raise


def main(tags_to_add=None):
    wait_for_service(config.IMAGE_GENERATION_API, timeout=2260)
    service_bus: ServiceBusInterface = AzureServiceBus(
        config.AZURE_SERVICE_BUS_CONNECTION_STRING
    )
    service_bus.consume_indefinitely(
        config.AZURE_SERVICE_BUS_QUEUE_NAME,
        ImageGenerationMessageHandler(tags_to_add=tags_to_add),
    )


if __name__ == "__main__":
    import argparse

    # Parse command line arguments for tags_to_add
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags_to_add", type=json.loads, default=None)
    main(**vars(parser.parse_args()))
