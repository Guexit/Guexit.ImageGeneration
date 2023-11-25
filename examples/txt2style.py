import argparse
import io
import zipfile

from image_generation.utils import call_image_generation_api


def extract_zip_images(response, style):
    # Extract zip images
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(f"images/{style}/")


if __name__ == "__main__":
    # Text to style input args
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", type=str, default="general")
    parser.add_argument("--num_images", type=int, default=3)
    args = parser.parse_args()

    # Call Image Generation API
    response = call_image_generation_api(
        host="http://127.0.0.1:5000",
        endpoint="/text_to_style",
        request_object={
            "style": args.style,
            "num_images": args.num_images,
        },
    )

    # Save images
    extract_zip_images(response, args.style)
