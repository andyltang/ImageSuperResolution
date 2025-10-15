import numpy as np
import math
import cv2

IMAGE1 = './sample_epoch90.png'
IMAGE2 = './sample_epoch100.png'

def psnr(img1, img2):
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')  # identical images
    PIXEL_MAX = 255.0
    psnr = 10 * math.log10((PIXEL_MAX ** 2) / mse)
    return psnr


original = cv2.imread(f'./checkpoints/{IMAGE1}')
upscaled = cv2.imread(f'./checkpoints/{IMAGE2}')
psnr_value = psnr(original, upscaled)
print("PSNR:", psnr_value)
