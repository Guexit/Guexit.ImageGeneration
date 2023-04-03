#!/bin/bash
export $(grep -v '^#' .env | xargs)
python3 services/image_generation_message_handler.py
