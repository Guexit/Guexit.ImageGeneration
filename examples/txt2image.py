import requests
import json


# Call Image Generation API
def call_image_generation_api(request_object: dict):
    # Call Image Generation API
    response = requests.post("http://127.0.0.1:5000/text_to_image", json=request_object)
    # Check if the request was successful
    if response.status_code == 200:
        # Get the response
        response_object = json.loads(response.content)
        # Return the response
        return response_object
    else:
        raise Exception(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    import argparse

    # Text to image input args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path", type=str, default="stabilityai/stable-diffusion-2-1-base"
    )
    parser.add_argument("--prompt", type=str, default="portrait of an alien astronaut")
    parser.add_argument("--guidance_scale", type=float, default=7.5)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    parser.add_argument("--num_images_per_prompt", type=int, default=1)
    args = parser.parse_args()
    # Call Image Generation API
    response_object = call_image_generation_api(
        {
            "model_path": args.model_path,
            "prompt": args.prompt,
            "guidance_scale": args.guidance_scale,
            "height": args.height,
            "width": args.width,
            "num_inference_steps": args.num_inference_steps,
            "num_images_per_prompt": args.num_images_per_prompt,
            "return_images": True,
            "upload_images": False,
        }
    )
    # Save images
    for image in response_object["images"]:
        with open(f"{args.prompt}.png", "wb") as f:
            f.write(image)
