from flask import current_app, Blueprint, make_response, send_file, jsonify
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from torchvision import transforms
import segmentation_models_pytorch as smp
import googlemaps
import osmnx as ox
import numpy as np
import requests
from PIL import Image
import io
import os
import torch
from rasterio.features import rasterize
from shapely.geometry import box


image_bp = Blueprint('image_bp', __name__)
gmaps = googlemaps.Client(key='AIzaSyCEXjMi2OrxvBQNgU8NVxw5GSbSWZUTLmM')

image_processor = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Base-hf")
depth_anything = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Base-hf")
depth_anything.load_state_dict(torch.load("./depth_anything_16k_mix_batch_40_lr_0.0005_epoch_9.pth", weights_only=True, map_location=torch.device('cpu')))
depth_anything.eval()

unet_baseline = smp.Unet(encoder_name="resnet34", encoder_weights=None, in_channels=3, classes=1)
unet_baseline.load_state_dict(torch.load('./model_epoch_{epoch+1}.pth', weights_only=True, map_location=torch.device('cpu'))) 
unet_baseline.eval()


@image_bp.route('/mesh/image/<string:address>', methods=['GET'])
def show_image(address):
    try:
        decoded_address = unquote(address)
        media = os.path.join(current_app.root_path, 'media')
        images = os.path.join(media, 'depth_anything/images')
        image_filename = secure_filename(f"{decoded_address.replace(' ', '_')}_image.jpg")
        image_path = os.path.join(images, image_filename)

        if os.path.exists(image_path):
            return make_response(send_file(image_path,mimetype="image/jpeg"))
        else:
            image = get_satellite_image_as_pil(decoded_address) 
            image.save(image_path, format="JPEG")
            return make_response(send_file(image_path,mimetype="image/jpeg"))
    except Exception as e:
        return {"error": str(e)}, 500
    
    

@image_bp.route('/image/volume/<string:address>/<string:model>', methods=['GET'])
def calculate_volume(address, model):

        if model == 'Depth Anything V2':
            image_height, image_width = 518, 518
            depth = predict_depth_anything(address)
        elif model == 'Unet Baseline':
            image_height, image_width = 544, 544
            depth = predict_unet_baseline(address)
        elif model == 'Zoe Depth':
            image_height, image_width = 518, 518 
            depth = predict_zoe_depth(address)

        decoded_address = unquote(address)
        depth = np.asarray(depth)

        geocode_result = gmaps.geocode(decoded_address)
        location = geocode_result[0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
        volume, building_area = get_volume(depth, latitude, longitude, image_width, image_height)

        return make_response({"total_volume": float(volume),
                              "total_area": float(building_area)}), 200



def get_satellite_image_as_pil(address):
        # Paths for images based on models
        da_images = os.path.join(current_app.root_path, 'media/depth_anything/images')
        unet_images = os.path.join(current_app.root_path, 'media/unet_baseline/images')
        zoe_images = os.path.join(current_app.root_path, 'media/zoe_depth/images')

        # Filename
        image_filename = secure_filename(f"{address.replace(' ', '_')}_image.jpg")

        # Get geolocation and zoom level
        geocode_result = gmaps.geocode(address)
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        zoom_level = 18
        watermark_pixels = 19

        # Sizes and paths for all desired models
        sizes_and_paths = [
            (518, os.path.join(da_images, image_filename)),
            (544, os.path.join(unet_images, image_filename)),
            (518, os.path.join(zoe_images, image_filename)),
        ]

        # Fetch and save images for all desired sizes
        for desired_final_size, image_path in sizes_and_paths:
            if os.path.exists(image_path):
                continue  # Skip if already exists

            # API parameters
            api_height = desired_final_size + watermark_pixels
            api_width = desired_final_size
            static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom_level}&size={api_width}x{api_height}&maptype=satellite&key=AIzaSyCEXjMi2OrxvBQNgU8NVxw5GSbSWZUTLmM"

            response = requests.get(static_map_url)
            if response.status_code != 200:
                raise ValueError("Failed to fetch satellite image")

            # Process the image
            image_bytes = io.BytesIO(response.content)
            image = Image.open(image_bytes)
            width, height = image.size
            cropped_image = image.crop((0, 0, width, height - watermark_pixels))

            if cropped_image.mode != 'RGB':
                cropped_image = cropped_image.convert('RGB')

            cropped_image = cropped_image.resize((desired_final_size, desired_final_size))
            cropped_image.save(image_path, format="JPEG")  # Save image

        return Image.open(os.path.join(da_images, image_filename))



def calculate_bounding_box_from_zoom(lat, lng, image_width, image_height):
    # Calculate meters/pixel (zoom level 18)
    resolution = 0.597
    width_meters = image_width * resolution
    height_meters = image_height * resolution

    # Convert meters to degrees
    lat_offset = (height_meters / 2) / 111320  # Latitude degrees per meter
    lng_offset = (width_meters / 2) / 111320  # Longitude degrees per meter

    # Calculate bounding box
    north = lat + lat_offset
    south = lat - lat_offset
    east = lng + lng_offset
    west = lng - lng_offset

    return north, south, east, west



def get_volume(depth, latitude, longitude, image_width, image_height):
    # Calculate bounding box and resolution
    bbox = calculate_bounding_box_from_zoom(latitude, longitude, image_width, image_height)
    resolution = 0.597
    pixel_area = resolution**2  # Area of each pixel in m²

    # Retrieve building footprints
    gdf = ox.features_from_bbox(bbox=bbox, tags={"building": True})
    grid_size = image_height
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny

    # Ensure square cells
    cell_width = width / grid_size
    cell_height = height / grid_size

    # Create a bounding box geometry for the entire grid
    bbox = box(minx, miny, maxx, maxy)

    # Step 3: Filter buildings within the bounding box (in case gdf is larger)
    gdf = gdf[gdf.intersects(bbox)]
    transform = [
        cell_width, 0, minx,
        0, -cell_height, maxy
    ]
    shapes = [(geom, 1) for geom in gdf.geometry if geom.is_valid]
    raster = rasterize(
        shapes=shapes,
        out_shape=(grid_size, grid_size),
        transform=transform,
        fill=0,  # Default value (False)
        dtype=np.uint8
    )
    return np.sum((raster*pixel_area) * depth), np.sum(raster*pixel_area)



def predict_depth_anything(address):
    images = os.path.join(current_app.root_path, 'media/depth_anything/images')
    image_filename = secure_filename(f"{address.replace(' ', '_')}_image.jpg")
    image_path = os.path.join(images, image_filename)
    depths = os.path.join(current_app.root_path, 'media/depth_anything/depths')
    depth_filename = secure_filename(f"{address.replace(' ', '_')}_depth.npy")
    depth_path = os.path.join(depths, depth_filename)
    image = Image.open(image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    common_transform = transforms.Compose([transforms.Resize((518,518)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)

    with torch.no_grad():
            outputs = depth_anything(pixel_values=image)
            predicted_depth = outputs.predicted_depth.unsqueeze(1) 
    
    if os.path.exists(depth_path):
         return predicted_depth
    else: 
        np.save(depth_path, predicted_depth.squeeze().numpy())
        return predicted_depth
        


def predict_unet_baseline(address):
    ub_images = os.path.join(current_app.root_path, 'media/unet_baseline/images')
    image_filename = secure_filename(f"{address.replace(' ', '_')}_image.jpg")
    image_path = os.path.join(ub_images, image_filename)
    depths = os.path.join(current_app.root_path, 'media/unet_baseline/depths')
    depth_filename = secure_filename(f"{address.replace(' ', '_')}_depth.npy")
    depth_path = os.path.join(depths, depth_filename)
    image = Image.open(image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    common_transform = transforms.Compose([transforms.Resize((544,544)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)
    
    with torch.no_grad():
        outputs = unet_baseline(image)
        predicted_depth = outputs 
        
    if os.path.exists(depth_path):
         return predicted_depth
    else: 
        np.save(depth_path, predicted_depth.squeeze().numpy())
        return predicted_depth



def predict_zoe_depth(address):
    images = os.path.join(current_app.root_path, 'media/zoe_depth/images')
    image_filename = secure_filename(f"{address.replace(' ', '_')}_image.jpg")
    image_path = os.path.join(images, image_filename)
    depths = os.path.join(f'{current_app.root_path}/media/zoe_depth/depths')
    depth_filename = secure_filename(f"{address.replace(' ', '_')}_depth.npy")
    depth_path = os.path.join(depths, depth_filename)
    image = Image.open(image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    common_transform = transforms.Compose([transforms.Resize((518,518)), transforms.ToTensor()])
    image = common_transform(image)
    image = image.unsqueeze(0)

    with torch.no_grad():
            outputs = depth_anything(pixel_values=image)
            predicted_depth = outputs.predicted_depth.unsqueeze(1) 
        
    if os.path.exists(depth_path):
         return predicted_depth
    else: 
        np.save(depth_path, predicted_depth.squeeze().numpy())
        return predicted_depth
