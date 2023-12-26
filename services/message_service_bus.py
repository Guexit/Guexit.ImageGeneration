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

    def create_message_to_send(self, file_blob_url: List[dict], metadata: dict) -> str:
        """
        Create a message to send to the service bus

        Args:
            file_blob_url (List[dict]): List of file blob urls
            metadata (dict): Metadata for the files

        Returns:
            str: The message to send to the service bus
        """
        metadata = {key: metadata[key] for key in self.metadata_fields_to_keep}
        metadata = {**metadata, **self.tags_to_add}
        tags = [f"{key}:{str(value)}" for key, value in metadata.items()]
        message = MessageServiceBus(url=file_blob_url, tags=tags)
        return message.json()
