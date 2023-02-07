import torch
from diffusers import StableDiffusionPipeline


class StableDiffusionHandler:
    def __init__(self, model_path: str, device: torch.device = None):
        if device is None:
            if torch.backends.mps.is_available():
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")
            else:
                device = torch.device("cpu")
        self.device = device
        self.pipe = StableDiffusionPipeline.from_pretrained(model_path)
        self.pipe.to(self.device)
        # Recommended if computer has < 64 GB of RAM
        self.pipe.enable_attention_slicing()
        # Warm up the model
        self.pipe("", num_inference_steps=1)

    def txt2img(self, input_data):
        prompt = input_data["prompt"]
        guidance_scale = input_data.get("guidance_scale", 7.5)
        height = input_data.get("height", 512)
        width = input_data.get("width", 512)
        num_inference_steps = input_data.get("num_inference_steps", 50)
        images = self.pipe(
            prompt=prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
        ).images
        image = images[0]
        return image


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--prompt", type=str, default="portrait of an alien astronaut")
    parser.add_argument("--guidance_scale", type=float, default=7.5)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    args = parser.parse_args()

    model = StableDiffusionHandler(args.model_path)
    image = model.txt2img(
        {
            "prompt": args.prompt,
            "guidance_scale": args.guidance_scale,
            "height": args.height,
            "width": args.width,
            "num_inference_steps": args.num_inference_steps,
        }
    )
    # Save image
    image.save("output.png")
