import torch
from torchvision import transforms
from torchvision.transforms import ToPILImage
from torchvision.utils import save_image

def upscale(image, model):
  device = "cuda" if torch.cuda.is_available() else "cpu"

  # Load LR image
  lr_image = image.convert("RGB")
  to_tensor = transforms.ToTensor()
  lr_tensor = to_tensor(lr_image).unsqueeze(0).to(device)

  # Super-resolve
  with torch.no_grad():
      sr_tensor = model(lr_tensor)
      sr_tensor = torch.clamp(sr_tensor, 0, 1)

  # Convert tensor to PIL image
  to_pil = ToPILImage()
  pil_image = to_pil(sr_tensor.squeeze(0))

  return pil_image