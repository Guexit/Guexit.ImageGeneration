import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

class StableDiffusionHandler:
    def __init__(self, model_path: str, device: torch.device = None):
        
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.pipe = StableDiffusionPipeline.from_pretrained(model_path)
        self.pipe.to(device)

    
