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
    python3.9-venv \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender-dev \
    libxext6 \
    tzdata \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install setuptools before creating virtual environment
RUN pip install -U pip && pip install setuptools>=65.5.0

# Create and activate virtual environment
RUN python3.9 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install torch, torchvision, and torchaudio (cacheable layer)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Install diffusers
RUN pip install diffusers>=0.11.1 transformers>=4.25.1 accelerate>=0.15.0

# Set environment variable for the model
ENV DEFAULT_MODEL_NAME="prompthero/openjourney-v4"
# Set the transformers cache directory
ENV TRANSFORMERS_CACHE=/models

# Pre-download the model
RUN python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('${DEFAULT_MODEL_NAME}')"

# Copy the project files
COPY . .

# Install the project dependencies
RUN --mount=type=secret,id=git-credentials,dst=/root/.git-credentials \
    git config --global credential.helper store && \
    pip install .

# Start the server and consumer
CMD ["sh", "-c", "./start_server.sh & ./start_consuming.sh"]
