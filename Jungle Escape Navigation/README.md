# Jungle Escape Navigation - AI-Powered Path Planning

An AI/ML-based solution for navigating out of dense jungle using drone RGB images and satellite imagery.

## 📋 Overview

This project implements an intelligent navigation system that helps find safe paths through dense jungle terrain. It combines satellite imagery analysis with simulated drone camera feeds to compute optimal escape routes using computer vision and path planning algorithms.

## 🎯 Project Structure

```
Jungle Escape Navigation/
├── code/
│   ├── jungle_navigator.py      # Main navigation implementation
│   ├── data_acquisition.py      # Data download and simulation
│   └── [other utility scripts]
├── data/
│   ├── satellite_image.png      # Satellite map of the region
│   └── drone_images/            # Simulated drone RGB images
├── output/
│   ├── navigation_result.png    # Visualized path on map
│   └── path_data.json          # Path coordinates
├── report.pdf                   # Detailed report (3 methods + results)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Installation

1. Install Python 3.7 or higher
2. Install required packages:

```bash
cd "Jungle Escape Navigation"
pip install -r requirements.txt
```

### Data Acquisition

Generate simulated satellite imagery and drone images:

```bash
cd code
python data_acquisition.py
```

Or use your own Google Maps API key for real satellite imagery.

### Run Navigation System

Execute the main navigation system:

```bash
python jungle_navigator.py
```

## 🧠 Implemented Methods

### Method 1: Vision-based Terrain Classification + A* Path Planning (IMPLEMENTED)

This is the primary method implemented in this project.

**How it works:**
1. **Terrain Classification**: Uses color-based segmentation in HSV color space to identify:
   - Dense vegetation (dark green) - High traversal cost
   - Light vegetation (light green) - Medium cost
   - Clear paths/roads (brown/gray) - Low cost
   - Water bodies (blue) - Impassable

2. **Cost Map Generation**: Assigns traversal costs based on terrain type
   - Dense vegetation: Cost = 10
   - Light vegetation: Cost = 5
   - Clear paths: Cost = 1
   - Water: Cost = 1000 (nearly impassable)

3. **A* Path Planning**: Finds optimal path minimizing total traversal cost
   - Uses Euclidean distance heuristic
   - 8-directional movement
   - Considers both distance and terrain difficulty

4. **Drone Image Analysis**: Analyzes local terrain features:
   - Vegetation density calculation
   - Path detection (lighter areas)
   - Safety score estimation

**Advantages:**
- No training data required
- Fast computation
- Works with limited computational resources
- Real-time capable
- Interpretable results

### Method 2: Deep Learning with Semantic Segmentation (PROPOSED)

**Approach:**
- Use pre-trained models like DeepLabV3+ or U-Net
- Fine-tune on aerial imagery datasets (e.g., Mapillary Vistas, ADE20K)
- Segment terrain into multiple classes
- Generate cost map from segmentation
- Apply path planning algorithm

**Advantages:**
- Higher accuracy in complex terrain
- Can detect subtle features (animal paths, clearings)
- Learns from data patterns

**Disadvantages:**
- Requires training data
- Computationally expensive
- Needs GPU for real-time performance

### Method 3: SLAM + Visual Odometry (PROPOSED)

**Approach:**
- Simultaneous Localization and Mapping using drone camera
- Match drone images to satellite map using feature detection (SIFT/ORB)
- Estimate drone position through visual odometry
- Build local occupancy grid
- Use RRT* or D* Lite for dynamic path planning

**Advantages:**
- Continuous position tracking
- Adapts to terrain changes
- Works without GPS

**Disadvantages:**
- Complex implementation
- Drift accumulation over time
- Requires overlapping image sequences

## 📊 Results

The system successfully:
- ✅ Classifies terrain from satellite imagery
- ✅ Generates traversal cost maps
- ✅ Finds optimal paths using A* algorithm
- ✅ Analyzes drone images for local features
- ✅ Visualizes complete navigation solution
- ✅ Outputs path coordinates for drone guidance

### Sample Output

The visualization includes:
1. Original satellite image with computed path
2. Terrain classification map (color-coded)
3. Traversal cost heatmap
4. Path statistics and metrics

## 🗺️ Test Location

**Location:** Sundarbans Mangrove Forest, West Bengal, India
- **Coordinates:** 21.9497°N, 89.1833°E
- **Terrain:** Dense mangrove forest with water channels
- **Challenge:** Complex terrain with mixed vegetation density

## 📝 Usage Examples

### Custom Start/Goal Positions

```python
from jungle_navigator import JungleNavigator

# Initialize with your satellite image
navigator = JungleNavigator('data/satellite_image.png')

# Classify terrain
navigator.classify_terrain()
navigator.create_cost_map()

# Find path
start = (100, 100)  # (row, col)
goal = (500, 600)
path = navigator.astar_pathfinding(start, goal)

# Visualize
navigator.visualize_results(path, [], 'output/my_path.png')
```

### Analyze Drone Image

```python
# Analyze a single drone image
analysis = navigator.analyze_drone_image('data/drone_images/drone_image_01.png')
print(f"Vegetation density: {analysis['vegetation_density']:.2f}")
print(f"Traversable: {analysis['traversable']}")
```

## 🔧 Configuration

Key parameters you can adjust in `jungle_navigator.py`:

- **Terrain Classification Colors**: Adjust HSV ranges for different environments
- **Cost Values**: Modify traversal costs for terrain types
- **A* Heuristic**: Change heuristic function (Euclidean, Manhattan, etc.)
- **Start/Goal Positions**: Set custom waypoints

## 📈 Performance Metrics

- **Path Planning Speed**: ~0.5-2 seconds for 800x800 image
- **Memory Usage**: ~100-200 MB
- **Accuracy**: Depends on satellite image quality
- **Scalability**: Linear with image size

## 🛠️ Future Improvements

1. **Real-time GPS Integration**: Add GPS fallback when available
2. **Machine Learning Enhancement**: Train semantic segmentation model
3. **Obstacle Avoidance**: Add real-time obstacle detection from drone
4. **Weather Adaptation**: Account for weather conditions
5. **Multi-objective Optimization**: Balance distance, safety, and energy
6. **3D Terrain Analysis**: Incorporate elevation data

## 📚 References

- A* Algorithm: Hart, P. E.; Nilsson, N. J.; Raphael, B. (1968)
- Color-based Segmentation: Cheng, H. D., et al. (2001)
- Path Planning in Robotics: LaValle, S. M. (2006)

## 👤 Author

Created for the "Escape the Jungle" AI Navigation Challenge

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Google Maps API for satellite imagery
- OpenCV and scikit-image communities
- Path planning algorithm references
