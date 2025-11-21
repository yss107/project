# API Reference

Complete API documentation for the PhysicalAI-Autonomous-Vehicles dataset toolkit.

## Module: `utils.data_loader`

### Class: `DatasetLoader`

Main interface for loading dataset metadata and accessing sensor data.

#### Constructor

```python
DatasetLoader(data_root: str)
```

**Parameters:**
- `data_root` (str): Path to the root directory of the dataset

**Raises:**
- `ValueError`: If dataset root directory does not exist

#### Methods

##### `load_metadata(metadata_type: str = 'data_collection') -> pd.DataFrame`

Load metadata parquet file.

**Parameters:**
- `metadata_type` (str): Type of metadata. Options: `'data_collection'`, `'sensor_presence'`

**Returns:**
- `pd.DataFrame`: Metadata dataframe

**Raises:**
- `FileNotFoundError`: If metadata file not found

##### `filter_clips(**kwargs) -> pd.DataFrame`

Filter clips based on various criteria.

**Parameters:**
- `country` (str, optional): Filter by country name
- `month` (int, optional): Filter by month (1-12)
- `hour_range` (tuple, optional): Hour range as (start, end)
- `radar_config` (str, optional): Radar config ('NA', 'low', 'med', 'high')
- `camera_required` (str, optional): Required camera sensor name

**Returns:**
- `pd.DataFrame`: Filtered clip metadata

**Example:**
```python
us_clips = loader.filter_clips(
    country='United States',
    hour_range=(6, 18),
    radar_config='high'
)
```

##### `get_clip_info(clip_id: str) -> Dict`

Get comprehensive information about a specific clip.

**Parameters:**
- `clip_id` (str): UUID of the clip

**Returns:**
- `dict`: Dictionary containing all metadata for the clip

**Raises:**
- `ValueError`: If clip ID not found

##### `get_statistics() -> Dict`

Get overall dataset statistics.

**Returns:**
- `dict`: Statistics including:
  - `total_clips`: Total number of clips
  - `total_hours`: Total hours of data
  - `countries`: Number of unique countries
  - `country_distribution`: Clips per country
  - `clips_with_radar`: Number of clips with radar
  - `radar_config_distribution`: Radar config distribution
  - `platform_distribution`: Platform class distribution

##### `sample_clips(n: int = 10, random_state: Optional[int] = None, **filter_kwargs) -> pd.DataFrame`

Sample random clips with optional filtering.

**Parameters:**
- `n` (int): Number of clips to sample
- `random_state` (int, optional): Random seed
- `**filter_kwargs`: Filtering criteria

**Returns:**
- `pd.DataFrame`: Sample of clip metadata

---

## Module: `utils.camera_utils`

### Class: `CameraLoader`

Utility for loading and processing camera data.

#### Constructor

```python
CameraLoader(dataset_root: str)
```

**Parameters:**
- `dataset_root` (str): Root directory of the dataset

#### Methods

##### `load_video_from_chunk(clip_id: str, camera_name: str, chunk_file: Optional[str] = None) -> Tuple[np.ndarray, pd.DataFrame]`

Load video data and timestamps for a specific clip and camera.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `camera_name` (str): Camera sensor name (e.g., 'camera_front_wide_120fov')
- `chunk_file` (str, optional): Path to chunk file (auto-detected if None)

**Returns:**
- `tuple`: (frames, timestamps)
  - `frames`: numpy array (n_frames, height, width, 3)
  - `timestamps`: pandas DataFrame with frame timestamps

**Raises:**
- `FileNotFoundError`: If chunk or video file not found

**Example:**
```python
camera = CameraLoader('/path/to/dataset')
frames, ts = camera.load_video_from_chunk(clip_id, 'camera_front_wide_120fov')
print(f"Loaded {len(frames)} frames")
```

##### `extract_frame(clip_id: str, camera_name: str, frame_idx: int, chunk_file: Optional[str] = None) -> np.ndarray`

Extract a single frame from a video clip.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `camera_name` (str): Camera sensor name
- `frame_idx` (int): Frame index to extract
- `chunk_file` (str, optional): Path to chunk file

**Returns:**
- `np.ndarray`: Single frame (height, width, 3)

**Raises:**
- `IndexError`: If frame index out of range

##### `get_video_info(clip_id: str, camera_name: str, chunk_file: Optional[str] = None) -> dict`

Get video information without loading all frames.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `camera_name` (str): Camera sensor name
- `chunk_file` (str, optional): Path to chunk file

**Returns:**
- `dict`: Video info including:
  - `fps`: Frames per second
  - `frame_count`: Total frames
  - `width`: Video width
  - `height`: Video height
  - `duration_sec`: Duration in seconds

##### `create_video_mosaic(clip_id: str, camera_names: List[str], frame_idx: int = 0, layout: str = '2x4') -> np.ndarray`

Create a mosaic view from multiple cameras.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `camera_names` (list): List of camera names
- `frame_idx` (int): Frame index to extract
- `layout` (str): Layout pattern (e.g., '2x4' for 2 rows, 4 columns)

**Returns:**
- `np.ndarray`: Mosaic image

---

## Module: `utils.lidar_utils`

### Class: `LiDARLoader`

Utility for loading and processing LiDAR point cloud data.

#### Constructor

```python
LiDARLoader(dataset_root: str)
```

**Parameters:**
- `dataset_root` (str): Root directory of the dataset

**Raises:**
- `ImportError`: If DracoPy is not available

#### Methods

##### `load_pointcloud(clip_id: str, chunk_file: Optional[str] = None) -> pd.DataFrame`

Load LiDAR point cloud data for a specific clip.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `chunk_file` (str, optional): Path to chunk file

**Returns:**
- `pd.DataFrame`: Point cloud data with columns:
  - `spin_index`: Spin number (0-199)
  - `reference_timestamp`: Timestamp (microseconds)
  - `draco_encoded_pointcloud`: Binary encoded point cloud

##### `decode_pointcloud(draco_bytes: bytes) -> np.ndarray`

Decode Draco-encoded point cloud to numpy array.

**Parameters:**
- `draco_bytes` (bytes): Draco-encoded binary data

**Returns:**
- `np.ndarray`: Decoded point cloud (N, 3+) [x, y, z, ...]

##### `load_spin(clip_id: str, spin_idx: int, chunk_file: Optional[str] = None) -> np.ndarray`

Load a single LiDAR spin as numpy array.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `spin_idx` (int): Spin index (0-199)
- `chunk_file` (str, optional): Path to chunk file

**Returns:**
- `np.ndarray`: Decoded point cloud for the spin

**Example:**
```python
lidar = LiDARLoader('/path/to/dataset')
points = lidar.load_spin(clip_id, spin_idx=50)
print(f"Loaded {len(points)} points")
```

##### `extract_bounding_box(points: np.ndarray, x_range: Optional[Tuple[float, float]] = None, y_range: Optional[Tuple[float, float]] = None, z_range: Optional[Tuple[float, float]] = None) -> np.ndarray`

Extract points within a bounding box.

**Parameters:**
- `points` (np.ndarray): Point cloud (N, 3+)
- `x_range` (tuple, optional): (min_x, max_x)
- `y_range` (tuple, optional): (min_y, max_y)
- `z_range` (tuple, optional): (min_z, max_z)

**Returns:**
- `np.ndarray`: Filtered points

##### `downsample_pointcloud(points: np.ndarray, voxel_size: float = 0.1) -> np.ndarray`

Downsample point cloud using voxel grid filtering.

**Parameters:**
- `points` (np.ndarray): Point cloud (N, 3+)
- `voxel_size` (float): Voxel grid size in meters

**Returns:**
- `np.ndarray`: Downsampled points

---

## Module: `utils.radar_utils`

### Class: `RadarLoader`

Utility for loading and processing radar data.

#### Constructor

```python
RadarLoader(dataset_root: str)
```

**Parameters:**
- `dataset_root` (str): Root directory of the dataset

#### Methods

##### `load_radar_data(clip_id: str, radar_sensor: str, chunk_file: Optional[str] = None) -> pd.DataFrame`

Load radar data for a specific clip and sensor.

**Parameters:**
- `clip_id` (str): UUID of the clip
- `radar_sensor` (str): Radar sensor name
- `chunk_file` (str, optional): Path to chunk file

**Returns:**
- `pd.DataFrame`: Radar data with columns:
  - `scan_index`: Sequential scan number
  - `timestamp`: System timestamp (microseconds)
  - `azimuth`: Horizontal angle (radians)
  - `elevation`: Vertical angle (radians)
  - `distance`: Distance (meters)
  - `radial_velocity`: Radial velocity (m/s)
  - `rcs`: Radar cross-section (dBsm)
  - `snr`: Signal-to-noise ratio (dB)
  - ... and more

##### `convert_to_cartesian(radar_df: pd.DataFrame) -> np.ndarray`

Convert radar data from spherical to Cartesian coordinates.

**Parameters:**
- `radar_df` (pd.DataFrame): Radar dataframe

**Returns:**
- `np.ndarray`: Points in Cartesian (N, 3) [x, y, z]

##### `filter_by_distance(radar_df: pd.DataFrame, min_distance: float = 0.0, max_distance: float = np.inf) -> pd.DataFrame`

Filter radar detections by distance.

##### `filter_by_velocity(radar_df: pd.DataFrame, min_velocity: float = -np.inf, max_velocity: float = np.inf) -> pd.DataFrame`

Filter radar detections by radial velocity.

##### `filter_by_snr(radar_df: pd.DataFrame, min_snr: float = 0.0) -> pd.DataFrame`

Filter radar detections by signal-to-noise ratio.

---

## Module: `utils.calibration_utils`

### Class: `CalibrationLoader`

Utility for loading and processing calibration data.

#### Constructor

```python
CalibrationLoader(dataset_root: str)
```

**Parameters:**
- `dataset_root` (str): Root directory of the dataset

#### Methods

##### `load_camera_intrinsics(clip_id: Optional[str] = None) -> pd.DataFrame`

Load camera intrinsic parameters.

**Parameters:**
- `clip_id` (str, optional): Specific clip ID (loads all if None)

**Returns:**
- `pd.DataFrame`: Camera intrinsics with f-theta model parameters

##### `load_sensor_extrinsics(clip_id: str) -> pd.DataFrame`

Load sensor extrinsic parameters (poses).

**Parameters:**
- `clip_id` (str): Clip ID

**Returns:**
- `pd.DataFrame`: Sensor extrinsics (quaternion rotation and translation)

##### `load_vehicle_dimensions(clip_id: str) -> pd.Series`

Load vehicle dimension parameters.

**Parameters:**
- `clip_id` (str): Clip ID

**Returns:**
- `pd.Series`: Vehicle dimensions

##### `quaternion_to_rotation_matrix(qx: float, qy: float, qz: float, qw: float) -> np.ndarray`

Convert quaternion to rotation matrix.

**Returns:**
- `np.ndarray`: 3x3 rotation matrix

##### `get_transformation_matrix(extrinsics: pd.Series) -> np.ndarray`

Get 4x4 transformation matrix from extrinsic parameters.

**Returns:**
- `np.ndarray`: 4x4 transformation matrix

##### `project_points_to_camera(points_3d: np.ndarray, camera_intrinsics: pd.Series, camera_extrinsics: pd.Series) -> Tuple[np.ndarray, np.ndarray]`

Project 3D points to camera image plane.

**Parameters:**
- `points_3d` (np.ndarray): 3D points in world coordinates (N, 3)
- `camera_intrinsics` (pd.Series): Camera intrinsic parameters
- `camera_extrinsics` (pd.Series): Camera extrinsic parameters

**Returns:**
- `tuple`: (points_2d, valid_mask)
  - `points_2d`: 2D image coordinates (N, 2)
  - `valid_mask`: Boolean mask for points in front of camera

**Example:**
```python
calib = CalibrationLoader('/path/to/dataset')
intrinsics = calib.load_camera_intrinsics(clip_id)
extrinsics = calib.load_sensor_extrinsics(clip_id)

points_2d, valid = calib.project_points_to_camera(
    lidar_points, intrinsics.iloc[0], extrinsics.iloc[0]
)
```

---

## Common Data Types

### Clip ID
- **Type**: `str`
- **Format**: UUID (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')

### Timestamps
- **Type**: `int64`
- **Units**: Microseconds since Unix epoch
- **Conversion**: `seconds = microseconds / 1_000_000`

### Coordinates
- **Type**: `float` or `np.ndarray`
- **Units**: Meters
- **Frame**: Rig coordinate system (see FAQ)

### Angles
- **Type**: `float`
- **Units**: Radians
- **Range**: [-π, π]

---

## Error Handling

All classes may raise the following exceptions:

- `FileNotFoundError`: When requested files don't exist
- `ValueError`: For invalid parameters or data
- `ImportError`: When required dependencies are missing
- `IndexError`: When accessing out-of-range indices

Always wrap calls in try-except blocks for production code:

```python
try:
    frames, ts = camera.load_video_from_chunk(clip_id, camera_name)
except FileNotFoundError:
    print("Video not found")
except Exception as e:
    print(f"Error: {e}")
```

---

*For more examples, see the `examples/` directory.*
