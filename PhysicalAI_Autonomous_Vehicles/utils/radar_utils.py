"""
Radar data utilities for PhysicalAI-Autonomous-Vehicles dataset.

This module provides utilities for loading and processing radar point cloud data
from multiple radar sensors with different configurations (SRR, MRR, LRR).
"""

import io
import zipfile
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
import pandas as pd


class RadarLoader:
    """
    Utility class for loading and processing radar data.
    
    Handles radar point clouds from up to 10 different radar sensors
    with various configurations (short/medium/long range).
    """
    
    # Radar sensor names
    RADAR_SENSORS = [
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
    
    def __init__(self, dataset_root: str):
        """
        Initialize radar loader.
        
        Args:
            dataset_root (str): Root directory of the dataset
        """
        self.dataset_root = Path(dataset_root)
        self.radar_dir = self.dataset_root / 'radar'
    
    def load_radar_data(
        self, 
        clip_id: str,
        radar_sensor: str,
        chunk_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load radar data for a specific clip and sensor.
        
        Args:
            clip_id (str): UUID of the clip
            radar_sensor (str): Name of the radar sensor
            chunk_file (str, optional): Path to chunk file (auto-detected if None)
            
        Returns:
            pd.DataFrame: Radar data with columns:
                - scan_index: Sequential scan number
                - timestamp: System timestamp (microseconds)
                - sensor_timestamp: Sensor timestamp (microseconds)
                - num_returns: Number of detections in scan
                - detection_index: Detection index within scan
                - radar_model: Radar model identifier
                - azimuth: Horizontal angle (radians)
                - elevation: Vertical angle (radians)
                - distance: Distance to target (meters)
                - radial_velocity: Radial velocity (m/s)
                - rcs: Radar cross-section (dBsm)
                - snr: Signal-to-noise ratio (dB)
                - exist_probb: Existence probability
        """
        if radar_sensor not in self.RADAR_SENSORS:
            raise ValueError(f"Invalid radar sensor: {radar_sensor}")
        
        if chunk_file is None:
            chunk_file = self._find_chunk_for_clip(clip_id, radar_sensor)
            if chunk_file is None:
                raise FileNotFoundError(
                    f"Chunk file not found for clip {clip_id} and sensor {radar_sensor}"
                )
        
        # Radar files are named: <clip_id>.radar_<config>.parquet
        parquet_filename = f"{clip_id}.{radar_sensor}.parquet"
        
        with zipfile.ZipFile(chunk_file, 'r') as zf:
            if parquet_filename not in zf.namelist():
                raise FileNotFoundError(f"Radar file not found in chunk: {parquet_filename}")
            
            parquet_bytes = zf.read(parquet_filename)
            
            # Read parquet from bytes
            radar_df = pd.read_parquet(io.BytesIO(parquet_bytes))
        
        return radar_df
    
    def load_all_radars(
        self, 
        clip_id: str,
        available_sensors: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load data from all available radar sensors for a clip.
        
        Args:
            clip_id (str): UUID of the clip
            available_sensors (list, optional): List of available sensors
                (if None, will try to load from all possible sensors)
            
        Returns:
            dict: Dictionary mapping sensor names to radar dataframes
        """
        radar_data = {}
        
        sensors_to_try = available_sensors if available_sensors else self.RADAR_SENSORS
        
        for sensor in sensors_to_try:
            try:
                data = self.load_radar_data(clip_id, sensor)
                radar_data[sensor] = data
            except FileNotFoundError:
                # Sensor not available for this clip
                continue
        
        return radar_data
    
    def _find_chunk_for_clip(self, clip_id: str, radar_sensor: str) -> Optional[str]:
        """
        Find which chunk file contains the clip for specified radar sensor.
        
        Args:
            clip_id (str): UUID of the clip
            radar_sensor (str): Name of the radar sensor
            
        Returns:
            str: Path to chunk file or None if not found
        """
        sensor_dir = self.radar_dir / radar_sensor
        
        if not sensor_dir.exists():
            return None
        
        chunk_files = sorted(sensor_dir.glob(f'{radar_sensor}.chunk_*.zip'))
        
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
    
    def convert_to_cartesian(self, radar_df: pd.DataFrame) -> np.ndarray:
        """
        Convert radar data from spherical to Cartesian coordinates.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe with azimuth, elevation, distance
            
        Returns:
            np.ndarray: Points in Cartesian coordinates (N, 3) - [x, y, z]
        """
        azimuth = radar_df['azimuth'].values
        elevation = radar_df['elevation'].values
        distance = radar_df['distance'].values
        
        # Convert spherical to Cartesian
        x = distance * np.cos(elevation) * np.cos(azimuth)
        y = distance * np.cos(elevation) * np.sin(azimuth)
        z = distance * np.sin(elevation)
        
        return np.column_stack([x, y, z])
    
    def filter_by_distance(
        self, 
        radar_df: pd.DataFrame,
        min_distance: float = 0.0,
        max_distance: float = np.inf
    ) -> pd.DataFrame:
        """
        Filter radar detections by distance.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe
            min_distance (float): Minimum distance (meters)
            max_distance (float): Maximum distance (meters)
            
        Returns:
            pd.DataFrame: Filtered radar data
        """
        mask = (radar_df['distance'] >= min_distance) & (radar_df['distance'] <= max_distance)
        return radar_df[mask]
    
    def filter_by_velocity(
        self, 
        radar_df: pd.DataFrame,
        min_velocity: float = -np.inf,
        max_velocity: float = np.inf
    ) -> pd.DataFrame:
        """
        Filter radar detections by radial velocity.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe
            min_velocity (float): Minimum velocity (m/s)
            max_velocity (float): Maximum velocity (m/s)
            
        Returns:
            pd.DataFrame: Filtered radar data
        """
        mask = (
            (radar_df['radial_velocity'] >= min_velocity) & 
            (radar_df['radial_velocity'] <= max_velocity)
        )
        return radar_df[mask]
    
    def filter_by_snr(
        self, 
        radar_df: pd.DataFrame,
        min_snr: float = 0.0
    ) -> pd.DataFrame:
        """
        Filter radar detections by signal-to-noise ratio.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe
            min_snr (float): Minimum SNR (dB)
            
        Returns:
            pd.DataFrame: Filtered radar data
        """
        return radar_df[radar_df['snr'] >= min_snr]
    
    def get_scan_at_time(
        self, 
        radar_df: pd.DataFrame,
        timestamp: int
    ) -> pd.DataFrame:
        """
        Get radar scan closest to a specific timestamp.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe
            timestamp (int): Target timestamp (microseconds)
            
        Returns:
            pd.DataFrame: Radar scan data
        """
        # Find scan with closest timestamp
        unique_scans = radar_df['scan_index'].unique()
        
        closest_scan = None
        min_diff = float('inf')
        
        for scan_idx in unique_scans:
            scan_data = radar_df[radar_df['scan_index'] == scan_idx]
            scan_time = scan_data['timestamp'].iloc[0]
            diff = abs(scan_time - timestamp)
            
            if diff < min_diff:
                min_diff = diff
                closest_scan = scan_idx
        
        return radar_df[radar_df['scan_index'] == closest_scan]
    
    def get_statistics(self, radar_df: pd.DataFrame) -> dict:
        """
        Get statistics about radar data.
        
        Args:
            radar_df (pd.DataFrame): Radar dataframe
            
        Returns:
            dict: Statistics including detection counts, ranges, velocities, etc.
        """
        stats = {
            'total_detections': len(radar_df),
            'num_scans': radar_df['scan_index'].nunique(),
            'avg_detections_per_scan': len(radar_df) / radar_df['scan_index'].nunique(),
            'distance_range': (radar_df['distance'].min(), radar_df['distance'].max()),
            'velocity_range': (
                radar_df['radial_velocity'].min(), 
                radar_df['radial_velocity'].max()
            ),
            'avg_snr': radar_df['snr'].mean(),
            'radar_models': radar_df['radar_model'].unique().tolist(),
            'duration_us': radar_df['timestamp'].max() - radar_df['timestamp'].min()
        }
        
        return stats
    
    def merge_radar_scans(
        self, 
        radar_data_dict: Dict[str, pd.DataFrame],
        timestamp: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Merge radar data from multiple sensors at a specific time.
        
        Args:
            radar_data_dict (dict): Dictionary of radar sensor data
            timestamp (int, optional): Target timestamp (uses first scan if None)
            
        Returns:
            pd.DataFrame: Merged radar data from all sensors
        """
        merged_scans = []
        
        for sensor_name, radar_df in radar_data_dict.items():
            if timestamp is not None:
                scan = self.get_scan_at_time(radar_df, timestamp)
            else:
                # Get first scan
                first_scan_idx = radar_df['scan_index'].min()
                scan = radar_df[radar_df['scan_index'] == first_scan_idx]
            
            # Add sensor name column
            scan = scan.copy()
            scan['sensor_name'] = sensor_name
            merged_scans.append(scan)
        
        return pd.concat(merged_scans, ignore_index=True)


if __name__ == "__main__":
    print("Radar utilities for PhysicalAI-Autonomous-Vehicles dataset")
    print("Usage: from utils.radar_utils import RadarLoader")
    print(f"Supported radar sensors: {len(RadarLoader.RADAR_SENSORS)}")
