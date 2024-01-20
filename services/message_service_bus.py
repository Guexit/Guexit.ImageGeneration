import importlib.metadata
from typing import List

from services.models import MessageServiceBus


class MessageServiceBusClass:
    """
    Class to create messages to send to the service bus
    """

    def __init__(
        self, metadata_fields_to_keep: List[str], tags_to_add: dict = None
    ) -> None:
        self.metadata_fields_to_keep = metadata_fields_to_keep
        self.tags_to_add = tags_to_add if tags_to_add is not None else {}

    def get_package_version(self, package_name: str) -> str:
        """
        Get the version of a package.

        Args:
            package_name (str): The name of the package to get the version for.

        Returns:
            str: The version of the package.
        """
        try:
            # Attempt to retrieve the version using importlib.metadata (Python 3.8+)
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            # If the package is not found, we return an empty string or raise an error
            # Depending on the use case, you may want to handle this differently
            return ""

    def create_message_to_send(self, file_blob_url: str, metadata: dict = None) -> str:
        """
        Create a message to send to the service bus

        Args:
            file_blob_url (str): List of file blob urls
            metadata (dict): Metadata for the files

        Returns:
            str: The message to send to the service bus
        """
        if metadata is None:
            metadata = {}
        metadata = {key: metadata[key] for key in self.metadata_fields_to_keep}
        metadata = {**metadata, **self.tags_to_add}
        metadata["image_generation_version"] = self.get_package_version(
            "image_generation"
        )
        tags = [f"{key}:{str(value)}" for key, value in metadata.items()]
        message = MessageServiceBus(url=file_blob_url, tags=tags)
        return message.json()
