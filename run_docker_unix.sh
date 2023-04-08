#!/bin/bash
docker run --gpus all --env-file .env -p 5000:5000 guexit_image_generation
