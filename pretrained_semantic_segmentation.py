# -*- coding: utf-8 -*-
"""pretrained_semantic_segmentation.ipynb

Automatically generated by Colaboratory.

"""

import os
import copy
import time
import random
import numpy as np

import functools

from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as opt
import torch.nn.functional as F
import torch.utils.data as data

import torchvision.models as models
import torchvision.datasets as datasets
import torchvision.transforms as transforms

from matplotlib import pyplot as plt

SEED = 241

def seed_everything(seed):
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  os.environ['PYTHONHASHSEED'] = str(seed)

  if torch.cuda.is_available(): 
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

seed_everything(SEED)

model = models.segmentation.fcn_resnet101(pretrained=True).eval()
print(model)

from PIL import Image

!wget -nv https://static.independent.co.uk/s3fs-public/thumbnails/image/2018/04/10/19/pinyon-jay-bird.jpg -O bird.png
img = Image.open('./bird.png')
plt.imshow(img)

def preprocess(img):
  out_crop = 256
  crop_to = 224
  means = [0.485, 0.456, 0.406]
  stds = [0.229, 0.224, 0.225]

  train_transforms = transforms.Compose([
    transforms.Resize(out_crop),
    transforms.CenterCrop(crop_to),
    transforms.ToTensor(),
    transforms.Normalize(mean=means, std=stds)
  ])

  img = train_transforms(img).unsqueeze(0)
  return img

def predict(mode, img, preprocess):
  img = preprocess(img)
  out = model(img)['out']
  out = out.squeeze(0)
  out = torch.argmax(out, dim=0).detach().cpu().numpy()
  return out

output = predict(model, img, preprocess)

plt.imshow(output)
plt.show()

def decode_image(image, n_channels=21):
  label_colors = np.array([(0, 0, 0),  # 0=background
               # 1=aeroplane, 2=bicycle, 3=bird, 4=boat, 5=bottle
               (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
               # 6=bus, 7=car, 8=cat, 9=chair, 10=cow
               (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
               # 11=dining table, 12=dog, 13=horse, 14=motorbike, 15=person
               (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
               # 16=potted plant, 17=sheep, 18=sofa, 19=train, 20=tv/monitor
               (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)])

  red = np.zeros_like(image).astype(np.uint8)
  green = np.zeros_like(image).astype(np.uint8)
  blue = np.zeros_like(image).astype(np.uint8)

  for c in range(n_channels):
    idx = (image == c)
    red[idx] = label_colors[c, 0]
    green[idx] = label_colors[c, 1]
    blue[idx] = label_colors[c, 2]

  result = np.stack([red, green, blue], axis=-1)
  return result

def segment(model, image):
  output = predict(model, image, preprocess)
  decoded = decode_image(output)
  return decoded

result = segment(model, Image.open('./bird.png'))
plt.imshow(result)
plt.show()

