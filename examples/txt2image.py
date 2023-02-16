import grequests
import zipfile, io


# Call Image Generation API
def call_image_generation_api(request_object: dict):
    # Call Image Generation API
    async_req = grequests.post(
        "http://127.0.0.1:5000/text_to_image", json=request_object
    )
    response = grequests.map([async_req])[0]
    # Check if the request was successful
    if response.status_code == 200:
        # Return the response
        return response
    else:
        raise Exception(f"Request failed with status code {response.status_code}")


def extract_zip_images(response):
    # Extract zip images
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall("images/")


if __name__ == "__main__":
    import argparse

    # Text to image input args
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="prompthero/openjourney-v2")
    parser.add_argument("--model_scheduler", type=str, default=None)
    parser.add_argument(
        "--positive_prompt",
        type=str,
        default="portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed --v 4",
    )
    parser.add_argument(
        "--negative_prompt",
        type=str,
        default="bad quality, malformed",
    )
    parser.add_argument("--guidance_scale", type=float, default=16.5)
    parser.add_argument("--height", type=int, default=688)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    parser.add_argument("--num_images", type=int, default=2)
    parser.add_argument("--seed", type=int, default=57857)
    args = parser.parse_args()
    # Call Image Generation API
    response = call_image_generation_api(
        {
            "text_to_image": {
                "model_path": args.model_path,
                "model_scheduler": args.model_scheduler,
                "prompt": {
                    "positive": args.positive_prompt,
                    "negative": args.negative_prompt,
                    "guidance_scale": args.guidance_scale,
                },
                "height": args.height,
                "width": args.width,
                "num_inference_steps": args.num_inference_steps,
                "num_images": args.num_images,
                "seed": args.seed,
                "return_images": True,
                "upload_images": False,
            }
        }
    )
    # Save images
    extract_zip_images(response)
