#!/bin/bash

# API settings
HOST="http://127.0.0.1:5000"
ENDPOINT="/text_to_style"

# Text to style settings
STYLE="general"
NUM_IMAGES=20

# Make the API call and save the response as a zip file
curl -X POST -H "Content-Type: application/json" -d "{
    \"style\": \"$STYLE\",
    \"num_images\": $NUM_IMAGES
}" "$HOST$ENDPOINT" --output images.zip

# Extract the zip file
mkdir -p images
unzip -o images.zip -d images
rm images.zip
