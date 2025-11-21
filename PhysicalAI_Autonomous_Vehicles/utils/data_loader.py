"""
Main data loader for PhysicalAI-Autonomous-Vehicles dataset.

This module provides the primary interface for loading and accessing
various sensor data, metadata, and calibration information from the dataset.
"""

import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
from tqdm import tqdm


class DatasetLoader:
    """
    Main loader class for the PhysicalAI-Autonomous-Vehicles dataset.
    
    This class provides convenient methods to load camera videos, LiDAR point clouds,
    radar data, calibration files, and metadata from the dataset.
    
    Attributes:
        data_root (Path): Root directory of the dataset
        camera_types (List[str]): Available camera sensor types
        radar_types (List[str]): Available radar sensor types
    """
    
    # Define available sensor types
    CAMERA_TYPES = [
        'camera_cross_left_120fov',
        'camera_cross_right_120fov',
        'camera_front_wide_120fov',
        'camera_front_tele_30fov',
        'camera_rear_left_70fov',
        'camera_rear_right_70fov',
        'camera_rear_tele_30fov'
    ]
    
    RADAR_TYPES = [
        'radar_corner_front_left_srr_0',
        'radar_corner_front_left_srr_3',
        'radar_corner_front_right_srr_0',
        'radar_corner_front_right_srr_3',
        'radar_corner_rear_left_srr_0',
        'radar_corner_rear_left_srr_3',
        'radar_corner_rear_right_srr_0',
        'radar_corner_rear_right_srr_3',
        'radar_front_center_imaging_lrr_1',
        'radar_front_center_mrr_2',
        'radar_front_center_srr_0',
        'radar_rear_left_mrr_2',
        'radar_rear_left_srr_0',
        'radar_rear_right_mrr_2',
        'radar_rear_right_srr_0',
        'radar_side_left_srr_0',
        'radar_side_left_srr_3',
        'radar_side_right_srr_0',
        'radar_side_right_srr_3'
    ]
    
    def __init__(self, data_root: str):
        """
        Initialize the dataset loader.
        
        Args:
            data_root (str): Path to the root directory of the dataset
        """
        self.data_root = Path(data_root)
        if not self.data_root.exists():
            raise ValueError(f"Dataset root directory does not exist: {data_root}")
        
        self.camera_types = self.CAMERA_TYPES
        self.radar_types = self.RADAR_TYPES
        
    def load_metadata(self, metadata_type: str = 'data_collection') -> pd.DataFrame:
        """
        Load metadata parquet file.
        
        Args:
            metadata_type (str): Type of metadata to load. Options:
                - 'data_collection': Collection metadata (country, month, hour, etc.)
                - 'sensor_presence': Sensor availability per clip
                
        Returns:
            pd.DataFrame: Metadata dataframe
        """
        metadata_path = self.data_root / 'metadata' / f'{metadata_type}.parquet'
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        return pd.read_parquet(metadata_path)
    
    def load_sensor_presence(self) -> pd.DataFrame:
        """
        Load sensor presence metadata.
        
        Returns:
            pd.DataFrame: Sensor presence information for all clips
        """
        return self.load_metadata('sensor_presence')
    
    def load_data_collection_metadata(self) -> pd.DataFrame:
        """
        Load data collection metadata.
        
        Returns:
            pd.DataFrame: Data collection metadata (country, time, platform)
        """
        return self.load_metadata('data_collection')
    
    def filter_clips(
        self,
        country: Optional[str] = None,
        month: Optional[int] = None,
        hour_range: Optional[Tuple[int, int]] = None,
        radar_config: Optional[str] = None,
        camera_required: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter clips based on various criteria.
        
        Args:
            country (str, optional): Filter by country name
            month (int, optional): Filter by month (1-12)
            hour_range (tuple, optional): Filter by hour range (start, end)
            radar_config (str, optional): Filter by radar config ('NA', 'low', 'med', 'high')
            camera_required (str, optional): Require specific camera sensor
            
        Returns:
            pd.DataFrame: Filtered clip metadata
        """
        # Load both metadata types
        collection_meta = self.load_data_collection_metadata()
        sensor_meta = self.load_sensor_presence()
        
        # Merge on clip_id
        merged = pd.merge(collection_meta, sensor_meta, on='clip_id', how='inner')
        
        # Apply filters
        if country is not None:
            merged = merged[merged['country'] == country]
        
        if month is not None:
            merged = merged[merged['month'] == month]
        
        if hour_range is not None:
            start_hour, end_hour = hour_range
            merged = merged[
                (merged['hour_of_day'] >= start_hour) & 
                (merged['hour_of_day'] <= end_hour)
            ]
        
        if radar_config is not None:
            merged = merged[merged['radar_config'] == radar_config]
        
        if camera_required is not None:
            if camera_required not in self.camera_types:
                raise ValueError(f"Invalid camera type: {camera_required}")
            merged = merged[merged[camera_required] == True]
        
        return merged
    
    def get_clip_info(self, clip_id: str) -> Dict:
        """
        Get comprehensive information about a specific clip.
        
        Args:
            clip_id (str): UUID of the clip
            
        Returns:
            dict: Dictionary containing all metadata for the clip
        """
        collection_meta = self.load_data_collection_metadata()
        sensor_meta = self.load_sensor_presence()
        
        clip_collection = collection_meta[collection_meta['clip_id'] == clip_id]
        clip_sensor = sensor_meta[sensor_meta['clip_id'] == clip_id]
        
        if clip_collection.empty:
            raise ValueError(f"Clip ID not found: {clip_id}")
        
        info = {
            **clip_collection.iloc[0].to_dict(),
            **clip_sensor.iloc[0].to_dict()
        }
        
        return info
    
    def find_chunk_for_clip(
        self, 
        clip_id: str, 
        sensor_type: str,
        sensor_name: str
    ) -> Optional[str]:
        """
        Find which chunk file contains a specific clip for a given sensor.
        
        Args:
            clip_id (str): UUID of the clip
            sensor_type (str): Type of sensor ('camera', 'lidar', 'radar')
            sensor_name (str): Specific sensor name
            
        Returns:
            str: Path to the chunk file containing the clip, or None if not found
        """
        sensor_dir = self.data_root / sensor_type / sensor_name
        
        if not sensor_dir.exists():
            return None
        
        # Search through chunk files
        chunk_files = sorted(sensor_dir.glob('*.zip'))
        
        for chunk_file in chunk_files:
            try:
                with zipfile.ZipFile(chunk_file, 'r') as zf:
                    # Check if clip exists in this chunk
                    file_list = zf.namelist()
                    for file_name in file_list:
                        if clip_id in file_name:
                            return str(chunk_file)
            except Exception as e:
                print(f"Error reading chunk {chunk_file}: {e}")
                continue
        
        return None
    
    def load_calibration(
        self, 
        calib_type: str, 
        clip_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load calibration data.
        
        Args:
            calib_type (str): Type of calibration ('camera_intrinsics', 
                             'sensor_extrinsics', 'vehicle_dimensions')
            clip_id (str, optional): Specific clip ID to load calibration for
            
        Returns:
            pd.DataFrame: Calibration data
        """
        calib_path = self.data_root / 'calibration' / f'{calib_type}.parquet'
        
        if not calib_path.exists():
            raise FileNotFoundError(f"Calibration file not found: {calib_path}")
        
        calib_data = pd.read_parquet(calib_path)
        
        if clip_id is not None:
            calib_data = calib_data[calib_data['clip_id'] == clip_id]
        
        return calib_data
    
    def load_ego_motion(self, clip_id: str) -> pd.DataFrame:
        """
        Load ego motion data for a specific clip.
        
        Args:
            clip_id (str): UUID of the clip
            
        Returns:
            pd.DataFrame: Ego motion data (pose, velocity, acceleration)
        """
        # Ego motion is typically stored in labels directory
        ego_path = self.data_root / 'labels' / 'ego_motion' / f'{clip_id}.parquet'
        
        if not ego_path.exists():
            raise FileNotFoundError(f"Ego motion file not found: {ego_path}")
        
        return pd.read_parquet(ego_path)
    
    def get_statistics(self) -> Dict:
        """
        Get overall dataset statistics.
        
        Returns:
            dict: Dictionary containing dataset statistics
        """
        collection_meta = self.load_data_collection_metadata()
        sensor_meta = self.load_sensor_presence()
        
        stats = {
            'total_clips': len(collection_meta),
            'total_hours': len(collection_meta) * 20 / 3600,  # 20 sec clips
            'countries': collection_meta['country'].nunique(),
            'country_distribution': collection_meta['country'].value_counts().to_dict(),
            'clips_with_radar': sensor_meta[sensor_meta['radar_config'] != 'NA'].shape[0],
            'radar_config_distribution': sensor_meta['radar_config'].value_counts().to_dict(),
            'platform_distribution': collection_meta['platform_class'].value_counts().to_dict()
        }
        
        return stats
    
    def sample_clips(
        self, 
        n: int = 10, 
        random_state: Optional[int] = None,
        **filter_kwargs
    ) -> pd.DataFrame:
        """
        Sample random clips from the dataset with optional filtering.
        
        Args:
            n (int): Number of clips to sample
            random_state (int, optional): Random seed for reproducibility
            **filter_kwargs: Additional filtering criteria (passed to filter_clips)
            
        Returns:
            pd.DataFrame: Sample of clip metadata
        """
        if filter_kwargs:
            clips = self.filter_clips(**filter_kwargs)
        else:
            clips = self.load_data_collection_metadata()
        
        if len(clips) < n:
            print(f"Warning: Only {len(clips)} clips available, returning all")
            return clips
        
        return clips.sample(n=n, random_state=random_state)


if __name__ == "__main__":
    # Example usage
    print("PhysicalAI-Autonomous-Vehicles Dataset Loader")
    print("=" * 50)
    print("\nUsage example:")
    print("loader = DatasetLoader('/path/to/dataset')")
    print("metadata = loader.load_metadata()")
    print("stats = loader.get_statistics()")
