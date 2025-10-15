# check if torch can see your GPU
import torch
print(f'Cuda Version: {torch.version.cuda}')
print(f'Cuda Available: {torch.cuda.is_available()}')
print(f'Device Name: {torch.cuda.get_device_name(0)}')