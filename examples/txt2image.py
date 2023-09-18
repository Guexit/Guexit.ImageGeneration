import io
import zipfile

from image_generation.utils import call_image_generation_api


def extract_zip_images(response):
    # Extract zip images
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall("images/")


if __name__ == "__main__":
    import argparse

    # Text to image input args
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="digiplay/Juggernaut_final")
    parser.add_argument("--model_scheduler", type=str, default="euler_a")
    parser.add_argument(
        "--positive_prompt",
        type=str,
        default="portrait of samantha prince set in fire, cinematic lighting, photorealistic, ornate, intricate, realistic, detailed, volumetric light and shadow, hyper HD, octane render, unreal engine insanely detailed and intricate, hypermaximalist, elegant, ornate, hyper-realistic, super detailed",
    )
    parser.add_argument(
        "--negative_prompt",
        type=str,
        default="bad quality, malformed",
    )
    parser.add_argument("--guidance_scale", type=float, default=10)
    parser.add_argument("--height", type=int, default=688)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    parser.add_argument("--num_images", type=int, default=1)
    parser.add_argument("--seed", type=int, default=57857)
    args = parser.parse_args()
    # Call Image Generation API
    response = call_image_generation_api(
        host="http://127.0.0.1:5000",
        endpoint="/text_to_image",
        request_object={
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
        },
    )
    # Save images
    extract_zip_images(response)
