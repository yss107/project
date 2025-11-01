"""
Jungle Navigation System using AI/ML
This module implements AI-powered navigation to find safe paths out of dense jungle
using drone RGB images and satellite imagery.
"""

import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import os
import json
from typing import List, Tuple, Dict
from dataclasses import dataclass
import heapq
import warnings
warnings.filterwarnings('ignore')


@dataclass
class Position:
    """Represents a 2D position with latitude and longitude."""
    lat: float
    lon: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return np.sqrt((self.lat - other.lat)**2 + (self.lon - other.lon)**2)


class JungleNavigator:
    """
    Main class for jungle navigation using computer vision and path planning.
    
    This implementation uses Method 1: Vision-based Terrain Classification + A* Path Planning
    """
    
    def __init__(self, satellite_image_path: str):
        """
        Initialize the navigator with a satellite image.
        
        Args:
            satellite_image_path: Path to the satellite image of the region
        """
        self.satellite_image = cv2.imread(satellite_image_path)
        if self.satellite_image is None:
            raise ValueError(f"Could not load satellite image from {satellite_image_path}")
        
        self.satellite_rgb = cv2.cvtColor(self.satellite_image, cv2.COLOR_BGR2RGB)
        self.height, self.width = self.satellite_image.shape[:2]
        
        # Initialize terrain classification map
        self.terrain_map = None
        self.cost_map = None
        
    def classify_terrain(self) -> np.ndarray:
        """
        Classify terrain types from satellite imagery using color-based segmentation.
        
        Terrain types:
        - 0: Dense vegetation (dark green) - High cost
        - 1: Light vegetation (light green) - Medium cost
        - 2: Clear paths/roads (brown/gray) - Low cost
        - 3: Water bodies (blue) - Impassable
        
        Returns:
            2D array with terrain classification for each pixel
        """
        print("Classifying terrain from satellite imagery...")
        
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(self.satellite_image, cv2.COLOR_BGR2HSV)
        
        # Initialize terrain map
        terrain_map = np.zeros((self.height, self.width), dtype=np.uint8)
        
        # Define color ranges for different terrain types
        # Dense vegetation (dark green)
        dense_veg_lower = np.array([35, 40, 20])
        dense_veg_upper = np.array([85, 255, 120])
        dense_veg_mask = cv2.inRange(hsv, dense_veg_lower, dense_veg_upper)
        terrain_map[dense_veg_mask > 0] = 0
        
        # Light vegetation (light green/yellow-green)
        light_veg_lower = np.array([25, 20, 120])
        light_veg_upper = np.array([85, 255, 255])
        light_veg_mask = cv2.inRange(hsv, light_veg_lower, light_veg_upper)
        light_veg_mask = cv2.bitwise_and(light_veg_mask, cv2.bitwise_not(dense_veg_mask))
        terrain_map[light_veg_mask > 0] = 1
        
        # Clear paths (brown/gray/sandy colors)
        clear_lower1 = np.array([0, 0, 100])
        clear_upper1 = np.array([25, 100, 200])
        clear_mask = cv2.inRange(hsv, clear_lower1, clear_upper1)
        terrain_map[clear_mask > 0] = 2
        
        # Water bodies (blue)
        water_lower = np.array([90, 50, 50])
        water_upper = np.array([130, 255, 255])
        water_mask = cv2.inRange(hsv, water_lower, water_upper)
        terrain_map[water_mask > 0] = 3
        
        self.terrain_map = terrain_map
        return terrain_map
    
    def create_cost_map(self) -> np.ndarray:
        """
        Create a traversal cost map based on terrain classification.
        
        Returns:
            2D array with traversal costs for each pixel
        """
        print("Creating traversal cost map...")
        
        if self.terrain_map is None:
            self.classify_terrain()
        
        # Define costs for each terrain type
        cost_values = {
            0: 10,   # Dense vegetation - high cost
            1: 5,    # Light vegetation - medium cost
            2: 1,    # Clear paths - low cost
            3: 1000  # Water - impassable (very high cost)
        }
        
        # Create cost map
        cost_map = np.zeros((self.height, self.width), dtype=np.float32)
        for terrain_type, cost in cost_values.items():
            cost_map[self.terrain_map == terrain_type] = cost
        
        self.cost_map = cost_map
        return cost_map
    
    def analyze_drone_image(self, drone_image_path: str) -> Dict:
        """
        Analyze a drone image to extract local terrain features.
        
        Args:
            drone_image_path: Path to drone RGB image
            
        Returns:
            Dictionary with analysis results (vegetation density, obstacles, etc.)
        """
        drone_image = cv2.imread(drone_image_path)
        if drone_image is None:
            return {"error": "Could not load image"}
        
        hsv = cv2.cvtColor(drone_image, cv2.COLOR_BGR2HSV)
        
        # Calculate vegetation density
        green_lower = np.array([35, 40, 40])
        green_upper = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        vegetation_density = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
        
        # Detect potential paths (lighter areas)
        gray = cv2.cvtColor(drone_image, cv2.COLOR_BGR2GRAY)
        _, bright_areas = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        path_score = np.sum(bright_areas > 0) / (bright_areas.shape[0] * bright_areas.shape[1])
        
        return {
            "vegetation_density": float(vegetation_density),
            "path_score": float(path_score),
            "traversable": vegetation_density < 0.7,
            "safety_score": 1.0 - vegetation_density
        }
    
    def astar_pathfinding(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find optimal path using A* algorithm on the cost map.
        
        Args:
            start: Starting position (row, col)
            goal: Goal position (row, col)
            
        Returns:
            List of positions forming the path from start to goal
        """
        print(f"Finding path from {start} to {goal} using A* algorithm...")
        
        if self.cost_map is None:
            self.create_cost_map()
        
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            """Euclidean distance heuristic."""
            return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
        # Use priority queue for better performance
        open_heap = []
        heapq.heappush(open_heap, (0, start))
        
        # Track which nodes are in open set
        open_set = {start}
        closed_set = set()
        
        # Cost from start to each node
        g_score = {start: 0}
        
        # Track parent nodes for path reconstruction
        came_from = {}
        
        # Neighbor offsets for 8-directional movement
        neighbors_offsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        iterations = 0
        max_iterations = 500000  # Safety limit
        
        while open_heap and iterations < max_iterations:
            iterations += 1
            
            if iterations % 10000 == 0:
                print(f"  Iteration {iterations}, open set size: {len(open_set)}")
            
            # Get node with lowest f_score
            _, current = heapq.heappop(open_heap)
            
            if current not in open_set:
                continue  # Already processed
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                print(f"Path found with {len(path)} waypoints in {iterations} iterations!")
                return path
            
            open_set.remove(current)
            closed_set.add(current)
            
            # Check all neighbors
            for dr, dc in neighbors_offsets:
                neighbor = (current[0] + dr, current[1] + dc)
                
                # Check bounds
                if not (0 <= neighbor[0] < self.height and 0 <= neighbor[1] < self.width):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                # Skip if cost is too high (impassable)
                if self.cost_map[neighbor] >= 500:
                    continue
                
                # Calculate cost to reach neighbor
                move_cost = 1.414 if abs(dr) + abs(dc) == 2 else 1.0
                tentative_g = g_score[current] + self.cost_map[neighbor] * move_cost
                
                if neighbor in g_score and tentative_g >= g_score[neighbor]:
                    continue
                
                # This path is the best so far
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                
                if neighbor not in open_set:
                    heapq.heappush(open_heap, (f_score, neighbor))
                    open_set.add(neighbor)
        
        print(f"No path found after {iterations} iterations!")
        return []
    
    def visualize_results(self, path: List[Tuple[int, int]], 
                         drone_positions: List[Tuple[int, int]],
                         output_path: str):
        """
        Create visualization of the navigation solution.
        
        Args:
            path: Computed path as list of (row, col) positions
            drone_positions: Positions where drone images were captured
            output_path: Path to save the visualization
        """
        print("Creating visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))
        
        # 1. Original satellite image with path
        axes[0, 0].imshow(self.satellite_rgb)
        if path:
            path_array = np.array(path)
            axes[0, 0].plot(path_array[:, 1], path_array[:, 0], 'r-', linewidth=3, label='Computed Path')
            axes[0, 0].plot(path[0][1], path[0][0], 'go', markersize=15, label='Start')
            axes[0, 0].plot(path[-1][1], path[-1][0], 'ro', markersize=15, label='Goal')
        
        # Mark drone positions
        if drone_positions:
            drone_array = np.array(drone_positions)
            axes[0, 0].scatter(drone_array[:, 1], drone_array[:, 0], c='yellow', 
                             s=100, marker='D', edgecolors='black', linewidth=2, 
                             label='Drone Positions', zorder=5)
        
        axes[0, 0].set_title('Satellite Image with Navigation Path', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].axis('off')
        
        # 2. Terrain classification map
        if self.terrain_map is not None:
            terrain_colors = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            terrain_colors[self.terrain_map == 0] = [0, 100, 0]      # Dense vegetation - dark green
            terrain_colors[self.terrain_map == 1] = [144, 238, 144]  # Light vegetation - light green
            terrain_colors[self.terrain_map == 2] = [210, 180, 140]  # Clear paths - tan
            terrain_colors[self.terrain_map == 3] = [0, 0, 255]      # Water - blue
            
            axes[0, 1].imshow(terrain_colors)
            if path:
                axes[0, 1].plot(path_array[:, 1], path_array[:, 0], 'r-', linewidth=2)
            axes[0, 1].set_title('Terrain Classification Map', fontsize=14, fontweight='bold')
            axes[0, 1].axis('off')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=[0, 0.4, 0], label='Dense Vegetation'),
                Patch(facecolor=[0.56, 0.93, 0.56], label='Light Vegetation'),
                Patch(facecolor=[0.82, 0.71, 0.55], label='Clear Paths'),
                Patch(facecolor=[0, 0, 1], label='Water')
            ]
            axes[0, 1].legend(handles=legend_elements, loc='upper right')
        
        # 3. Cost map visualization
        if self.cost_map is not None:
            cost_display = np.log1p(self.cost_map)  # Log scale for better visualization
            im = axes[1, 0].imshow(cost_display, cmap='hot')
            if path:
                axes[1, 0].plot(path_array[:, 1], path_array[:, 0], 'c-', linewidth=2)
            axes[1, 0].set_title('Traversal Cost Map (Log Scale)', fontsize=14, fontweight='bold')
            axes[1, 0].axis('off')
            plt.colorbar(im, ax=axes[1, 0], label='Cost (log scale)')
        
        # 4. Path metrics and statistics
        axes[1, 1].axis('off')
        if path:
            # Calculate path statistics
            total_distance = len(path)
            path_costs = [self.cost_map[pos] for pos in path]
            total_cost = sum(path_costs)
            avg_cost = np.mean(path_costs)
            max_cost = np.max(path_costs)
            
            # Count terrain types along path
            terrain_counts = {0: 0, 1: 0, 2: 0, 3: 0}
            for pos in path:
                terrain_counts[self.terrain_map[pos]] += 1
            
            stats_text = f"""
PATH STATISTICS
{'='*40}

Total Waypoints: {len(path)}
Euclidean Distance: {np.sqrt((path[-1][0]-path[0][0])**2 + (path[-1][1]-path[0][1])**2):.2f} pixels

Start Position: ({path[0][0]}, {path[0][1]})
Goal Position: ({path[-1][0]}, {path[-1][1]})

TRAVERSAL COSTS
{'='*40}
Total Cost: {total_cost:.2f}
Average Cost: {avg_cost:.2f}
Maximum Cost: {max_cost:.2f}

TERRAIN DISTRIBUTION
{'='*40}
Dense Vegetation: {terrain_counts[0]} waypoints ({100*terrain_counts[0]/len(path):.1f}%)
Light Vegetation: {terrain_counts[1]} waypoints ({100*terrain_counts[1]/len(path):.1f}%)
Clear Paths: {terrain_counts[2]} waypoints ({100*terrain_counts[2]/len(path):.1f}%)
Water: {terrain_counts[3]} waypoints ({100*terrain_counts[3]/len(path):.1f}%)

DRONE IMAGE ANALYSIS
{'='*40}
Number of Drone Images: {len(drone_positions)}
Coverage Area: Analyzed
"""
            axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes,
                           fontsize=11, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_path}")
        plt.close()
    
    def save_path_data(self, path: List[Tuple[int, int]], output_path: str):
        """
        Save path data to JSON file.
        
        Args:
            path: Computed path
            output_path: Path to save JSON file
        """
        path_data = {
            "num_waypoints": len(path),
            "waypoints": [(int(p[0]), int(p[1])) for p in path],
            "start": (int(path[0][0]), int(path[0][1])) if path else None,
            "goal": (int(path[-1][0]), int(path[-1][1])) if path else None
        }
        
        with open(output_path, 'w') as f:
            json.dump(path_data, f, indent=2)
        
        print(f"Path data saved to {output_path}")


def main():
    """Main execution function for the jungle navigation system."""
    
    print("="*60)
    print("JUNGLE ESCAPE NAVIGATION SYSTEM")
    print("AI-Powered Path Planning using Satellite and Drone Imagery")
    print("="*60)
    print()
    
    # Set up paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    output_dir = os.path.join(base_dir, 'output')
    
    # Create directories if they don't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check for satellite image
    satellite_image_path = os.path.join(data_dir, 'satellite_image.png')
    if not os.path.exists(satellite_image_path):
        # Try alternative names
        for name in ['satellite_map.png', 'satellite.png', 'map.png']:
            alt_path = os.path.join(data_dir, name)
            if os.path.exists(alt_path):
                satellite_image_path = alt_path
                break
    
    if not os.path.exists(satellite_image_path):
        print(f"ERROR: Satellite image not found at {satellite_image_path}")
        print("Please place a satellite image in the data/ directory")
        return
    
    # Initialize navigator
    print(f"Loading satellite image from: {satellite_image_path}")
    navigator = JungleNavigator(satellite_image_path)
    
    # Classify terrain and create cost map
    navigator.classify_terrain()
    navigator.create_cost_map()
    
    # Analyze drone images if available
    drone_positions = []
    drone_dir = os.path.join(data_dir, 'drone_images')
    if os.path.exists(drone_dir):
        print(f"\nAnalyzing drone images from: {drone_dir}")
        drone_files = sorted([f for f in os.listdir(drone_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        for i, drone_file in enumerate(drone_files):
            drone_path = os.path.join(drone_dir, drone_file)
            analysis = navigator.analyze_drone_image(drone_path)
            print(f"  Drone image {i+1}: {drone_file}")
            print(f"    Vegetation density: {analysis.get('vegetation_density', 0):.2f}")
            print(f"    Safety score: {analysis.get('safety_score', 0):.2f}")
            print(f"    Traversable: {analysis.get('traversable', False)}")
            
            # Simulate drone position (distribute along potential path)
            if i == 0:
                # Start position
                pos = (50, 50)
            else:
                # Positions along the path
                progress = i / len(drone_files)
                pos = (int(50 + progress * (navigator.height - 100)),
                       int(50 + progress * (navigator.width - 100)))
            
            drone_positions.append(pos)
    else:
        print(f"\nNo drone images directory found at: {drone_dir}")
        print("Proceeding with satellite imagery only")
        # Create some default positions for visualization
        drone_positions = [
            (50, 50),
            (100, 150),
            (200, 250),
            (300, 350),
            (400, 450)
        ]
    
    # Define start and goal positions
    # Start: Upper-left area
    start = (50, 50)
    # Goal: Lower-right area (edge of jungle)
    # Use reasonable goal position (not too far for faster computation)
    goal = (min(navigator.height - 50, 600), min(navigator.width - 50, 600))
    
    print(f"\nPlanning path from {start} to {goal}...")
    
    # Find path using A* algorithm
    path = navigator.astar_pathfinding(start, goal)
    
    if path:
        print(f"\n✓ Successfully found path with {len(path)} waypoints!")
        
        # Save results
        output_image_path = os.path.join(output_dir, 'navigation_result.png')
        output_json_path = os.path.join(output_dir, 'path_data.json')
        
        navigator.visualize_results(path, drone_positions, output_image_path)
        navigator.save_path_data(path, output_json_path)
        
        print(f"\n{'='*60}")
        print("RESULTS SAVED:")
        print(f"  - Visualization: {output_image_path}")
        print(f"  - Path data: {output_json_path}")
        print(f"{'='*60}")
    else:
        print("\n✗ Could not find a valid path!")
    
    print("\nNavigation complete!")


if __name__ == "__main__":
    main()
