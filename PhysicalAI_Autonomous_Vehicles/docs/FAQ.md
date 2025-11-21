# Frequently Asked Questions (FAQ)

## General Questions

### What is the PhysicalAI-Autonomous-Vehicles dataset?

The PhysicalAI-Autonomous-Vehicles dataset is one of the largest, most geographically diverse collections of multi-sensor data for autonomous vehicle research, provided by NVIDIA Corporation. It contains 1,727 hours of driving data from 25 countries and 2,500+ cities.

### How large is the dataset?

- **Total size**: ~100TB
- **Number of clips**: 310,895 clips (20 seconds each)
- **Duration**: 1,727 hours
- **Geographic coverage**: 25 countries, 2,500+ cities

### What sensors are included?

- **7 cameras**: Various fields of view (30°, 70°, 120°, 360°)
- **1 LiDAR**: 360° top-mounted, 10Hz
- **Up to 10 radars**: Short/medium/long range configurations

### How is the data organized?

Data is organized in chunks (zip files) containing approximately 100 clips each. This allows you to download only the sensors and geographic regions you need.

## Access and Usage

### Where can I download the dataset?

The dataset is available on HuggingFace:
https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles

### What is the license?

The dataset is provided under the **NVIDIA Autonomous Vehicle Dataset License Agreement**. It can be used for autonomous vehicle-related use cases (commercial or non-commercial) as long as the license terms are followed.

### Do I need to download the entire dataset?

No! The chunked structure allows you to:
1. Download metadata first
2. Filter clips by country, time, sensors, etc.
3. Download only the chunks you need

### How much storage do I need?

It depends on what you download:
- **Full dataset**: ~100TB
- **Single sensor (e.g., front camera)**: ~15-20TB
- **Sample subset (1000 clips)**: ~10-50GB depending on sensors

## Technical Questions

### What programming language is supported?

This toolkit is written in Python 3.8+. The utilities work with standard scientific Python libraries (pandas, numpy, opencv, etc.).

### How do I decode LiDAR point clouds?

LiDAR data is compressed using Draco encoding. You need the `DracoPy` library:

```python
pip install DracoPy
```

Then use the `LiDARLoader` utility:

```python
from utils import LiDARLoader

loader = LiDARLoader(dataset_root)
pointcloud_df = loader.load_pointcloud(clip_id)
```

### How do I work with camera data?

Camera data is stored as MP4 videos. Use the `CameraLoader`:

```python
from utils import CameraLoader

loader = CameraLoader(dataset_root)
frames, timestamps = loader.load_video_from_chunk(clip_id, 'camera_front_wide_120fov')
```

### What coordinate system is used?

**Rig Coordinate Frame**:
- **Origin**: Center of rear axle, projected to ground plane
- **X-axis**: Points forward
- **Y-axis**: Points left (when facing forward)
- **Z-axis**: Points up
- **Units**: Meters

### How are timestamps formatted?

All timestamps are in **microseconds** (µs) since Unix epoch.

```python
# Convert to seconds
timestamp_seconds = timestamp_microseconds / 1_000_000
```

### What is the frame rate for cameras?

All cameras record at **30 fps** with **1080p** resolution.

### What is the LiDAR capture rate?

The LiDAR operates at **10 Hz**, providing approximately 200 spins per 20-second clip.

### How do I project LiDAR/radar points to camera images?

Use the calibration utilities:

```python
from utils import CalibrationLoader

calib = CalibrationLoader(dataset_root)
camera_intrinsics = calib.load_camera_intrinsics(clip_id)
camera_extrinsics = calib.load_sensor_extrinsics(clip_id)

points_2d, valid_mask = calib.project_points_to_camera(
    points_3d, camera_intrinsics, camera_extrinsics
)
```

### What radar configurations are available?

There are 4 radar configurations:
- **NA**: No radars
- **low**: All SRR_0 radars (163,850 clips don't have radar)
- **med**: All SRR_3 (except sides), all MRR_2 and LRR_1
- **high**: All SRR_3, all MRR_2 and LRR_1

## Data Quality and Coverage

### Are all sensors available for every clip?

No. All clips have camera and LiDAR, but only 163,850 clips have radar coverage. Use the sensor presence metadata to check availability:

```python
sensor_meta = loader.load_sensor_presence()
clips_with_radar = sensor_meta[sensor_meta['radar_config'] != 'NA']
```

### What weather conditions are included?

- Clear
- Rain
- Snow
- Fog

### What time-of-day coverage is available?

- Daytime
- Nighttime

Filter by hour:
```python
daytime_clips = loader.filter_clips(hour_range=(6, 18))
nighttime_clips = loader.filter_clips(hour_range=(18, 6))
```

### Which countries have the most data?

Top 5 countries:
1. **United States**: 155,360 clips (50%)
2. **Germany**: 45,673 clips
3. **France**: 10,911 clips
4. **Italy**: 9,082 clips
5. **Sweden**: 7,451 clips

See README for full list.

## Use Cases

### What can I use this dataset for?

Intended use cases include:
- End-to-end autonomous driving
- Neural reconstruction
- Synthetic data generation
- Scenario mining
- Sensor fusion research
- 3D mapping and localization
- Traffic behavior analysis

### Can I use this for commercial purposes?

Yes, as long as it's for autonomous vehicle-related use cases and follows the license terms.

### Are there ground truth labels?

Currently, the dataset provides:
- Ego motion (pose, velocity, acceleration)
- Autogenerated machine labels
- Calibration data

Object and road element labels are **coming soon**.

## Performance and Optimization

### How can I speed up data loading?

1. **Use chunking**: Only load the sensors you need
2. **Filter first**: Use metadata to identify relevant clips before downloading
3. **Cache processed data**: Store decoded point clouds to avoid repeated decoding
4. **Parallel processing**: Use multiprocessing for batch operations
5. **SSD storage**: Use fast storage for better I/O performance

### How much RAM do I need?

Recommended:
- **Metadata only**: 4GB
- **Single clip processing**: 8GB
- **Batch processing**: 16GB+
- **Full point cloud processing**: 32GB+

### Can I process this on a laptop?

Yes, for small subsets. Recommended approach:
1. Download metadata (small)
2. Filter to interesting clips (e.g., 100-1000 clips)
3. Download only those chunks
4. Process incrementally

## Troubleshooting

### I get "DracoPy not available" error

Install DracoPy:
```bash
pip install DracoPy
```

### Files are corrupted or won't unzip

- Check download integrity
- Verify sufficient disk space
- Try re-downloading the chunk
- Check filesystem permissions

### Out of memory errors

- Reduce batch size
- Process clips one at a time
- Use downsampling for point clouds
- Close unused applications

### Can't find clip in chunk

- Verify clip_id is correct
- Check sensor availability in metadata
- Ensure chunk file is for correct sensor

## Getting Help

### Where can I report issues?

- GitHub Issues: [yss107/project](https://github.com/yss107/project)
- Check existing issues first

### Where can I find more documentation?

- `docs/DATA_FORMAT.md`: Detailed data format specifications
- `docs/CALIBRATION.md`: Calibration guide
- `docs/API_REFERENCE.md`: API documentation
- Example notebooks in `examples/`

### Can I contribute?

Yes! Contributions are welcome:
- Report bugs
- Submit pull requests
- Improve documentation
- Add examples

## Related Resources

- **NVIDIA Developer Kit**: https://github.com/NVlabs/physical_ai_av (Coming Soon)
- **Cosmos Dataset Search**: https://developer.nvidia.com/cosmos
- **HuggingFace Dataset**: https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles

---

*Last updated: 2025*
