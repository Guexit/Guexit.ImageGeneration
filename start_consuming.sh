#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Pass all arguments to the Python script
python3 services/image_generation_message_handler.py "$@"
