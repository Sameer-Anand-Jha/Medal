
import time
import torch.nn as nn
#import torch.nn.functional as F
from torch.utils.data import DataLoader
# from torch.utils.data import Dataset
import torch, math
import torch.fft
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
# !pip install vit-pytorch
import pandas as pd
import time
import torch.nn.functional as F
import pywt
from torch.autograd import Function
from torch.utils.data import DataLoader
# from torch.utils.data import Dataset
import torch.optim as optim
# !pip install torchsummary
from torchsummary import summary
# !pip install einops
from math import ceil
import os
import copy
import torchvision.models as models
from torch import nn, einsum
from einops import rearrange, repeat
from einops.layers.torch import Rearrange
import warnings
warnings.filterwarnings("ignore")
# helpers
from einops import reduce

from patch_loader_inference import Patchdataset
from tqdm import tqdm
# from FNET_model import FNet2D
import tensorboard
import torch
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter()
torch.cuda.empty_cache()

transform = transforms.Compose([transforms.ToTensor()]) #transforms.Resize([256, 256]), 


batch_size = 256
path='/workspace/hnsc_for_tumor/tum_ntum/wflt_tissue_coord_csv_396_slide/TCGA-CQ-5329-01Z-00-DX1.csv'
slide_id=path.split('/')[-1].split('.')[0]

val_dataset = Patchdataset(path='/workspace/hnsc_for_tumor/tum_ntum/wflt_tissue_coord_csv_396_slide/TCGA-CQ-5329-01Z-00-DX1.csv' ,transforms=transform)


testloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=False)

device = torch.device("cuda:2" if torch.cuda.is_available() else "cpu")

# model = models.mobilenet_v2(pretrained=True)  # Load a pre-trained MobileNet

# model = models.resnet34(pretrained=True)
###################################### modified model ########################
import torch.nn as nn
import torchvision.models as models

class ModifiedResNet34(nn.Module):
    def __init__(self, num_classes=2):
        super(ModifiedResNet34, self).__init__()
        self.model = models.resnet34(pretrained=True)
        self.model.fc = nn.Sequential(
            nn.Dropout(p=0.6),
            nn.Linear(self.model.fc.in_features, num_classes)
        )

    def forward(self, x):
        return self.model(x)

model = ModifiedResNet34(num_classes=2).to(device)
##############################################################################
# print(model)
model_path='/workspace/hnsc_for_tumor/tum_ntum/tum_ntum1/model_wt/Resnet34/modified_res34_cn_cj_17_wc_june/Resnet34_best_val_0.8228_iteration_4_20.pth'
epoch_itr=model_path.split('/')[-1].split('.')[1].split('_')[-4]+'_'+model_path.split('/')[-1].split('.')[1].split('_')[-2]+'_'+model_path.split('/')[-1].split('.')[1].split('_')[-1]
print(epoch_itr)
# model.classifier[1] = torch.nn.Linear(model.last_channel, 2)
model.fc = nn.Linear(in_features=512, out_features=2, bias=True)
model.load_state_dict(torch.load(model_path),strict=False)
model.to(device)

criterion = nn.CrossEntropyLoss()
scaler = torch.cuda.amp.GradScaler()


optimizer = optim.AdamW(model.parameters(), lr=3e-4, betas=(0.9, 0.999), eps=1e-08, weight_decay=0.01, amsgrad=False)
results = []  # Prepare to collect batch results

for epoch in range(1):  # Loop over the dataset multiple times
    t0 = time.time()
    running_corrects = 0
    running_loss = 0.0
    
    for data in tqdm(testloader):
        images, x, y = data[0], data[1].cpu().numpy(), data[2].cpu().numpy()
        with torch.no_grad():
            outputs = model(images.to(device))
            s_out = F.softmax(outputs, dim=1)
            preds = torch.argmax(s_out, dim=1).cpu().numpy()
            
            # Collect batch results
            for i in range(images.size(0)):
                probs = s_out[i].cpu().tolist()
                prob=probs[0]
                label_=preds[i]
                if label_==0:

                    results.append({
                        'dim1': x[i],
                        'dim2': y[i],
                        'Softmax': s_out[i].cpu().tolist(),
                        'label': label_,
                        'probability':prob
                    })

# Convert collected results to DataFrame
df = pd.DataFrame(results)

print('Finished Testing')
# df.to_csv('inference_result.csv', index=False)
# df.to_csv(f'./inference/inference_csv/resnet18_wts_24ap/{slide_id}_inference_resnet18_{epoch_itr}.csv', index=False)
df.to_csv(f'./inference/inference_csv/Resnet34/modified_res34_cn_cj_17_wc_june/{slide_id}_res18_{epoch_itr}.csv', index=False)


