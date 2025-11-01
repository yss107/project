"""Quick test to verify system functionality"""
from jungle_navigator import JungleNavigator
import os

print("="*50)
print("SYSTEM VALIDATION TEST")
print("="*50)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sat_path = os.path.join(base_dir, 'data', 'satellite_image.png')

print(f"\n1. Loading satellite image...")
nav = JungleNavigator(sat_path)
print(f"   ✅ Image loaded: {nav.width}x{nav.height} pixels")

print(f"\n2. Classifying terrain...")
nav.classify_terrain()
print(f"   ✅ Terrain classified")

print(f"\n3. Creating cost map...")
nav.create_cost_map()
print(f"   ✅ Cost map created")

print(f"\n4. Testing path planning...")
start = (100, 100)
goal = (200, 200)
print(f"   Finding path from {start} to {goal}...")
path = nav.astar_pathfinding(start, goal)

if path:
    print(f"   ✅ Path found with {len(path)} waypoints")
    print(f"\n{'='*50}")
    print("✅ ALL TESTS PASSED - SYSTEM OPERATIONAL")
    print(f"{'='*50}")
else:
    print(f"   ❌ No path found")
    print(f"\n{'='*50}")
    print("❌ TEST FAILED")
    print(f"{'='*50}")
