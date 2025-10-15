from PIL import Image
import os
import torch
from torchvision import transforms
from torchvision.utils import save_image
from lesrcnn import LESRCNN

MODEL = './checkpoints/lesrcnn_epoch100.pth'
IMAGE_EXT = '.png'
IMAGE_PATH = './images/inference/'
OUTPUT_PATH = './images/output/'

IMAGE_FILENAME = 'test3' + IMAGE_EXT
OUTPUT_FILENAME = 'upscaled2x' + IMAGE_EXT

device = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(OUTPUT_PATH, exist_ok=True)

print("Generating super resolved image...")

# Load model
model = LESRCNN(scale=2).to(device)
model.load_state_dict(torch.load(MODEL, map_location=device))
model.eval()

# Load LR image
lr_image = Image.open(os.path.join(IMAGE_PATH, IMAGE_FILENAME)).convert("RGB")
to_tensor = transforms.ToTensor()
lr_tensor = to_tensor(lr_image).unsqueeze(0).to(device)

# Super-resolve
with torch.no_grad():
    sr_tensor = model(lr_tensor)
    sr_tensor = torch.clamp(sr_tensor, 0, 1)

# Save output
save_image(sr_tensor, os.path.join(OUTPUT_PATH, OUTPUT_FILENAME))
print(f"Saved super-resolved image to {os.path.join(OUTPUT_PATH, OUTPUT_FILENAME)}!")
