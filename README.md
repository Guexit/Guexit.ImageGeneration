# Guexit.ImageGeneration

[![codecov](https://codecov.io/gh/Guexit/Guexit.ImageGeneration/branch/main/graph/badge.svg?token=U47OQU1RG5)](https://codecov.io/gh/Guexit/Guexit.ImageGeneration)

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

    If you are in Linux or Windows you have to check what CUDA version you have installed and use [this Pytorch guide](https://pytorch.org/get-started/locally/) to know what to install. Ideally you would want to install version 11.7. You need a GPU with at least 4GB of memory. If not, you should send requests that are executed in the CPU.

    ```shell
    # CUDA 11.7
    pip install -e .
    # WINDOWS
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    # LINUX
    pip install torch torchvision torchaudio
    ```

    If you are in MacOS:

    ```shell
    pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
    GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true pip3 install -e .
    ```

5. Install pre-commit:

    ```shell
    pre-commit install
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
            "model_path": "prompthero/openjourney-v4",
            "model_scheduler": "euler_a",
            "prompt": {
                "positive": "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed",
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
python3 examples/txt2image.py --model_path "prompthero/openjourney-v4" /
                               --model_scheduler euler_a /
                               --positive_prompt "portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed"
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
```

These are in `env_samples.env`, but you need to have them in a `.env` file in the project directory: `cp env_samples.env .env` and then substitute the values with the correct ones.

You can set these environment variables in your terminal or in a .env file in the project directory. Here's an example of how to set them in your terminal:

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

## Docker

To run the service and the handler in Docker:

1. Have Docker installed.

2. Git credentials must be stored in `~/.git-credentials`. To do so please execute:

    ```shell
    git config --global credential.helper "store --file ~/.git-credentials"
    ```

3. Build the docker image with:

    ```shell
    docker build . --secret id=git-credentials,src=~/.git-credentials -t guexit_image_generation
    ```

4. Run the docker image with:

    ```shell
    docker run --gpus all --env-file .env -p 5000:5000 guexit_image_generation
    ```
