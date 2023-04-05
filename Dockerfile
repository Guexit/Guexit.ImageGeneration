# Using nvidia/cuda base image with Python 3.9
FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

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
    && rm -rf /var/lib/apt/lists/*

# Install torch and torchvision
RUN pip3 install torch==1.12.1 torchvision>=0.13.1

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install the project dependencies
RUN pip3 install -e .

# Start the server and consumer
CMD ["./start_server.sh", "&&", "./start_consuming.sh"]
