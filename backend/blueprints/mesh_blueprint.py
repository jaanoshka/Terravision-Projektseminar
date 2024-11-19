from flask import current_app, Blueprint, make_response, send_file
from blueprints.image_blueprint import get_satellite_image_as_pil, predict_depth_anything, predict_unet_baseline, predict_zoe_depth
from urllib.parse import unquote
from werkzeug.utils import secure_filename
import open3d as o3d
import numpy as np
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive rendering
import matplotlib.pyplot as plt
from PIL import Image

mesh_bp = Blueprint('mesh_bp', __name__)



@mesh_bp.route('/mesh/ply/<string:address>/<string:model>', methods=['GET'])
def get_ply(address, model):
        decoded_address = unquote(address)
        #load images
        da_images = os.path.join(current_app.root_path, 'media/depth_anything/images')
        unet_images = os.path.join(current_app.root_path, 'media/unet_baseline/images')
        zoe_images = os.path.join(current_app.root_path, 'media/zoe_depth/images')
        #load meshes
        da_meshes = os.path.join(current_app.root_path, 'media/depth_anything/meshes')
        unet_meshes = os.path.join(current_app.root_path, 'media/unet_baseline/meshes')
        zoe_meshes = os.path.join(current_app.root_path, 'media/zoe_depth/meshes')
        #load depths
        da_depths = os.path.join(current_app.root_path, 'media/depth_anything/depths')
        unet_depths = os.path.join(current_app.root_path, 'media/unet_baseline/depths')
        zoe_depths = os.path.join(current_app.root_path, 'media/zoe_depth/depths')
        #filenames
        np_depth_filename = secure_filename(f"{decoded_address.replace(' ', '_')}_depth.npy")
        mesh_filename = secure_filename(f"{decoded_address.replace(' ', '_')}_mesh.ply")
        image_filename = secure_filename(f"{decoded_address.replace(' ', '_')}_image.jpg")
        #mesh paths
        da_mesh_path = os.path.join(da_meshes, mesh_filename)
        unet_mesh_path = os.path.join(unet_meshes, mesh_filename)
        zoe_mesh_path = os.path.join(zoe_meshes, mesh_filename)
        #depth map paths
        da_np_depth_path = os.path.join(da_depths, np_depth_filename)
        unet_np_depth_path = os.path.join(unet_depths, np_depth_filename)
        zoe_np_depth_path = os.path.join(zoe_depths, np_depth_filename)
        #images paths
        da_image_path = os.path.join(da_images, image_filename)
        unet_image_path = os.path.join(unet_images, image_filename)
        zoe_image_path = os.path.join(zoe_images, image_filename)

        if model == 'Depth Anything V2':
            if not os.path.exists(da_mesh_path):
                mesh = generate_pointcloud_with_lat_lon(da_image_path, da_np_depth_path)
                o3d.io.write_triangle_mesh(da_mesh_path, mesh)
            return make_response(send_file(da_mesh_path,mimetype="image/jpeg"))
        elif model == 'Unet Baseline':
            if not os.path.exists(unet_mesh_path):
                mesh = generate_pointcloud_with_lat_lon(unet_image_path, unet_np_depth_path)
                o3d.io.write_triangle_mesh(unet_mesh_path, mesh)
            return make_response(send_file(unet_mesh_path,mimetype="image/jpeg"))
        elif model == 'Zoe Depth':
            if not os.path.exists(zoe_mesh_path):
                mesh = generate_pointcloud_with_lat_lon(zoe_image_path, zoe_np_depth_path)
                o3d.io.write_triangle_mesh(zoe_mesh_path, mesh)
            return make_response(send_file(zoe_mesh_path,mimetype="image/jpeg"))



@mesh_bp.route('/mesh/depth/<string:address>/<string:model>', methods=['GET'])
def get_depth(address, model):
        da_depths = os.path.join(current_app.root_path, 'media/depth_anything/depths')
        unet_depths = os.path.join(current_app.root_path, 'media/unet_baseline/depths')
        zoe_depths = os.path.join(current_app.root_path, 'media/zoe_depth/depths')

        decoded_address = unquote(address)
        depth_filename = secure_filename(f"{decoded_address.replace(' ', '_')}_depth.jpg")
        da_depth_path = os.path.join(da_depths, depth_filename)
        unet_depth_path = os.path.join(unet_depths, depth_filename)
        zoe_depth_path = os.path.join(zoe_depths, depth_filename)

        if model == 'Depth Anything V2':
            if os.path.exists(da_depth_path):
                return make_response(send_file(da_depth_path,mimetype="image/jpeg"))
            else:
                depth = predict_depth_anything(decoded_address)
                fig, ax = plt.subplots(figsize=(6, 8))
                cax = ax.imshow(depth.squeeze(), cmap='inferno')
                ax.set_title('Depth Map', fontsize=16, pad=20)
                ax.axis('off')
                cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, aspect=40)
                cbar.set_label('Depth Value', rotation=270, labelpad=15)  
                cbar.ax.tick_params(labelsize=12) 
                fig.savefig(da_depth_path, format='jpg', bbox_inches='tight')
                plt.close(fig)
                return make_response(send_file(da_depth_path,mimetype="image/jpeg"))
        elif model == 'Unet Baseline':
            if os.path.exists(unet_depth_path):
                return make_response(send_file(unet_depth_path,mimetype="image/jpeg"))
            else:
                depth = predict_unet_baseline(decoded_address)
                fig, ax = plt.subplots(figsize=(6, 8))
                cax = ax.imshow(depth.squeeze(), cmap='inferno')
                ax.set_title('Depth Map', fontsize=16, pad=20)
                ax.axis('off')
                cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, aspect=40)
                cbar.set_label('Depth Value', rotation=270, labelpad=15)  
                cbar.ax.tick_params(labelsize=12) 
                fig.savefig(unet_depth_path, format='jpg', bbox_inches='tight')
                plt.close(fig)
                return make_response(send_file(unet_depth_path,mimetype="image/jpeg"))
        elif model == 'Zoe Depth':
            if os.path.exists(zoe_depth_path):
                return make_response(send_file(zoe_depth_path,mimetype="image/jpeg"))
            else:
                depth = predict_zoe_depth(decoded_address)
                fig, ax = plt.subplots(figsize=(6, 8))
                cax = ax.imshow(depth.squeeze(), cmap='inferno')
                ax.set_title('Depth Map', fontsize=16, pad=20)
                ax.axis('off')
                cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, aspect=40)
                cbar.set_label('Depth Value', rotation=270, labelpad=15)  
                cbar.ax.tick_params(labelsize=12) 
                fig.savefig(zoe_depth_path, format='jpg', bbox_inches='tight')
                plt.close(fig)
                return make_response(send_file(zoe_depth_path,mimetype="image/jpeg"))




########################### UTILITY METHODS - MESH #############################
    
def generate_pointcloud_with_lat_lon(image, depth):
        image_pil = Image.open(image)
        depth_np = np.load(depth)
        image_np = np.asarray(image_pil)
        df = get_rgbd_data_csv_format(depth_np, image_np)

        points = df[['x', 'y', 'z']].to_numpy()
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)

        if 'r' in df.columns and 'g' in df.columns and 'b' in df.columns:
            colors = df[['r', 'g', 'b']].to_numpy()
            point_cloud.colors = o3d.utility.Vector3dVector(colors)

        point_cloud.normals = o3d.utility.Vector3dVector(np.zeros((len(points), 3)))  
        point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        if point_cloud is not None:
            point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
            poisson_mesh = create_poisson_mesh(point_cloud, depth=11)
        
        return poisson_mesh
   

def get_rgbd_data_csv_format(depth, image):
    height, width = depth.shape
    xx, yy = np.meshgrid(np.arange(width, dtype=float), np.arange(height, dtype=float))
    z = depth.flatten()

    r, g, b = image.reshape(-1, 3).T / 255.0

    r_scaled = r.astype(np.float32)
    g_scaled = g.astype(np.float32)
    b_scaled = b.astype(np.float32)
    z_scaled = z.astype(np.float32)

    data = pd.DataFrame({
        'x': xx.flatten(),
        'y': yy.flatten(),
        'z': z_scaled,
        'r': r_scaled,
        'g': g_scaled,
        'b': b_scaled
    })
    return data

def create_poisson_mesh(pcd, depth=11):
    print("Starte Poisson-Mesherstellung...")
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=depth, width=0, scale=1.1, linear_fit=False)[0]
    return poisson_mesh
