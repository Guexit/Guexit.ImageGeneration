@echo off

rem API settings
set HOST=http://127.0.0.1:5000
set ENDPOINT=/text_to_image

rem Text to image settings
set MODEL_PATH=prompthero/openjourney-v4
set MODEL_SCHEDULER=euler_a
set POSITIVE_PROMPT=portrait of samantha prince set in fire^, cinematic lighting^, photorealistic^, ornate^, intricate^, realistic^, detailed^, volumetric light and shadow^, hyper HD^, octane render^, unreal engine insanely detailed and intricate^, hypermaximalist^, elegant^, ornate^, hyper-realistic^, super detailed
set NEGATIVE_PROMPT=bad quality^, malformed
set GUIDANCE_SCALE=16.5
set HEIGHT=688
set WIDTH=512
set NUM_INFERENCE_STEPS=50
set NUM_IMAGES=1
set SEED=57857

rem Make the API call and save the response as a zip file
curl --max-time 600 -X POST -H "Content-Type: application/json" -d "{ \"model_path\": \"%MODEL_PATH%\", \"model_scheduler\": \"%MODEL_SCHEDULER%\", \"prompt\": { \"positive\": \"%POSITIVE_PROMPT%\", \"negative\": \"%NEGATIVE_PROMPT%\", \"guidance_scale\": %GUIDANCE_SCALE% }, \"height\": %HEIGHT%, \"width\": %WIDTH%, \"num_inference_steps\": %NUM_INFERENCE_STEPS%, \"num_images\": %NUM_IMAGES%, \"seed\": %SEED% }" "%HOST%%ENDPOINT%" --output images.zip

rem Extract the zip file
if not exist "images" mkdir "images"
tar -xf images.zip --directory images
del images.zip
