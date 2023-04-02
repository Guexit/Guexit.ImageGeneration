import os

AZURE_SERVICE_BUS_CONNECTION_STRING = os.environ.get(
    "AZURE_SERVICE_BUS_CONNECTION_STRING", ""
)
AZURE_SERVICE_BUS_TOPIC_NAME = os.environ.get(
    "AZURE_SERVICE_BUS_TOPIC_NAME", "guexit-imagegeneration"
)
AZURE_SERVICE_BUS_QUEUE_NAME = os.environ.get(
    "AZURE_SERVICE_BUS_QUEUE_NAME", "guexit-cron-generate-image-command"
)
AZURE_SERVICE_BUS_MESSAGE_TYPE = os.environ.get(
    "AZURE_SERVICE_BUS_MESSAGE_TYPE", "urn:message:Guexit.Game.Messages:ImageGenerated"
)
IMAGE_GENERATION_API = os.environ.get("IMAGE_GENERATION_API", "http://127.0.0.1:5000")
AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STORAGE_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "test")
