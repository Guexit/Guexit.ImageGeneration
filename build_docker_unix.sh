#!/bin/bash
docker build . --secret id=git-credentials,src=$HOME/.git-credentials -t guexit_image_generation
