# Using nvidia/cuda base image with Python 3.9
FROM nvidia/cuda:11.7.0-devel-ubuntu20.04

ARG GITHUB_TOKEN

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
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install the project dependencies
RUN pip3 install -U pip
RUN pip3 install torch torchvision torchaudio
RUN echo "machine github.com login ${GITHUB_TOKEN}" > ~/.netrc \
    && chmod 600 ~/.netrc \
    && pip3 install . \
    && rm ~/.netrc

# Start the server and consumer
CMD ["sh", "-c", "./start_server.sh && ./start_consuming.sh"]
