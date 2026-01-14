"""
Lightweight Enhanced Super Resolution CNN model loader
"""
import math
import torch
import torch.nn as nn

MODEL = './models/lesrcnn_epoch100.pth'

class IEEB(nn.Module):
    def __init__(self, feat_ch=64, num_layers=6):
        super().__init__()
        layers = []
        for i in range(num_layers):
            k = 3 if i % 2 == 0 else 1
            layers += [
                nn.Conv2d(feat_ch, feat_ch, kernel_size=k, padding=(k // 2)),
                nn.ReLU(inplace=True)
            ]
        self.body = nn.Sequential(*layers)
        self.conv_out = nn.Conv2d(feat_ch, feat_ch, 3, 1, 1)

    def forward(self, x):
        out = self.body(x)
        out = self.conv_out(out)
        return x + 0.1 * out

class RB(nn.Module):
    def __init__(self, feat_ch=64):
        super().__init__()
        self.conv1 = nn.Conv2d(feat_ch, feat_ch, 3, 1, 1)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(feat_ch, feat_ch, 3, 1, 1)

    def forward(self, x):
        out = self.relu(self.conv1(x))
        out = self.conv2(out)
        return x + 0.1 * out

class IRB(nn.Module):
    def __init__(self, feat_ch=64, out_ch=3):
        super().__init__()
        body = []
        for _ in range(4):
            body += [nn.Conv2d(feat_ch, feat_ch, 3, 1, 1), nn.ReLU(inplace=True)]
        self.body = nn.Sequential(*body)
        self.conv_last = nn.Conv2d(feat_ch, out_ch, 3, 1, 1)

    def forward(self, x):
        out = self.body(x)
        return self.conv_last(out)


class LESRCNN(nn.Module):
    def __init__(self, in_ch=3, feat_ch=64, num_ieeb_layers=6, scale=2):
        super().__init__()
        assert (scale & (scale - 1)) == 0, "Scale must be a power of 2"
        self.conv_in = nn.Conv2d(in_ch, feat_ch, 3, 1, 1)
        self.relu = nn.ReLU(inplace=True)
        self.ieeb = IEEB(feat_ch, num_layers=num_ieeb_layers)
        self.rb = RB(feat_ch)

        n_up = int(math.log2(scale))
        up_layers = []
        for _ in range(n_up):
            up_layers += [
                nn.Conv2d(feat_ch, feat_ch * 4, 3, 1, 1),
                nn.PixelShuffle(2),
                nn.ReLU(inplace=True)
            ]
        self.upsample = nn.Sequential(*up_layers)
        self.irb = IRB(feat_ch, out_ch=in_ch)

    def forward(self, x):
        x0 = self.relu(self.conv_in(x))
        fi = self.ieeb(x0)
        fr = self.rb(fi)
        fu = self.upsample(fr)
        return self.irb(fu)


def load():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LESRCNN(scale=2).to(device)
    model.load_state_dict(torch.load(MODEL, map_location=device))
    model.eval()
    return model
    