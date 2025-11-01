"""
Data Acquisition Script for Jungle Navigation
Downloads satellite imagery and simulates drone flight paths
"""

import requests
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2
from typing import List, Tuple


class DataAcquisition:
    """Handles downloading and simulating imagery for jungle navigation."""
    
    def __init__(self, data_dir: str):
        """
        Initialize data acquisition.
        
        Args:
            data_dir: Directory to save downloaded data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'drone_images'), exist_ok=True)
    
    def download_satellite_image(self, location: Tuple[float, float], 
                                 zoom: int = 15, 
                                 size: str = "640x640",
                                 api_key: str = None) -> str:
        """
        Download satellite image from Google Static Maps API.
        
        Args:
            location: (latitude, longitude) tuple
            zoom: Zoom level (1-20)
            size: Image size as "widthxheight"
            api_key: Google Maps API key
            
        Returns:
            Path to saved image
        """
        if api_key is None:
            print("No API key provided. Please provide Google Maps API key.")
            print("You can get one from: https://developers.google.com/maps/documentation/maps-static/get-api-key")
            print("\nFor now, creating a simulated satellite image...")
            return self.create_simulated_satellite_image()
        
        lat, lon = location
        url = f"https://maps.googleapis.com/maps/api/staticmap"
        params = {
            'center': f"{lat},{lon}",
            'zoom': zoom,
            'size': size,
            'maptype': 'satellite',
            'key': api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            output_path = os.path.join(self.data_dir, 'satellite_image.png')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Satellite image downloaded successfully: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Error downloading satellite image: {e}")
            print("Creating simulated image instead...")
            return self.create_simulated_satellite_image()
    
    def create_simulated_satellite_image(self, size: Tuple[int, int] = (800, 800)) -> str:
        """
        Create a simulated satellite image of jungle terrain.
        
        Args:
            size: Image size (width, height)
            
        Returns:
            Path to saved image
        """
        print("Creating simulated satellite image of jungle terrain...")
        
        width, height = size
        
        # Create base image with varying green tones
        img = np.random.randint(20, 80, (height, width, 3), dtype=np.uint8)
        img[:, :, 1] = np.random.randint(60, 120, (height, width))  # More green
        
        # Add some darker dense vegetation areas (patches)
        for _ in range(15):
            cx, cy = np.random.randint(0, width), np.random.randint(0, height)
            radius = np.random.randint(50, 150)
            y, x = np.ogrid[-cy:height-cy, -cx:width-cx]
            mask = x*x + y*y <= radius*radius
            img[mask] = img[mask] * 0.4  # Darker
        
        # Add lighter vegetation patches
        for _ in range(20):
            cx, cy = np.random.randint(0, width), np.random.randint(0, height)
            radius = np.random.randint(30, 80)
            y, x = np.ogrid[-cy:height-cy, -cx:width-cx]
            mask = x*x + y*y <= radius*radius
            if mask.any():
                img[mask, 1] = np.clip(img[mask, 1] * 1.5, 0, 255)  # Brighter green
        
        # Add some clear paths/trails (lighter brown areas)
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        
        # Create a winding path
        path_points = []
        x, y = 50, 50
        for i in range(20):
            x += np.random.randint(-30, 50)
            y += np.random.randint(-30, 50)
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            path_points.append((x, y))
        
        # Draw path
        for i in range(len(path_points) - 1):
            draw.line([path_points[i], path_points[i+1]], fill=(139, 119, 101), width=15)
        
        # Add some water bodies (blue)
        for _ in range(3):
            cx, cy = np.random.randint(100, width-100), np.random.randint(100, height-100)
            radius = np.random.randint(30, 60)
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                        fill=(70, 130, 180), outline=(50, 110, 160))
        
        # Apply slight blur for realism
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Add texture
        img_array = np.array(pil_img)
        noise = np.random.randint(-10, 10, img_array.shape, dtype=np.int16)
        img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        output_path = os.path.join(self.data_dir, 'satellite_image.png')
        Image.fromarray(img_array).save(output_path)
        
        print(f"Simulated satellite image saved: {output_path}")
        return output_path
    
    def simulate_drone_images(self, satellite_image_path: str, 
                             flight_path: List[Tuple[int, int]],
                             crop_size: int = 200) -> List[str]:
        """
        Simulate drone images by cropping regions from satellite image.
        
        Args:
            satellite_image_path: Path to satellite image
            flight_path: List of (row, col) positions for drone
            crop_size: Size of crop around each position
            
        Returns:
            List of paths to saved drone images
        """
        print(f"Simulating {len(flight_path)} drone images along flight path...")
        
        satellite_img = cv2.imread(satellite_image_path)
        if satellite_img is None:
            print(f"Error: Could not load satellite image from {satellite_image_path}")
            return []
        
        height, width = satellite_img.shape[:2]
        drone_image_paths = []
        
        for i, (row, col) in enumerate(flight_path):
            # Calculate crop boundaries
            half_size = crop_size // 2
            r1 = max(0, row - half_size)
            r2 = min(height, row + half_size)
            c1 = max(0, col - half_size)
            c2 = min(width, col + half_size)
            
            # Crop region
            crop = satellite_img[r1:r2, c1:c2].copy()
            
            # Add some noise and blur to simulate drone camera
            noise = np.random.randint(-15, 15, crop.shape, dtype=np.int16)
            crop = np.clip(crop.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            crop = cv2.GaussianBlur(crop, (3, 3), 0)
            
            # Add vignette effect
            rows, cols = crop.shape[:2]
            kernel_x = cv2.getGaussianKernel(cols, cols/2)
            kernel_y = cv2.getGaussianKernel(rows, rows/2)
            kernel = kernel_y * kernel_x.T
            mask = kernel / kernel.max()
            crop = (crop * np.expand_dims(mask, axis=2)).astype(np.uint8)
            
            # Save drone image
            output_path = os.path.join(self.data_dir, 'drone_images', f'drone_image_{i+1:02d}.png')
            cv2.imwrite(output_path, crop)
            drone_image_paths.append(output_path)
        
        print(f"Saved {len(drone_image_paths)} drone images")
        return drone_image_paths
    
    def generate_sample_flight_path(self, img_height: int, img_width: int, 
                                   num_points: int = 8) -> List[Tuple[int, int]]:
        """
        Generate a sample flight path across the image.
        
        Args:
            img_height: Height of the image
            img_width: Width of the image
            num_points: Number of waypoints
            
        Returns:
            List of (row, col) positions
        """
        # Create a path from top-left to bottom-right with some variation
        path = []
        for i in range(num_points):
            progress = i / (num_points - 1)
            
            # Base position along diagonal
            row = int(progress * (img_height - 100)) + 50
            col = int(progress * (img_width - 100)) + 50
            
            # Add some randomness
            if i > 0 and i < num_points - 1:
                row += np.random.randint(-50, 50)
                col += np.random.randint(-50, 50)
            
            path.append((row, col))
        
        return path


def main():
    """Main function to acquire all necessary data."""
    
    print("="*60)
    print("DATA ACQUISITION FOR JUNGLE NAVIGATION")
    print("="*60)
    print()
    
    # Set up paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Initialize data acquisition
    data_acq = DataAcquisition(data_dir)
    
    # Example location: Sundarbans, West Bengal, India (dense mangrove forest)
    # Location coordinates
    location = (21.9497, 89.1833)  # Sundarbans
    
    print("Target Location: Sundarbans Mangrove Forest, India")
    print(f"Coordinates: {location[0]:.4f}°N, {location[1]:.4f}°E")
    print()
    
    # Option 1: Download from Google Maps API (requires API key)
    api_key = input("Enter your Google Maps API key (or press Enter to use simulated image): ").strip()
    
    if api_key:
        satellite_path = data_acq.download_satellite_image(location, zoom=15, api_key=api_key)
    else:
        satellite_path = data_acq.create_simulated_satellite_image()
    
    # Load satellite image to get dimensions
    satellite_img = cv2.imread(satellite_path)
    if satellite_img is not None:
        height, width = satellite_img.shape[:2]
        
        # Generate flight path
        print(f"\nGenerating drone flight path...")
        flight_path = data_acq.generate_sample_flight_path(height, width, num_points=8)
        
        # Simulate drone images
        drone_paths = data_acq.simulate_drone_images(satellite_path, flight_path)
        
        print(f"\n{'='*60}")
        print("DATA ACQUISITION COMPLETE!")
        print(f"  - Satellite image: {satellite_path}")
        print(f"  - Drone images: {len(drone_paths)} images in {os.path.join(data_dir, 'drone_images')}")
        print(f"{'='*60}")
    else:
        print("Error: Could not load satellite image")


if __name__ == "__main__":
    main()
