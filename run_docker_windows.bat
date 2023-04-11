@echo off
docker run --gpus all --env-file .env -p 5000:5000 -t -d guexit_image_generation
