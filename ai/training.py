import os
import random
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.utils import save_image
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr

from lesrcnn import LESRCNN

# -----------------------
# Dataset
# -----------------------
class SRDataset(Dataset):
    """
    Super-resolution dataset:
    - Generates LR images on-the-fly from HR images
    - Randomly crops HR patches (training) or full images (validation)
    """
    def __init__(self, hr_dir, scale=2, patch_size=96, training=True):
        self.hr_paths = sorted(Path(hr_dir).glob("*.png"))
        self.scale = scale
        self.patch_size = patch_size
        self.training = training
        self.to_tensor = transforms.ToTensor()

    def __len__(self):
        return len(self.hr_paths)

    def __getitem__(self, idx):
        hr = Image.open(self.hr_paths[idx]).convert("RGB")
        if self.training:
            # random crop HR patch
            w, h = hr.size
            x = random.randint(0, w - self.patch_size * self.scale)
            y = random.randint(0, h - self.patch_size * self.scale)
            hr_patch = hr.crop((x, y, x + self.patch_size * self.scale, y + self.patch_size * self.scale))
            # generate LR patch
            lr_patch = hr_patch.resize((self.patch_size, self.patch_size), Image.BICUBIC)
        else:
            # use full image for validation
            lr_patch = hr.resize((hr.width // self.scale, hr.height // self.scale), Image.BICUBIC)
            hr_patch = hr

        return self.to_tensor(lr_patch), self.to_tensor(hr_patch)

# -----------------------
# PSNR Evaluation
# -----------------------
def evaluate_psnr(model, val_loader, device):
    model.eval()
    total_psnr = 0
    with torch.no_grad():
        for lr, hr in val_loader:
            lr, hr = lr.to(device), hr.to(device)
            sr = model(lr)
            sr = torch.clamp(sr, 0.0, 1.0)
            # convert to numpy for PSNR
            sr_np = sr.permute(0, 2, 3, 1).cpu().numpy()
            hr_np = hr.permute(0, 2, 3, 1).cpu().numpy()
            for s, h in zip(sr_np, hr_np):
                total_psnr += psnr(h, s, data_range=1.0)
    return total_psnr / len(val_loader.dataset)

# -----------------------
# Training
# -----------------------
def train(hr_train_dir, hr_val_dir, scale=2, patch_size=96, batch_size=16, epochs=100, lr=1e-4):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    save_dir = "./checkpoints"
    os.makedirs(save_dir, exist_ok=True)

    # Datasets & Loaders
    train_dataset = SRDataset(hr_train_dir, scale=scale, patch_size=patch_size, training=True)
    val_dataset = SRDataset(hr_val_dir, scale=scale, training=False)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)

    # Model, loss, optimizer
    model = LESRCNN(scale=scale).to(device)
    criterion = nn.L1Loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for i, (lr_patch, hr_patch) in enumerate(train_loader):
            lr_patch, hr_patch = lr_patch.to(device), hr_patch.to(device)
            sr = model(lr_patch)
            loss = criterion(sr, hr_patch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f}")

        # Evaluate PSNR on validation set
        val_psnr = evaluate_psnr(model, val_loader, device)
        print(f"Validation PSNR: {val_psnr:.2f} dB")

        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = os.path.join(save_dir, f"lesrcnn_epoch{epoch+1}.pth")
            torch.save(model.state_dict(), checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")

            # Save a sample image from validation set
            lr_sample, hr_sample = next(iter(val_loader))
            lr_sample = lr_sample.to(device)
            with torch.no_grad():
                sr_sample = model(lr_sample)
            save_image(sr_sample.clamp(0, 1)[:4], os.path.join(save_dir, f"sample_epoch{epoch+1}.png"))

    print("Training completed.")

if __name__ == "__main__":
    train("./images/DIV2K_train_HR", "./images/DIV2K_valid_HR")
