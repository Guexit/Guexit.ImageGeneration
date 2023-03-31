from gevent import monkey

monkey.patch_all()
import os
from cloud_manager.azure_service_bus import AzureServiceBus
from cloud_manager.interfaces.service_bus import ServiceBusInterface
import json
from image_generation.custom_logging import set_logger
from image_generation.utils import (
    call_image_generation_api,
    store_zip_images_temporarily,
)
from cloud_manager.azure_blob_storage import AzureBlobStorage
from cloud_manager.interfaces.blob_storage import BlobStorageInterface
import uuid

logger = set_logger("Image Generation Message Handler")

asb_connection_string = os.environ["AZURE_SERVICE_BUS_CONNECTION_STRING"]
asb_topic_name = os.environ.get(
    "AZURE_SERVICE_BUS_TOPIC_NAME", "guexit-imagegeneration"
)
asb_queue_name = os.environ.get(
    "AZURE_SERVICE_BUS_QUEUE_NAME", "guexit-cron-generate-image-command"
)
asb_message_type = os.environ.get(
    "AZURE_SERVICE_BUS_MESSAGE_TYPE", "urn:message:Guexit.Game.Messages:ImageGenerated"
)
image_generation_api = os.environ.get("IMAGE_GENERATION_API", "http://127.0.0.1:5000")
as_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
as_container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "test")

azure_cloud: BlobStorageInterface = AzureBlobStorage(as_connection_string)
service_bus: ServiceBusInterface = AzureServiceBus(asb_connection_string)


def get_file_name(prompt, seed, idx):
    prompt_str = "_".join(prompt["positive"].split(" "))
    if seed == -1:
        return f"{prompt_str}_{uuid.uuid4()}_{seed}_{idx}.png"
    else:
        return f"{prompt_str}_{seed}_{idx}.png"


def image_generation_message_handler(message):
    logger.info(f"Received message: {message}")
    message_json = json.loads(message)["message"]
    logger.info(f"Message content: {message_json}")
    endpoint = ""
    if "text_to_image" in message_json:
        endpoint = "/text_to_image"
        message_json = message_json["text_to_image"]
    else:
        raise Exception(f"Action not supported: {message_json}")
    response = call_image_generation_api(image_generation_api, endpoint, message_json)
    logger.info(f"Response: {response}")
    file_paths, temp_dir = store_zip_images_temporarily(response)
    file_objects = [
        {
            "name": get_file_name(message_json["prompt"], message_json["seed"], i),
            "path": file_path,
        }
        for i, file_path in enumerate(file_paths)
    ]
    logger.info(f"File objects: {file_objects}")
    logger.info("Uploading files to blob storage")
    blob_urls = azure_cloud.push_objects(as_container_name, file_objects, overwrite=True)
    temp_dir.cleanup()
    logger.info(f"Blob urls: {blob_urls}")
    message_to_send = """
    {{
        "destinationAddress": "",
        "headers": {{}},
        "message": {{
            "urls": {blob_urls}
        }},
        "messageType": [
            {asb_message_type}
        ]
    }}
    """.format(
        **{"blob_urls": blob_urls, "asb_message_type": asb_message_type},
    )
    print(f"Sending message ImageGenerated: {message_to_send}")
    service_bus.publish(asb_topic_name, message_to_send)


def main():
    service_bus: ServiceBusInterface = AzureServiceBus(asb_connection_string)
    service_bus.consume_indefinitely(asb_queue_name, image_generation_message_handler)


if __name__ == "__main__":
    main()
