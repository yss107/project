"""
LiDAR data utilities for PhysicalAI-Autonomous-Vehicles dataset.

This module provides utilities for loading and processing LiDAR point cloud data,
including Draco-encoded point cloud decoding and visualization support.
"""

import io
import zipfile
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd
try:
    import DracoPy
    DRACO_AVAILABLE = True
except ImportError:
    DRACO_AVAILABLE = False
    print("Warning: DracoPy not available. LiDAR decoding will not work.")


class LiDARLoader:
    """
    Utility class for loading and processing LiDAR point cloud data.
    
    Handles Draco-encoded point clouds stored in Parquet format.
    """
    
    def __init__(self, dataset_root: str):
        """
        Initialize LiDAR loader.
        
        Args:
            dataset_root (str): Root directory of the dataset
        """
        self.dataset_root = Path(dataset_root)
        self.lidar_dir = self.dataset_root / 'lidar' / 'lidar_top_360fov'
        
        if not DRACO_AVAILABLE:
            raise ImportError(
                "DracoPy is required for LiDAR data loading. "
                "Install it with: pip install DracoPy"
            )
    
    def load_pointcloud(
        self, 
        clip_id: str,
        chunk_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load LiDAR point cloud data for a specific clip.
        
        Args:
            clip_id (str): UUID of the clip
            chunk_file (str, optional): Path to chunk file (auto-detected if None)
            
        Returns:
            pd.DataFrame: Point cloud data with columns:
                - spin_index: Spin number (0-199 for 20s clip at 10Hz)
                - reference_timestamp: Timestamp in microseconds
                - draco_encoded_pointcloud: Binary encoded point cloud
        """
        if chunk_file is None:
            chunk_file = self._find_chunk_for_clip(clip_id)
            if chunk_file is None:
                raise FileNotFoundError(f"Chunk file not found for clip {clip_id}")
        
        parquet_filename = f"{clip_id}.lidar_top360_fov.parquet"
        
        with zipfile.ZipFile(chunk_file, 'r') as zf:
            if parquet_filename not in zf.namelist():
                raise FileNotFoundError(f"LiDAR file not found in chunk: {parquet_filename}")
            
            parquet_bytes = zf.read(parquet_filename)
            
            # Read parquet from bytes
            pointcloud_df = pd.read_parquet(io.BytesIO(parquet_bytes))
        
        return pointcloud_df
    
    def decode_pointcloud(self, draco_bytes: bytes) -> np.ndarray:
        """
        Decode Draco-encoded point cloud to numpy array.
        
        Args:
            draco_bytes (bytes): Draco-encoded point cloud binary data
            
        Returns:
            np.ndarray: Decoded point cloud (N, 3+) where columns are typically
                       [x, y, z, intensity, ...]
        """
        if not DRACO_AVAILABLE:
            raise ImportError("DracoPy is required for point cloud decoding")
        
        # Decode using DracoPy
        point_cloud = DracoPy.decode(draco_bytes)
        
        # Convert to numpy array
        # The exact format depends on the Draco encoding
        points = np.column_stack([
            point_cloud.points,  # x, y, z coordinates
        ])
        
        # Add additional attributes if available
        if hasattr(point_cloud, 'intensity'):
            intensity = np.array(point_cloud.intensity).reshape(-1, 1)
            points = np.column_stack([points, intensity])
        
        return points
    
    def load_spin(
        self, 
        clip_id: str, 
        spin_idx: int,
        chunk_file: Optional[str] = None
    ) -> np.ndarray:
        """
        Load a single LiDAR spin as numpy array.
        
        Args:
            clip_id (str): UUID of the clip
            spin_idx (int): Spin index (0-199 for 20s clip)
            chunk_file (str, optional): Path to chunk file
            
        Returns:
            np.ndarray: Decoded point cloud for the spin
        """
        pointcloud_df = self.load_pointcloud(clip_id, chunk_file)
        
        # Filter for specific spin
        spin_data = pointcloud_df[pointcloud_df['spin_index'] == spin_idx]
        
        if spin_data.empty:
            raise ValueError(f"Spin index {spin_idx} not found in clip {clip_id}")
        
        # Decode the point cloud
        draco_bytes = spin_data.iloc[0]['draco_encoded_pointcloud']
        points = self.decode_pointcloud(draco_bytes)
        
        return points
    
    def load_all_spins(
        self, 
        clip_id: str,
        chunk_file: Optional[str] = None,
        decoded: bool = True
    ) -> list:
        """
        Load all LiDAR spins for a clip.
        
        Args:
            clip_id (str): UUID of the clip
            chunk_file (str, optional): Path to chunk file
            decoded (bool): If True, decode all spins; if False, return raw data
            
        Returns:
            list: List of point clouds (if decoded) or raw dataframe rows
        """
        pointcloud_df = self.load_pointcloud(clip_id, chunk_file)
        
        if not decoded:
            return pointcloud_df
        
        spins = []
        for idx, row in pointcloud_df.iterrows():
            draco_bytes = row['draco_encoded_pointcloud']
            points = self.decode_pointcloud(draco_bytes)
            spins.append(points)
        
        return spins
    
    def _find_chunk_for_clip(self, clip_id: str) -> Optional[str]:
        """
        Find which chunk file contains the clip.
        
        Args:
            clip_id (str): UUID of the clip
            
        Returns:
            str: Path to chunk file or None if not found
        """
        if not self.lidar_dir.exists():
            return None
        
        chunk_files = sorted(self.lidar_dir.glob('lidar_top_360fov_clip_*.zip'))
        
        for chunk_file in chunk_files:
            try:
                with zipfile.ZipFile(chunk_file, 'r') as zf:
                    file_list = zf.namelist()
                    for file_name in file_list:
                        if clip_id in file_name:
                            return str(chunk_file)
            except Exception:
                continue
        
        return None
    
    def get_pointcloud_stats(
        self, 
        clip_id: str,
        chunk_file: Optional[str] = None
    ) -> dict:
        """
        Get statistics about a point cloud without full decoding.
        
        Args:
            clip_id (str): UUID of the clip
            chunk_file (str, optional): Path to chunk file
            
        Returns:
            dict: Statistics including number of spins, timestamps, etc.
        """
        pointcloud_df = self.load_pointcloud(clip_id, chunk_file)
        
        stats = {
            'num_spins': len(pointcloud_df),
            'spin_indices': pointcloud_df['spin_index'].tolist(),
            'start_timestamp': pointcloud_df['reference_timestamp'].min(),
            'end_timestamp': pointcloud_df['reference_timestamp'].max(),
            'duration_us': pointcloud_df['reference_timestamp'].max() - 
                          pointcloud_df['reference_timestamp'].min(),
            'avg_spin_rate_hz': len(pointcloud_df) / 
                               ((pointcloud_df['reference_timestamp'].max() - 
                                 pointcloud_df['reference_timestamp'].min()) / 1e6)
        }
        
        return stats
    
    def extract_bounding_box(
        self, 
        points: np.ndarray,
        x_range: Optional[Tuple[float, float]] = None,
        y_range: Optional[Tuple[float, float]] = None,
        z_range: Optional[Tuple[float, float]] = None
    ) -> np.ndarray:
        """
        Extract points within a bounding box.
        
        Args:
            points (np.ndarray): Point cloud array (N, 3+)
            x_range (tuple, optional): (min_x, max_x)
            y_range (tuple, optional): (min_y, max_y)
            z_range (tuple, optional): (min_z, max_z)
            
        Returns:
            np.ndarray: Filtered points
        """
        mask = np.ones(len(points), dtype=bool)
        
        if x_range is not None:
            mask &= (points[:, 0] >= x_range[0]) & (points[:, 0] <= x_range[1])
        
        if y_range is not None:
            mask &= (points[:, 1] >= y_range[0]) & (points[:, 1] <= y_range[1])
        
        if z_range is not None:
            mask &= (points[:, 2] >= z_range[0]) & (points[:, 2] <= z_range[1])
        
        return points[mask]
    
    def downsample_pointcloud(
        self, 
        points: np.ndarray,
        voxel_size: float = 0.1
    ) -> np.ndarray:
        """
        Downsample point cloud using voxel grid filtering.
        
        Args:
            points (np.ndarray): Point cloud array (N, 3+)
            voxel_size (float): Size of voxel grid
            
        Returns:
            np.ndarray: Downsampled points
        """
        # Simple voxel grid downsampling
        voxel_indices = np.floor(points[:, :3] / voxel_size).astype(int)
        
        # Get unique voxels
        unique_voxels, inverse_indices = np.unique(
            voxel_indices, axis=0, return_inverse=True
        )
        
        # Average points in each voxel
        downsampled = []
        for i in range(len(unique_voxels)):
            voxel_mask = inverse_indices == i
            voxel_points = points[voxel_mask]
            downsampled.append(voxel_points.mean(axis=0))
        
        return np.array(downsampled)


if __name__ == "__main__":
    print("LiDAR utilities for PhysicalAI-Autonomous-Vehicles dataset")
    print("Usage: from utils.lidar_utils import LiDARLoader")
    print(f"DracoPy available: {DRACO_AVAILABLE}")
