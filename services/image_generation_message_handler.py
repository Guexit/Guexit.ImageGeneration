import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

from rich.progress import BarColumn, Progress, TextColumn

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

    def __init__(self, tags_to_add: dict = None, batch_size: int = 50) -> None:
        """
        Initialize the ImageGenerationMessageHandler instance.

        Args:
            tags_to_add (dict, optional): A dictionary of tags to add to the Azure Service Bus message. Defaults to None.
            batch_size (int, optional): Number of images to process in each batch Defaults to 50.
        """
        if batch_size <= 1:
            error_message = "Batch size must be greater than 1."
            logger.error(error_message)
            raise ValueError(error_message)
        logger.info(f"Using batch size: {batch_size}")
        self.batch_size = batch_size
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
        logger.info(f"Keeping metadata fields: {metadata_fields_to_keep}")
        self.message_service_bus = MessageServiceBusClass(
            metadata_fields_to_keep=metadata_fields_to_keep, tags_to_add=tags_to_add
        )

    def __call__(self, message: str) -> None:
        """
        Process a given message by calling the handle_message method.

        Args:
            message (str): The message to be processed.
        """
        logger.info(f"Received message: {message}")
        message_json = json.loads(message)["message"]
        self.handle_message(message_json)

    def get_num_images_from_message(self, message_json: dict) -> int:
        """
        Get the number of images to generate from the given message.

        Args:
            message_json (dict): The message JSON.

        Returns:
            int: The number of images to generate.
        """
        for key, value in message_json.items():
            if isinstance(value, dict):
                if "num_images" in value:
                    return value["num_images"]

        error_message = "Could not find num_images in message_json"
        logger.error(error_message)
        raise ValueError(error_message)

    def set_num_images_in_message(self, message_json: dict, num_images: int) -> dict:
        """
        Set the number of images to generate in the given message.

        Args:
            message_json (dict): The message JSON.
            num_images (int): The number of images to generate.

        Returns:
            dict: The modified message JSON.
        """
        for key, value in message_json.items():
            if isinstance(value, dict):
                if "num_images" in value:
                    value["num_images"] = num_images
                    return message_json
        error_message = "Could not find num_images in message_json"
        logger.error(error_message)
        raise ValueError(error_message)

    def handle_message(self, message_json: dict) -> None:
        """
        Handle the given message by processing the request, generating images,
        uploading them to Azure Blob Storage, and sending a message with the
        generated image URLs to an Azure Service Bus topic.

        Args:
            message_json (dict): The message json to be handled.
        """
        try:
            logger.info(f"Message content: {message_json}")
            num_images = self.get_num_images_from_message(message_json)
            num_batches = -(-num_images // self.batch_size)
            logger.info(
                f"Number of images: {num_images}, Batch size: {self.batch_size}, Number of batches: {num_batches}"
            )
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TextColumn("[bold green]{task.fields[batch_info]}"),
            ) as progress:
                task = progress.add_task(
                    "Generating images...",
                    total=num_batches,
                    batch_info=f"0/{num_images}",
                )

                for i in range(0, num_images, self.batch_size):
                    message_json = self.set_num_images_in_message(
                        message_json, min(self.batch_size, num_images - i)
                    )
                    processed_message, message = self.process_incoming_message(
                        message_json
                    )
                    (
                        files_blob_urls,
                        metadata_list,
                        temp_dir,
                    ) = self.upload_images_to_blob_storage(processed_message, message)
                    for file_blob_url, metadata in zip(files_blob_urls, metadata_list):
                        metadata.update(message.message_json)
                        message_to_send = (
                            self.message_service_bus.create_message_to_send(
                                file_blob_url, metadata
                            )
                        )

                        logger.info(
                            f"Sending message ImageGenerated: {message_to_send}"
                        )
                        self.service_bus.publish(
                            config.AZURE_SERVICE_BUS_TOPIC_NAME, message_to_send
                        )
                    progress.update(
                        task,
                        advance=1,
                        batch_info="{}/{}".format(
                            min(i + self.batch_size, num_images), num_images
                        ),
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

    def run(self, generate_on_command: bool = False, total_images: int = 0):
        """
        Run the handler in the appropriate mode based on the provided parameters.

        Args:
            generate_on_command (bool): Whether to run in generate_on_command mode.
            total_images (int): Total number of images to generate in generate_on_command mode.
            batch_size (int): Number of images to send in each batch in generate_on_command mode.
        """
        if generate_on_command:
            if total_images <= 0:
                error_message = (
                    "Please provide total_images to run in generate_on_command mode."
                )
                logger.error(error_message)
                raise ValueError(error_message)
            message_json = {
                "text_to_style": {"style": "general", "num_images": total_images}
            }
            self.handle_message(message_json)
        else:
            # Default to standard message handling
            self.service_bus.consume_indefinitely(
                config.AZURE_SERVICE_BUS_QUEUE_NAME,
                self,
            )


def main(tags_to_add=None, generate_on_command=False, total_images=0, batch_size=50):
    wait_for_service(config.IMAGE_GENERATION_API, timeout=2260)
    handler = ImageGenerationMessageHandler(
        tags_to_add=tags_to_add, batch_size=batch_size
    )
    handler.run(generate_on_command=generate_on_command, total_images=total_images)


if __name__ == "__main__":
    import argparse

    # Parse command line arguments for tags_to_add
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags_to_add", type=json.loads, default=None)
    parser.add_argument("--generate_on_command", action="store_true", default=False)
    parser.add_argument("--total_images", type=int, default=0)
    parser.add_argument("--batch_size", type=int, default=50)
    args = parser.parse_args()
    main(
        tags_to_add=args.tags_to_add,
        generate_on_command=args.generate_on_command,
        total_images=args.total_images,
        batch_size=args.batch_size,
    )
    # Example usage:
    # python services/image_generation_message_handler.py --tags_to_add '{"test":"test"}' --generate_on_command --total_images 10
