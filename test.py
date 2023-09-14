import copy
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import PySimpleGUI as sui

# Reads .pcd, .ply, .pts, .obj, and .xyz files
# Can be used in either Python or C++

print("Load a ply point cloud, print it, and render it")
sample_ply_data = o3d.data.PLYPointCloud()

layout = [[sui.Text("Hello, world")],
          [sui.Button("This is a button")]]

pcd = o3d.io.read_point_cloud(sample_ply_data.path)
pcd = o3d.io.read_point_cloud("Hotel.ply")
o3d.visualization.draw_geometries([pcd])

# ----- Selection of areas -----
def pick_points(pcd):
  print("[shift + left click] to pick points")
  print("[shift + right click] to undo point")
  print("Q to close window")
  vis = o3d.visualization.VisualizerWithEditing()
  vis.create_window()
  vis.add_geometry(pcd)
  vis.run() # Shows window
  vis.destroy_window()
  print()
  return vis.get_picked_points()

# pick_points(pcd)

# ----- Painting -----
# point_cloud.paint_uniform_color([0-1, 0-1, 0-1]) <-rgb

# ----- Multiple cloud alignment -----
def draw_registration_result(source, target, transformation):
  source_temp = copy.deepcopy(source)
  target_temp = copy.deepcopy(target)
  source_temp.paint_uniform_color([1, 0.706, 0])
  target_temp.paint_uniform_color([0, 0.651, 0.929])
  source_temp.transform(transformation)
  o3d.visualization.draw_geometries([source_temp, target_temp])

def demo_manual_registration():
  print("Demo for manual ICP")
  pcd_data = o3d.data.DemoICPPointClouds()
  source = o3d.io.read_point_cloud(pcd_data.paths[0])
  target = o3d.io.read_point_cloud(pcd_data.paths[2])
  print("Visualization of two point clouds before manual alignment")
  draw_registration_result(source, target, np.identity(4))

  # pick points from two point clouds and builds correspondences
  picked_id_source = pick_points(source)
  picked_id_target = pick_points(target)
  assert (len(picked_id_source) >= 3 and len(picked_id_target) >= 3)
  assert (len(picked_id_source) == len(picked_id_target))
  corr = np.zeros((len(picked_id_source), 2))
  corr[:, 0] = picked_id_source
  corr[:, 1] = picked_id_target

  # estimate rough transformation using correspondences
  print("Compute a rough transform using the correspondences given by user")
  p2p = o3d.pipelines.registration.TransformationEstimationPointToPoint()
  trans_init = p2p.compute_transformation(source, target,
                                          o3d.utility.Vector2iVector(corr))

  # point-to-point ICP for refinement
  print("Perform point-to-point ICP refinement")
  threshold = 0.03  # 3cm distance threshold
  reg_p2p = o3d.pipelines.registration.registration_icp(
    source, target, threshold, trans_init,
    o3d.pipelines.registration.TransformationEstimationPointToPoint())
  draw_registration_result(source, target, reg_p2p.transformation)
  print("")

# demo_manual_registration()

# ----- Bounding boxes -----

 
# with o3d.utility.VerbosityContextManager(
#     o3d.utility.VerbosityLevel.Debug) as cm:
#   labels = np.array(
#     pcd.cluster_dbscan(eps=0.03, min_points=15, print_progress=False))

# max_label = labels.max()
# print(f"point cloud has {max_label + 1} clusters")
# colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
# colors[labels < 0] = 0
# pcd.colors = o3d.utility.Vector3dVector(colors[:, :3])
# o3d.visualization.draw_geometries([pcd])