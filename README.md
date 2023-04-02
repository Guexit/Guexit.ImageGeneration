# Guexit.ImageGeneration

AI Image Generation Service

## Local

### Setup

1. Install [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html)

2. Create and activate environment with:

    ```shell
    conda create -n sd_guexit python=3.9 --no-default-packages -y
    conda activate sd_guexit
    ```

3. Install Poetry from [here](https://python-poetry.org/docs/#installation)

4. Install dependencies with:

    If you are in Linux or Windows:

    ```shell
    pip3 install torch==1.12.1 torchvision>=0.13.1
    pip3 install -e .
    ```

    TODO: Instructions for installing with GPU support for Windows/Linux.

    If you are in MacOS:

    ```shell
    pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
    GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true pip3 install -e .
    ```

### Run

1. In one terminal, start the server with:

    ```shell
    sh start_server.sh
    ```

2. You can go to [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs) to see the swagger API. You will find an example of a valid request. It should look like this:

    ```json
    {
        "text_to_image": {
            "model_path": "prompthero/openjourney-2",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
                "negative": "bad quality, malformed",
                "guidance_scale": 16.5
            },
            "height": 688,
            "width": 512,
            "num_inference_steps": 50,
            "num_images": 2,
            "seed": 57857
        }
    }
    ```

3. You can also execute the script in the example folder to test the API:

```shell
python3 examples/text2image.py --model_path prompthero/openjourney-2 /
                               --model_scheduler euler_a /
                               --positive_prompt "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4"
                               --negative_prompt "bad quality, malformed"
                               --guidance_scale 16.5
                               --height 688
                               --width 512
                               --num_inference_steps 50
                               --num_images 2
                               --seed 57857
```

### Using ImageGenerationMessageHandler

The ImageGenerationMessageHandler in `scripts/image_generation_message_handler.py` is a script that processes incoming messages to generate images, uploads them to Azure Blob Storage, and sends a message with the generated image URLs to an Azure Service Bus topic.

To use the ImageGenerationMessageHandler, you need to have a few environment variables set up:

```shell
AZURE_STORAGE_CONNECTION_STRING: The connection string for your Azure Storage account.
AZURE_SERVICE_BUS_CONNECTION_STRING: The connection string for your Azure Service Bus instance.
AZURE_STORAGE_CONTAINER_NAME: The name of the container in your Azure Storage account where the images will be uploaded.
AZURE_SERVICE_BUS_QUEUE_NAME: The name of the queue in your Azure Service Bus instance where messages will be consumed.
AZURE_SERVICE_BUS_TOPIC_NAME: The name of the topic in your Azure Service Bus instance where messages will be published.
AZURE_SERVICE_BUS_MESSAGE_TYPE: The message type for the messages sent to the Azure Service Bus topic.
You can set these environment variables in your terminal or in a .env file in the project directory. Here's an example of how to set them in your terminal:
```

```shell
export AZURE_STORAGE_CONNECTION_STRING="<your_storage_connection_string>"
export AZURE_SERVICE_BUS_CONNECTION_STRING="<your_service_bus_connection_string>"
export AZURE_STORAGE_CONTAINER_NAME="<your_storage_container_name>"
export AZURE_SERVICE_BUS_QUEUE_NAME="<your_service_bus_queue_name>"
export AZURE_SERVICE_BUS_TOPIC_NAME="<your_service_bus_topic_name>"
export AZURE_SERVICE_BUS_MESSAGE_TYPE="<your_service_bus_message_type>"
```

Once you have the environment variables set up, you first need to have the service running on one terminal:

```shell
sh start_server.sh
```

Then you can start consuming messages from Azure Service Bus with:

```shell
sh start_consuming.sh
```

This will start the ImageGenerationMessageHandler and begin processing messages from the specified Azure Service Bus queue. The generated images will be uploaded to the specified Azure Storage container, and the resulting image URLs will be sent as a message to the specified Azure Service Bus topic.
