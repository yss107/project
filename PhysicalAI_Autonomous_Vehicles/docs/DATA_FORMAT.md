# Data Format Specification

This document provides detailed specifications for all data formats in the PhysicalAI-Autonomous-Vehicles dataset.

## Dataset Organization

The dataset is organized hierarchically:
```
dataset_root/
├── camera/
│   ├── camera_front_wide_120fov/
│   ├── camera_front_tele_30fov/
│   └── ...
├── lidar/
│   └── lidar_top_360fov/
├── radar/
│   ├── radar_corner_front_left_srr_0/
│   └── ...
├── calibration/
│   ├── camera_intrinsics.parquet
│   ├── sensor_extrinsics.parquet
│   └── vehicle_dimensions.parquet
├── labels/
│   └── ego_motion/
└── metadata/
    ├── data_collection.parquet
    └── sensor_presence.parquet
```

## Camera Data Format

### Directory Structure
```
camera/<camera_name>/
└── <camera_name>.chunk_XXXX.zip
```

### Camera Types
| Camera Name | Field of View | Resolution | Frame Rate |
|------------|---------------|------------|------------|
| `camera_cross_left_120fov` | 120° | 1080p | 30 fps |
| `camera_cross_right_120fov` | 120° | 1080p | 30 fps |
| `camera_front_wide_120fov` | 120° | 1080p | 30 fps |
| `camera_front_tele_30fov` | 30° | 1080p | 30 fps |
| `camera_rear_left_70fov` | 70° | 1080p | 30 fps |
| `camera_rear_right_70fov` | 70° | 1080p | 30 fps |
| `camera_rear_tele_30fov` | 30° | 1080p | 30 fps |

### File Naming Convention
- Video: `<clip_uuid>.camera_<field_of_view>.mp4`
- Timestamps: `<clip_uuid>.camera_<field_of_view>_timestamps.parquet`

### Video Properties
- **Format**: MP4 (H.264 encoding)
- **Duration**: 20 seconds per clip
- **Resolution**: 1920x1080
- **Frame Rate**: 30 fps (~600 frames per clip)

### Timestamp Schema
```python
{
    'frame_index': int64,        # Frame number (0, 1, 2, ..., ~599)
    'timestamp': int64,          # Timestamp in microseconds
}
```

## LiDAR Data Format

### Directory Structure
```
lidar/lidar_top_360fov/
└── lidar_top_360fov_clip_XXXX.zip
```

### File Naming Convention
`<clip_uuid>.lidar_top360_fov.parquet`

### LiDAR Properties
- **Type**: 360° rotating LiDAR
- **Capture Rate**: 10 Hz
- **Spins per Clip**: ~200 (20 seconds × 10 Hz)
- **Encoding**: Draco compression

### Parquet Schema
```python
{
    'spin_index': int64,                 # Spin number (0, 1, 2, ..., 199)
    'reference_timestamp': int64,        # Reference timestamp (microseconds)
    'draco_encoded_pointcloud': binary,  # Draco-encoded point cloud
}
```

### Point Cloud Structure (after decoding)
```python
{
    'x': float,          # X coordinate in meters (rig frame)
    'y': float,          # Y coordinate in meters (rig frame)
    'z': float,          # Z coordinate in meters (rig frame)
    'intensity': float,  # Reflection intensity (optional)
}
```

### Decoding Example
```python
import DracoPy
import pandas as pd

# Load parquet file
lidar_df = pd.read_parquet('clip.parquet')

# Decode a single spin
draco_bytes = lidar_df.iloc[0]['draco_encoded_pointcloud']
point_cloud = DracoPy.decode(draco_bytes)

# Access points
points = point_cloud.points  # Nx3 array [x, y, z]
```

## Radar Data Format

### Directory Structure
```
radar/<radar_sensor_name>/
└── <radar_sensor_name>.chunk_XXXX.zip
```

### Radar Types
- **SRR**: Short Range Radar
- **MRR**: Medium Range Radar
- **LRR**: Long Range Radar

### Radar Sensors (up to 10 per vehicle)
1. Corner radars: front-left, front-right, rear-left, rear-right
2. Front center: imaging LRR, MRR, SRR
3. Rear: left and right (MRR, SRR)
4. Side: left and right (SRR)

### File Naming Convention
`<clip_uuid>.radar_<location>_<type>_<model>.parquet`

Example: `abc123.radar_corner_front_left_srr_0.parquet`

### Parquet Schema
```python
{
    # Index
    'scan_index': int64,           # Sequential scan number
    
    # Timestamps
    'timestamp': int64,            # System timestamp (microseconds)
    'sensor_timestamp': int64,     # Sensor timestamp (microseconds)
    
    # Scan Information
    'num_returns': int64,          # Number of detections in scan
    'doppler_ambiguity': float32,  # Doppler ambiguity value
    'max_returns': float64,        # Maximum returns (NaN if N/A)
    'detection_index': int64,      # Detection index within scan
    'radar_model': uint8,          # Radar model identifier
    
    # Detection Spatial Data (Spherical Coordinates)
    'azimuth': float32,            # Horizontal angle (radians)
    'elevation': float32,          # Vertical angle (radians)
    'distance': float32,           # Distance to target (meters)
    
    # Detection Kinematics
    'radial_velocity': float32,    # Radial velocity (m/s)
    
    # Detection Quality Metrics
    'rcs': float32,                # Radar cross-section (dBsm)
    'snr': float32,                # Signal-to-noise ratio (dB)
    'exist_probb': uint8,          # Existence probability (0-255)
}
```

### Radar Configurations
| Config | Description |
|--------|-------------|
| `NA` | No radars present |
| `low` | All SRR_0 radars |
| `med` | All SRR_3 (except sides), all MRR_2 and LRR_1 |
| `high` | All SRR_3, all MRR_2 and LRR_1 |

## Calibration Data Format

### Camera Intrinsics

**File**: `calibration/camera_intrinsics.parquet`

**Schema**:
```python
{
    # Index
    'clip_id': str,                    # Unique clip identifier UUID
    'camera_name': str,                # Camera sensor name
    
    # Image Dimensions
    'width': int64,                    # Image width (pixels)
    'height': int64,                   # Image height (pixels)
    
    # Principal Point (optical center)
    'cx': float64,                     # Principal point X (pixels)
    'cy': float64,                     # Principal point Y (pixels)
    
    # Backward f-theta Polynomial (Undistortion)
    'bw_poly_0': float64,              # Coefficient 0
    'bw_poly_1': float64,              # Coefficient 1
    'bw_poly_2': float64,              # Coefficient 2
    'bw_poly_3': float64,              # Coefficient 3
    'bw_poly_4': float64,              # Coefficient 4
    
    # Forward f-theta Polynomial (Distortion)
    'fw_poly_0': float64,              # Coefficient 0
    'fw_poly_1': float64,              # Coefficient 1 (focal length)
    'fw_poly_2': float64,              # Coefficient 2
    'fw_poly_3': float64,              # Coefficient 3
    'fw_poly_4': float64,              # Coefficient 4
}
```

### Sensor Extrinsics

**File**: `calibration/sensor_extrinsics.parquet`

**Schema**:
```python
{
    'clip_id': str,      # Unique clip identifier
    'sensor_name': str,  # Sensor name (camera/lidar/radar)
    
    # Rotation (Quaternion)
    'qx': float64,       # Quaternion X component
    'qy': float64,       # Quaternion Y component
    'qz': float64,       # Quaternion Z component
    'qw': float64,       # Quaternion W (scalar) component
    
    # Translation
    'x': float64,        # X position (meters, rig frame)
    'y': float64,        # Y position (meters, rig frame)
    'z': float64,        # Z position (meters, rig frame)
}
```

**Rig Coordinate Frame**:
- **Origin**: Center of rear axle, projected to ground plane
- **X-axis**: Points forward
- **Y-axis**: Points left (when facing forward)
- **Z-axis**: Points up

### Vehicle Dimensions

**File**: `calibration/vehicle_dimensions.parquet`

**Schema**:
```python
{
    'clip_id': str,                       # Unique clip identifier
    
    # Dimensions (meters)
    'length': float64,                    # Vehicle length (front to back)
    'width': float64,                     # Vehicle width (left to right)
    'height': float64,                    # Vehicle height (bottom to top)
    'rear_axle_to_bbox_center': float64,  # Rear axle to geometric center
    'wheelbase': float64,                 # Distance between axles
    'track_width': float64,               # Wheel track width
}
```

## Ego Motion (Labels)

**Directory**: `labels/ego_motion/`
**File**: `<clip_uuid>.parquet`

**Schema**:
```python
{
    # Timing
    'timestamp': int64,                 # Absolute timestamp (microseconds)
    
    # Pose - Orientation (Quaternion in local frame)
    'qx': float64,                      # Quaternion X component
    'qy': float64,                      # Quaternion Y component
    'qz': float64,                      # Quaternion Z component
    'qw': float64,                      # Quaternion W (scalar)
    
    # Pose - Position in Local Frame (meters)
    'x': float64,                       # X position
    'y': float64,                       # Y position
    'z': float64,                       # Z position
    
    # Velocity in World Frame (m/s)
    'vx': float64,                      # X velocity
    'vy': float64,                      # Y velocity
    'vz': float64,                      # Z velocity
    
    # Acceleration in World Frame (m/s²)
    'ax': float64,                      # X acceleration
    'ay': float64,                      # Y acceleration
    'az': float64,                      # Z acceleration
    
    # Vehicle Kinematics
    'curvature': float64,               # Path curvature (1/meters)
}
```

**Local Frame**: Consistent across timestamps with origin at ego vehicle position at timestamp 0, oriented with 0 yaw at timestamp 0 but with pitch and roll estimated relative to gravity.

## Metadata Format

### Data Collection Metadata

**File**: `metadata/data_collection.parquet`

**Schema**:
```python
{
    'clip_id': str,                     # Unique clip identifier UUID
    
    # Geographic Information
    'country': str,                     # Country name
    
    # Temporal Information
    'month': int64,                     # Month (1-12)
    'hour_of_day': int64,               # Hour (0-23)
    
    # Vehicle Platform
    'platform_class': str,              # Platform type (hyperion_8/8.1)
}
```

### Sensor Presence Metadata

**File**: `metadata/sensor_presence.parquet`

**Schema**: Boolean fields indicating sensor availability
```python
{
    'clip_id': str,                              # UUID
    
    # Camera Sensors (bool)
    'camera_cross_left_120fov': bool,
    'camera_cross_right_120fov': bool,
    'camera_front_tele_30fov': bool,
    'camera_front_wide_120fov': bool,
    'camera_rear_left_70fov': bool,
    'camera_rear_right_70fov': bool,
    'camera_rear_tele_30fov': bool,
    
    # LiDAR Sensor (bool)
    'lidar_top_360fov': bool,
    
    # Radar Sensors (bool) - 19 total
    'radar_corner_front_left_srr_0': bool,
    'radar_corner_front_left_srr_3': bool,
    # ... (see full list in README)
    
    # Radar Configuration Summary
    'radar_config': str,                  # 'NA', 'low', 'med', 'high'
}
```

## Data Types Summary

| Data Type | Storage Format | Compression | Size per Clip |
|-----------|---------------|-------------|---------------|
| Camera (7 sensors) | MP4 (H.264) | Video codec | ~50-100 MB |
| LiDAR | Parquet + Draco | Draco | ~10-20 MB |
| Radar (10 sensors) | Parquet | Snappy | ~1-5 MB |
| Calibration | Parquet | Snappy | <1 KB |
| Ego Motion | Parquet | Snappy | <100 KB |
| Metadata | Parquet | Snappy | <1 KB |

## UUID Structure

Clip IDs are UUIDs that uniquely identify each 20-second recording clip. The same UUID is used across all sensors and metadata files for a given clip.

Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

## Timestamps

All timestamps are in **microseconds** (µs) since Unix epoch.

To convert to seconds:
```python
timestamp_seconds = timestamp_microseconds / 1_000_000
```

## Chunking Strategy

Data is chunked for efficient storage and retrieval:
- **Chunk size**: ~100 clips per chunk
- **Naming**: Sequential numbering (chunk_0000, chunk_0001, ...)
- **Exception**: Metadata files are not chunked

Benefits:
- Download only required sensors
- Filter by metadata before downloading
- Efficient bandwidth usage
