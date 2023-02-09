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

    If you are in MacOS:

    ```shell
    pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
    GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true pip3 install -e .
    ```
