@echo off
docker build . --secret id=git-credentials,src=%USERPROFILE%/.git-credentials -t guexit_image_generation
