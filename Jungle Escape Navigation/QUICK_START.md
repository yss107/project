# Quick Start Guide - Jungle Escape Navigation

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd "Jungle Escape Navigation"
pip install -r requirements.txt
```

### Step 2: Generate Test Data
```bash
cd code
python data_acquisition.py
```
Press Enter when asked for API key to use simulated satellite imagery.

### Step 3: Run Navigation System
```bash
python jungle_navigator.py
```

## 📁 Output Files

After running, check these locations:
- **output/navigation_result.png** - Visual map with computed path
- **output/path_data.json** - Path coordinates in JSON format
- **data/satellite_image.png** - Satellite map used
- **data/drone_images/** - 8 simulated drone images

## 📊 Understanding the Results

The visualization shows 4 panels:

1. **Top-Left**: Satellite image with navigation path (red line)
   - Green dot = Start position
   - Red dot = Goal/Exit position
   - Yellow diamonds = Drone image locations

2. **Top-Right**: Terrain classification map
   - Dark green = Dense vegetation (avoid)
   - Light green = Light vegetation (moderate)
   - Tan = Clear paths (prefer)
   - Blue = Water bodies (avoid)

3. **Bottom-Left**: Cost map heatmap
   - Darker = Higher cost (difficult terrain)
   - Lighter = Lower cost (easier terrain)

4. **Bottom-Right**: Statistics and metrics
   - Path length and waypoints
   - Terrain distribution
   - Cost analysis

## 🔧 Customization

### Change Start/Goal Positions
Edit `jungle_navigator.py` around line 490:
```python
start = (50, 50)      # Change these coordinates
goal = (600, 600)     # (row, col) in pixels
```

### Use Real Satellite Imagery
Get a Google Maps API key from:
https://developers.google.com/maps/documentation/maps-static/get-api-key

Then run:
```bash
python data_acquisition.py
# Enter your API key when prompted
```

### Adjust Terrain Classification
Edit color ranges in `jungle_navigator.py` in the `classify_terrain()` method (lines 70-100).

## 📖 Full Documentation

See **README.md** for complete documentation including:
- Detailed method explanations
- Algorithm descriptions
- Configuration options
- API reference

See **report.pdf** for:
- Comprehensive technical analysis
- 3 proposed methods comparison
- Implementation details
- Results and validation

## 💡 Tips

1. **For faster results**: Use smaller images or reduce goal distance
2. **Better accuracy**: Use higher resolution satellite imagery
3. **Real drone data**: Replace simulated images with actual drone photos
4. **Custom terrain**: Modify color thresholds for different environments

## 🆘 Troubleshooting

**Problem**: "Could not load satellite image"
- Solution: Run `data_acquisition.py` first to generate test data

**Problem**: Path finding takes too long
- Solution: Reduce goal distance or use smaller image

**Problem**: No path found
- Solution: Check start/goal positions are in valid terrain (not water)

**Problem**: Import errors
- Solution: Run `pip install -r requirements.txt`

## 📞 Need Help?

Check the following files:
1. **README.md** - Usage instructions and examples
2. **report.pdf** - Technical details and methods
3. Code comments - Inline documentation in Python files

## ✅ Quick Test

Verify everything works:
```bash
cd code
python data_acquisition.py < /dev/null
python jungle_navigator.py
ls -lh ../output/
```

You should see:
- ✓ Satellite image generated
- ✓ 8 drone images created
- ✓ Path computed successfully
- ✓ Visualization saved

## 🎯 Next Steps

1. ✅ Review the generated visualization
2. ✅ Read the technical report (report.pdf)
3. ✅ Experiment with different start/goal positions
4. ✅ Try with real satellite imagery using Google API
5. ✅ Customize terrain classification for your use case

Enjoy navigating through the jungle! 🌳🗺️
