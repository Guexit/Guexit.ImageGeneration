#!/bin/bash

# API settings
HOST="http://127.0.0.1:5000"
ENDPOINT="/text_to_image"

# Text to image settings
MODEL_PATH="prompthero/openjourney-v4"
MODEL_SCHEDULER="euler_a"
POSITIVE_PROMPT="portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed"
NEGATIVE_PROMPT="bad quality, malformed"
GUIDANCE_SCALE=16.5
HEIGHT=688
WIDTH=512
NUM_INFERENCE_STEPS=50
NUM_IMAGES=1
SEED=57857

# Make the API call and save the response as a zip file
curl -X POST -H "Content-Type: application/json" -d "{
    \"model_path\": \"$MODEL_PATH\",
    \"model_scheduler\": \"$MODEL_SCHEDULER\",
    \"prompt\": {
        \"positive\": \"$POSITIVE_PROMPT\",
        \"negative\": \"$NEGATIVE_PROMPT\",
        \"guidance_scale\": $GUIDANCE_SCALE
    },
    \"height\": $HEIGHT,
    \"width\": $WIDTH,
    \"num_inference_steps\": $NUM_INFERENCE_STEPS,
    \"num_images\": $NUM_IMAGES,
    \"seed\": $SEED
}" "$HOST$ENDPOINT" --output images.zip

# Extract the zip file
mkdir -p images
unzip -o images.zip -d images
rm images.zip
