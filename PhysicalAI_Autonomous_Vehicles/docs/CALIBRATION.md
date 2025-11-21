# Calibration Guide

This guide explains how to use calibration data in the PhysicalAI-Autonomous-Vehicles dataset.

## Overview

The dataset provides three types of calibration data:
1. **Camera Intrinsics**: Camera-specific parameters (f-theta model)
2. **Sensor Extrinsics**: 3D pose of each sensor relative to vehicle
3. **Vehicle Dimensions**: Physical dimensions of the vehicle

## Coordinate Systems

### Rig Coordinate Frame

All sensor extrinsics are defined relative to the **rig coordinate frame**:

- **Origin**: Center of the rear axle, projected onto the ground plane
- **X-axis**: Points forward (vehicle's driving direction)
- **Y-axis**: Points left (when facing forward)
- **Z-axis**: Points up (perpendicular to ground)
- **Units**: Meters

```
         Z (up)
         |
         |
         |_____ X (forward)
        /
       /
      Y (left)
```

## Loading Calibration Data

### Basic Setup

```python
from utils import CalibrationLoader

# Initialize loader
calib = CalibrationLoader('/path/to/dataset')
clip_id = 'your-clip-uuid'
```

### Camera Intrinsics

```python
# Load camera intrinsics for a specific clip
camera_intrinsics = calib.load_camera_intrinsics(clip_id)

# Get intrinsics for a specific camera
front_cam = camera_intrinsics[
    camera_intrinsics['camera_name'] == 'camera_front_wide_120fov'
].iloc[0]

print(f"Image size: {front_cam['width']}x{front_cam['height']}")
print(f"Principal point: ({front_cam['cx']}, {front_cam['cy']})")
print(f"Focal length (fw_poly_1): {front_cam['fw_poly_1']}")
```

### Sensor Extrinsics

```python
# Load all sensor extrinsics for a clip
sensor_extrinsics = calib.load_sensor_extrinsics(clip_id)

# Get extrinsics for front camera
front_cam_ext = sensor_extrinsics[
    sensor_extrinsics['sensor_name'] == 'camera_front_wide_120fov'
].iloc[0]

print(f"Position: ({front_cam_ext['x']}, {front_cam_ext['y']}, {front_cam_ext['z']})")
print(f"Rotation (quat): ({front_cam_ext['qx']}, {front_cam_ext['qy']}, "
      f"{front_cam_ext['qz']}, {front_cam_ext['qw']})")
```

### Vehicle Dimensions

```python
# Load vehicle dimensions
vehicle_dims = calib.load_vehicle_dimensions(clip_id)

print(f"Length: {vehicle_dims['length']:.2f} m")
print(f"Width: {vehicle_dims['width']:.2f} m")
print(f"Height: {vehicle_dims['height']:.2f} m")
print(f"Wheelbase: {vehicle_dims['wheelbase']:.2f} m")
```

## Camera Model: F-Theta

The cameras use an **f-theta distortion model**, not the standard pinhole model.

### Forward Projection (3D to 2D)

The forward polynomial maps from incident angle θ to image radius r:

```
r = fw_poly_0 + fw_poly_1 * θ + fw_poly_2 * θ² + fw_poly_3 * θ³ + fw_poly_4 * θ⁴
```

Where:
- `θ = atan(sqrt(x² + y²) / z)` for 3D point (x, y, z) in camera frame
- `r` is distance from principal point in pixels
- `fw_poly_1` approximates the focal length

### Backward Projection (2D to 3D ray)

The backward polynomial maps from image radius r to incident angle θ:

```
θ = bw_poly_0 + bw_poly_1 * r + bw_poly_2 * r² + bw_poly_3 * r³ + bw_poly_4 * r⁴
```

## Common Operations

### 1. Transform Points Between Frames

```python
import numpy as np

# Load LiDAR points (in rig frame)
from utils import LiDARLoader
lidar = LiDARLoader('/path/to/dataset')
points = lidar.load_spin(clip_id, spin_idx=0)

# Get camera extrinsics
camera_ext = sensor_extrinsics[
    sensor_extrinsics['sensor_name'] == 'camera_front_wide_120fov'
].iloc[0]

# Get transformation matrix (rig -> camera)
T_cam = calib.get_transformation_matrix(camera_ext)

# Transform points to camera frame
points_cam = calib.transform_points(points[:, :3], np.linalg.inv(T_cam))
```

### 2. Project LiDAR to Camera

```python
# Load camera intrinsics
camera_int = camera_intrinsics[
    camera_intrinsics['camera_name'] == 'camera_front_wide_120fov'
].iloc[0]

# Project 3D points to 2D
points_2d, valid_mask = calib.project_points_to_camera(
    points[:, :3],  # 3D points in rig frame
    camera_int,
    camera_ext
)

# Filter valid points (in front of camera)
points_2d_valid = points_2d[valid_mask]
points_3d_valid = points[valid_mask]

print(f"Projected {len(points_2d_valid)} points to camera")
```

### 3. Overlay Points on Camera Image

```python
from utils import CameraLoader
import cv2

# Load camera image
camera_loader = CameraLoader('/path/to/dataset')
frames, _ = camera_loader.load_video_from_chunk(clip_id, 'camera_front_wide_120fov')
image = frames[0].copy()

# Project and overlay points
for i, (u, v) in enumerate(points_2d_valid):
    # Check if point is within image bounds
    if 0 <= u < camera_int['width'] and 0 <= v < camera_int['height']:
        # Color by distance
        distance = np.linalg.norm(points_3d_valid[i, :3])
        color = int(255 * (1 - min(distance / 50.0, 1.0)))  # Fade with distance
        cv2.circle(image, (int(u), int(v)), 2, (0, color, 255), -1)

# Display or save
cv2.imwrite('lidar_overlay.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
```

### 4. Multi-Sensor Fusion

```python
from utils import RadarLoader

# Load radar data
radar_loader = RadarLoader('/path/to/dataset')
radar_df = radar_loader.load_radar_data(clip_id, 'radar_front_center_mrr_2')

# Convert radar to Cartesian (in sensor frame)
radar_points = radar_loader.convert_to_cartesian(radar_df)

# Get radar extrinsics
radar_ext = sensor_extrinsics[
    sensor_extrinsics['sensor_name'] == 'radar_front_center_mrr_2'
].iloc[0]

# Transform to rig frame
T_radar = calib.get_transformation_matrix(radar_ext)
radar_points_rig = calib.transform_points(radar_points, T_radar)

# Now radar_points_rig and lidar points are in same frame
# Can fuse, compare, or visualize together
```

### 5. Visualize Sensor Setup

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot each sensor position
for _, sensor in sensor_extrinsics.iterrows():
    x, y, z = sensor['x'], sensor['y'], sensor['z']
    sensor_name = sensor['sensor_name']
    
    # Color by sensor type
    if 'camera' in sensor_name:
        color = 'blue'
        marker = 'o'
    elif 'lidar' in sensor_name:
        color = 'green'
        marker = '^'
    else:  # radar
        color = 'red'
        marker = 's'
    
    ax.scatter(x, y, z, c=color, marker=marker, s=100, label=sensor_name)

# Plot vehicle outline (simplified)
vehicle = calib.load_vehicle_dimensions(clip_id)
length, width = vehicle['length'], vehicle['width']

# Draw vehicle box at origin
vehicle_box = np.array([
    [-length/2, -width/2, 0],
    [length/2, -width/2, 0],
    [length/2, width/2, 0],
    [-length/2, width/2, 0],
    [-length/2, -width/2, 0]
])
ax.plot(vehicle_box[:, 0], vehicle_box[:, 1], vehicle_box[:, 2], 'k-', linewidth=2)

ax.set_xlabel('X (forward) [m]')
ax.set_ylabel('Y (left) [m]')
ax.set_zlabel('Z (up) [m]')
ax.set_title('Sensor Configuration')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
```

## Quaternion Operations

### Converting to Rotation Matrix

```python
# Using calibration utility
R = calib.quaternion_to_rotation_matrix(qx, qy, qz, qw)

# Or manually
def quat_to_matrix(qx, qy, qz, qw):
    # Normalize
    norm = np.sqrt(qx**2 + qy**2 + qz**2 + qw**2)
    qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm
    
    # Convert to rotation matrix
    R = np.array([
        [1 - 2*(qy**2 + qz**2), 2*(qx*qy - qw*qz), 2*(qx*qz + qw*qy)],
        [2*(qx*qy + qw*qz), 1 - 2*(qx**2 + qz**2), 2*(qy*qz - qw*qx)],
        [2*(qx*qz - qw*qy), 2*(qy*qz + qw*qx), 1 - 2*(qx**2 + qy**2)]
    ])
    return R
```

### Composing Transformations

```python
# Transform A -> B and B -> C
T_AB = calib.get_transformation_matrix(extrinsics_AB)
T_BC = calib.get_transformation_matrix(extrinsics_BC)

# Compose to get A -> C
T_AC = T_BC @ T_AB
```

### Inverse Transformation

```python
T = calib.get_transformation_matrix(extrinsics)
T_inv = np.linalg.inv(T)

# Or for SE(3) (more efficient):
def inverse_transform(T):
    R = T[:3, :3]
    t = T[:3, 3]
    
    T_inv = np.eye(4)
    T_inv[:3, :3] = R.T
    T_inv[:3, 3] = -R.T @ t
    
    return T_inv
```

## Best Practices

1. **Always check sensor availability**: Not all sensors are present in all clips
2. **Validate projections**: Check that projected points are within image bounds
3. **Use appropriate coordinate frames**: Be careful about which frame you're in
4. **Cache transformations**: Compute transformation matrices once and reuse
5. **Handle edge cases**: Some points may be behind camera or outside FOV
6. **Account for temporal alignment**: Sensor data may have slight time offsets

## Troubleshooting

### Points project outside image

- Check if points are in front of camera (positive Z in camera frame)
- Verify camera FOV - wide angle cameras may have distortion at edges
- Ensure using correct camera extrinsics

### Incorrect alignment

- Double-check coordinate frame (rig frame vs sensor frame)
- Verify you're using correct transformation direction (forward vs inverse)
- Check quaternion normalization

### Performance issues

- Pre-compute and cache transformation matrices
- Filter points by distance before projection
- Use vectorized operations instead of loops

## Additional Resources

- See `API_REFERENCE.md` for detailed API documentation
- See `DATA_FORMAT.md` for calibration file format specifications
- Example notebooks in `examples/` directory

---

*For questions or issues, please refer to the FAQ or open an issue on GitHub.*
