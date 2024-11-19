from flask import Blueprint
from blueprints.image_blueprint import get_satellite_image_as_pil
import torch
import numpy as np
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from torchvision import transforms
import segmentation_models_pytorch as smp
import torch


model_bp = Blueprint('model_bp', __name__)

image_processor = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Base-hf")
depth_anything = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Base-hf")
depth_anything.load_state_dict(torch.load("./depth_anything_16k_mix_batch_40_lr_0.0005_epoch_9.pth", weights_only=True, map_location=torch.device('cpu')))
depth_anything.eval()

unet_baseline = smp.Unet(encoder_name="resnet34", encoder_weights=None, in_channels=3, classes=1)
unet_baseline.load_state_dict(torch.load('./model_epoch_{epoch+1}.pth', weights_only=True, map_location=torch.device('cpu'))) 
unet_baseline.eval()


def predict_depth_anything(address):
    model = 'Depth Anything V2'
    print(address)
    image = get_satellite_image_as_pil(address, model)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    print(image.size)
    common_transform = transforms.Compose([transforms.Resize((518,518)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)
    print(image.shape)

    with torch.no_grad():
            outputs = depth_anything(pixel_values=image)
            predicted_depth = outputs.predicted_depth.unsqueeze(1) 
        
    return predicted_depth



def predict_unet_baseline(address):
    model = 'Unet Baseline'
    image = get_satellite_image_as_pil(address, model)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    print(image.size)
    common_transform = transforms.Compose([transforms.Resize((544,544)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)
    print(image.shape)
    
    with torch.no_grad():
        outputs = unet_baseline(image)
        predicted_depth = outputs
        if len(predicted_depth.shape) == 3:               
            predicted_depth = predicted_depth.unsqueeze(1)
        
    return predicted_depth



def predict_zoe_depth(address):
    model = 'Zoe Depth'
    image = get_satellite_image_as_pil(address, model)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    print(image.size)
    common_transform = transforms.Compose([transforms.Resize((518,518)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)
    print(image.shape)

    with torch.no_grad():
            outputs = depth_anything(pixel_values=image)
            predicted_depth = outputs.predicted_depth.unsqueeze(1) 
        
    return predicted_depth
