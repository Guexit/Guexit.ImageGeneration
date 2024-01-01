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

# Construct the command
CMD="python3 services/image_generation_message_handler.py"

# Add --tags_to_add if TAGS_TO_ADD is set and non-empty
if [ ! -z "$TAGS_TO_ADD" ]; then
    CMD+=" --tags_to_add '$TAGS_TO_ADD'"
fi

# Add --generate_on_command if GENERATE_ON_COMMAND is set to a true-like value
if [ "$GENERATE_ON_COMMAND" = "true" ] || [ "$GENERATE_ON_COMMAND" = "yes" ] || [ "$GENERATE_ON_COMMAND" = "1" ]; then
    CMD+=" --generate_on_command"
fi

CMD+=" --total_images ${TOTAL_IMAGES:-0}"
CMD+=" --batch_size ${BATCH_SIZE:-50}"

# Execute the command
eval $CMD
