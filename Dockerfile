# Using nvidia/cuda base image with Python 3.9
FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    python3.9-dev \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender-dev \
    libxext6 \
    tzdata \
    git \
    && rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1


# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install -U pip && \
    pip install poetry && \
    pip install --upgrade certifi

# Set Poetry configuration to not create a virtual environment
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock file for dependencies installation
COPY pyproject.toml poetry.lock ./

# Install the project dependencies
RUN poetry install --no-interaction --no-root

# Copy the project files
COPY . .

# Start the server and consumer
CMD ["sh", "-c", "python3 -m uvicorn image_generation.api.server:app --host 127.0.0.1 --port 5000 --timeout-keep-alive 600 & python3 services/image_generation_message_handler.py"]
