# Guexit.ImageGeneration

AI Image Generation Service

## Local

### Setup

1. Install Python (3.8 - 3.10)

2. Create and activate environment with:

    ```shell
    python3 -m venv env && . env/bin/activate
    pip install -U pip
    ```

3. Install Poetry from [here](https://python-poetry.org/docs/#installation)

4. Install dependencies with:

    If you are in Linux or Windows:

    ```shell
    pip install torch==1.12.1 torchvision>=0.13.1
    pip install -e .
    ```

    If you are in MacOS (CURRENTLY FAILING IN MACOS):

    ```shell
    pip3 install torch torchvision
    GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true pip3 install -e .
    ```
