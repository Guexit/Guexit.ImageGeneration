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
    },
    "return_images": true,
    "upload_images": false
    }
    ```

3. You can also execute the scripts in the example folder to test the API.
