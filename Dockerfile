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

# Create and activate virtual environment
RUN python3.9 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install first what can be cached
RUN python -m pip install -U pip
RUN python -m pip install -U setuptools

# Install torch, torchvision, and torchaudio (cacheable layer)
RUN python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Copy the project files
COPY . .

# Install the project dependencies
RUN --mount=type=secret,id=git-credentials,dst=/root/.git-credentials \
    git config --global credential.helper store && \
    python -m pip install .

# Start the server and consumer
CMD ["sh", "-c", "./start_server.sh & ./start_consuming.sh"]
