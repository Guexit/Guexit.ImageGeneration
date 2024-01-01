#!/bin/bash

# Function to check if an environment variable is already set
is_var_set() {
    [ ! -z "${!1}" ]
}

# Load environment variables from .env file if it exists and the variable is not already set
if [ -f .env ]; then
    while IFS='=' read -r key value
    do
        # Remove leading and trailing spaces from key and value
        key=$(echo $key | xargs)
        value=$(echo $value | xargs)

        # Skip if key is empty
        if [ -z "$key" ]; then
            continue
        fi

        # Export the variable if not already set
        if ! is_var_set "$key"; then
            export "$key=$value"
        fi
    done < .env
fi

python3 -m uvicorn image_generation.api.server:app --host 127.0.0.1 --port 5000 --timeout-keep-alive 600
