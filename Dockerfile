# Using nvidia/cuda base image with Python 3.11
FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TAGS_TO_ADD='{}'
ENV GENERATE_ON_COMMAND=false
ENV TOTAL_IMAGES=0
ENV BATCH_SIZE=50

# Install system dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3-distutils \
    python3-pip \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender-dev \
    libxext6 \
    tzdata \
    curl \
    git && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Update pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Set the working directory
WORKDIR /app

# Update pip
RUN pip install -U pip && \
    pip install --upgrade certifi

RUN curl -sSL https://install.python-poetry.org | python3 -

# Set PATH for poetry
ENV PATH="/root/.local/bin:$PATH"

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Copy project files
COPY . .

# Install dependencies
RUN --mount=type=secret,id=git-credentials,dst=/root/.git-credentials \
    git config --global credential.helper store && \
    poetry install --with dev --sync

# Ensure the scripts are executable
RUN chmod +x start_server.sh start_generating.sh

# Start the server and consumer
CMD ["/bin/sh", "-c", "start_server.sh & start_generating.sh"]
