# 🚗 NVIDIA PhysicalAI-Autonomous-Vehicles Dataset

[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)
[![License](https://img.shields.io/badge/License-NVIDIA_AV_Dataset-blue?style=for-the-badge)](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://www.python.org/)

A comprehensive Python toolkit for working with NVIDIA's PhysicalAI-Autonomous-Vehicles dataset - one of the largest, most geographically diverse collections of multi-sensor data for autonomous vehicle research.

![Dataset Banner](readme-resources/av-banner.png)

## 📊 Dataset Overview

The PhysicalAI-Autonomous-Vehicles dataset provides:
- **1,727 hours** of driving data
- **310,895 clips** (20 seconds each)
- **25 countries** coverage
- **2,500+ cities** represented
- **~100TB** of total data

### 🌍 Geographic Coverage
- 50% from USA (155,360 clips)
- 50% from 24 EU countries (155,535 clips)

### 🎥 Sensor Configuration
- **7 Cameras**: Multiple FOV (30°, 70°, 120°, 360°)
- **1 LiDAR**: 360° top-mounted (10Hz)
- **Up to 10 Radars**: Short/Medium/Long range

## 🎯 Features

This project provides:
- 📦 Easy data loading utilities for all sensor types
- 🔍 Metadata filtering and querying
- 📊 Data visualization tools
- 🛠️ Calibration utilities
- 📝 Comprehensive documentation
- 💻 Example notebooks

## 📁 Dataset Structure

### Camera Data
```
camera/
├─ camera_front_wide_120fov/
│  ├─ camera_front_wide_120fov.chunk_0000.zip
│  └─ ...
└─ camera_cross_left_120fov/
   └─ ...
```

**7 Camera Views:**
- Cross left 120 FOV
- Cross right 120 FOV
- Front wide 120 FOV
- Front tele 30 FOV
- Rear left 70 FOV
- Rear right 70 FOV
- Rear tele 30 FOV

### LiDAR Data
```
lidar/
└─ lidar_top_360fov/
   ├─ lidar_top_360fov_clip_0000.zip
   └─ ...
```

**Format:** Draco-encoded point clouds at 10Hz (~200 spins per 20s clip)

### Radar Data
```
radar/
├─ radar_corner_front_left_srr_0/
├─ radar_corner_front_right_srr_0/
└─ ...
```

**Up to 10 Radar Sensors:**
- Corner radars (front/rear, left/right)
- Front center imaging
- Side radars
- Configurations: SRR (short), MRR (medium), LRR (long) range

## 🚀 Quick Start

### Installation

```bash
# Clone this repository
git clone https://github.com/yss107/project.git
cd project/PhysicalAI_Autonomous_Vehicles

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from utils.data_loader import DatasetLoader

# Initialize loader
loader = DatasetLoader(data_root="/path/to/dataset")

# Load clip metadata
metadata = loader.load_metadata()

# Filter clips by country and time
us_daytime = metadata[
    (metadata['country'] == 'United States') & 
    (metadata['hour_of_day'] >= 6) & 
    (metadata['hour_of_day'] <= 18)
]

# Load camera data for a specific clip
clip_id = "example-uuid"
camera_data = loader.load_camera_clip(clip_id, camera="front_wide_120fov")

# Load LiDAR point cloud
lidar_data = loader.load_lidar_clip(clip_id)

# Load radar data
radar_data = loader.load_radar_clip(clip_id, radar_sensor="front_center")
```

## 📚 Key Components

### 1. Data Loaders (`utils/`)
- `data_loader.py`: Main dataset loading utilities
- `camera_utils.py`: Camera data processing
- `lidar_utils.py`: LiDAR point cloud handling
- `radar_utils.py`: Radar data processing
- `calibration_utils.py`: Sensor calibration tools

### 2. Visualization (`visualization/`)
- Camera view display
- Point cloud rendering
- Radar visualization
- Multi-sensor fusion display

### 3. Examples (`examples/`)
- `01_data_exploration.ipynb`: Dataset exploration
- `02_sensor_visualization.ipynb`: Visualizing sensor data
- `03_metadata_filtering.ipynb`: Querying and filtering
- `04_calibration_example.ipynb`: Using calibration data

## 📊 Data Characteristics

### Environmental Diversity
- **Traffic**: No traffic, light, medium, heavy
- **Road Types**: Highways, urban, residential, rural
- **Weather**: Clear, rain, snow, fog
- **Surface**: Dry, wet, snow/ice
- **Time**: Daytime, nighttime
- **Infrastructure**: Tunnels, bridges, roundabouts, toll booths, etc.

### Sensor Coverage
- All clips have camera and LiDAR
- 163,850 clips have radar coverage
- 4 radar configurations: NA, low, med, high

## 🔬 Use Cases

This dataset is ideal for:
- 🚘 End-to-end autonomous driving
- 🌐 Neural reconstruction
- 🎨 Synthetic data generation
- 🔍 Scenario mining
- 📏 Sensor fusion research
- 🗺️ 3D mapping and localization
- 🚦 Traffic behavior analysis

## 📖 Documentation

Detailed documentation available in `docs/`:
- [Data Format Specification](docs/DATA_FORMAT.md)
- [Calibration Guide](docs/CALIBRATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [FAQ](docs/FAQ.md)

## 🛠️ Requirements

- Python 3.8+
- pandas
- numpy
- opencv-python
- DracoPy (for LiDAR decoding)
- pyarrow (for Parquet files)
- matplotlib
- seaborn

## 📝 License

This dataset is provided under the **NVIDIA Autonomous Vehicle Dataset License Agreement**.

**Intended Usage:** Autonomous vehicle related use cases only (commercial or non-commercial).

See [License Agreement](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles) for full terms.

## 🔗 Resources

- 📦 [Dataset on HuggingFace](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)
- 💻 [NVIDIA Developer Kit](https://github.com/NVlabs/physical_ai_av) (Coming Soon)
- 🔍 [Cosmos Dataset Search](https://developer.nvidia.com/cosmos) - Multimodal semantic search tool
- 📚 [Full Documentation](docs/)

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report issues
- Submit pull requests
- Suggest features
- Improve documentation

## 📧 Contact

For questions or collaboration:
- **Author**: Yash Kumar
- **LinkedIn**: [yash-kumar09](https://www.linkedin.com/in/yash-kumar09/)
- **GitHub**: [yss107](https://github.com/yss107)

## 🙏 Acknowledgments

Dataset provided by **NVIDIA Corporation**.

Special thanks to the NVIDIA team for making this comprehensive autonomous vehicle dataset publicly available for research.

---

<div align="center">

**Made with ❤️ for Autonomous Vehicle Research**

⭐ Star this repository if you find it useful!

</div>
