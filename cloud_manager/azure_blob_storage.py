"""
This class implements the CloudInterface for Azure Cloud.
"""

from typing import List

from azure.storage.blob import BlobServiceClient

from cloud_manager.custom_logging import set_logger
from cloud_manager.interfaces.blob_storage import BlobStorageInterface

logger = set_logger("Azure Blob Storage")


class AzureBlobStorage(BlobStorageInterface):
    def __init__(self, connection_string: str):
        logger.info("Initializing Azure Blob Storage")
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        except ValueError as e:
            logger.error(f"Invalid connection string: {e}")
            raise

    def push_objects(
        self, container_name: str, objects: List[dict], overwrite: bool = False
    ) -> List[str]:
        if not objects:
            logger.warning("No objects provided for upload")
            return []

        logger.info(f"Pushing {len(objects)} objects to '{container_name}'")
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_urls = []
        for obj in objects:
            try:
                blob_client = container_client.get_blob_client(obj["name"])
                with open(obj["path"], "rb") as data:
                    metadata = obj.get("metadata", {})
                    blob_client.upload_blob(
                        data, overwrite=overwrite, metadata=metadata
                    )
                blob_urls.append(blob_client.url)
            except FileNotFoundError:
                logger.error(f"File not found: {obj['path']}")
            except Exception as e:
                logger.error(f"Error uploading object '{obj['name']}': {e}")
        return blob_urls
