"""
Takes a Low Resolution image and upscales it using a pre-trained CNN model
"""
import os
import torch
from torchvision import transforms
from torchvision.transforms import ToPILImage
from torchvision.utils import save_image

torch.set_num_threads(int(os.getenv("TORCH_NUM_THREADS", "1")))
torch.set_num_interop_threads(1)

def upscale(image, model):
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

  # Load LR image
  print('Loading image')
  lr_image = image.convert("RGB")
  to_tensor = transforms.ToTensor()
  lr_tensor = to_tensor(lr_image).unsqueeze(0).to(device)

  # Upscale
  print('Running inference')
  with torch.no_grad():
      sr_tensor = model(lr_tensor)
      sr_tensor = torch.clamp(sr_tensor, 0, 1)

  # Convert tensor to PIL image
  print('Converting to image')
  to_pil = ToPILImage()
  pil_image = to_pil(sr_tensor.squeeze(0))

  print('Complete!')
  return pil_image