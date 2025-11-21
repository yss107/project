"""
Calibration utilities for PhysicalAI-Autonomous-Vehicles dataset.

This module provides utilities for loading and using calibration data including
camera intrinsics, sensor extrinsics, and vehicle dimensions.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


class CalibrationLoader:
    """
    Utility class for loading and processing calibration data.
    
    Handles camera intrinsics, sensor extrinsics, and vehicle dimensions.
    """
    
    def __init__(self, dataset_root: str):
        """
        Initialize calibration loader.
        
        Args:
            dataset_root (str): Root directory of the dataset
        """
        self.dataset_root = Path(dataset_root)
        self.calibration_dir = self.dataset_root / 'calibration'
    
    def load_camera_intrinsics(self, clip_id: Optional[str] = None) -> pd.DataFrame:
        """
        Load camera intrinsic parameters.
        
        Args:
            clip_id (str, optional): Specific clip ID (loads all if None)
            
        Returns:
            pd.DataFrame: Camera intrinsics with f-theta model parameters
        """
        calib_path = self.calibration_dir / 'camera_intrinsics.parquet'
        
        if not calib_path.exists():
            raise FileNotFoundError(f"Camera intrinsics not found: {calib_path}")
        
        intrinsics = pd.read_parquet(calib_path)
        
        if clip_id is not None:
            intrinsics = intrinsics[intrinsics['clip_id'] == clip_id]
        
        return intrinsics
    
    def load_sensor_extrinsics(self, clip_id: str) -> pd.DataFrame:
        """
        Load sensor extrinsic parameters (poses).
        
        Args:
            clip_id (str): Clip ID
            
        Returns:
            pd.DataFrame: Sensor extrinsics (rotation quaternion and translation)
        """
        extrinsics_path = self.calibration_dir / 'sensor_extrinsics.parquet'
        
        if not extrinsics_path.exists():
            raise FileNotFoundError(f"Sensor extrinsics not found: {extrinsics_path}")
        
        extrinsics = pd.read_parquet(extrinsics_path)
        extrinsics = extrinsics[extrinsics['clip_id'] == clip_id]
        
        return extrinsics
    
    def load_vehicle_dimensions(self, clip_id: str) -> pd.Series:
        """
        Load vehicle dimension parameters.
        
        Args:
            clip_id (str): Clip ID
            
        Returns:
            pd.Series: Vehicle dimensions
        """
        dimensions_path = self.calibration_dir / 'vehicle_dimensions.parquet'
        
        if not dimensions_path.exists():
            raise FileNotFoundError(f"Vehicle dimensions not found: {dimensions_path}")
        
        dimensions = pd.read_parquet(dimensions_path)
        dimensions = dimensions[dimensions['clip_id'] == clip_id]
        
        if dimensions.empty:
            raise ValueError(f"No vehicle dimensions found for clip {clip_id}")
        
        return dimensions.iloc[0]
    
    def get_camera_matrix(self, camera_intrinsics: pd.Series) -> np.ndarray:
        """
        Get camera intrinsic matrix from f-theta parameters.
        
        Note: This is a simplified representation. Full f-theta model
        requires polynomial evaluation.
        
        Args:
            camera_intrinsics (pd.Series): Camera intrinsic parameters
            
        Returns:
            np.ndarray: 3x3 camera matrix (simplified)
        """
        cx = camera_intrinsics['cx']
        cy = camera_intrinsics['cy']
        # Use fw_poly_1 as approximate focal length
        f = camera_intrinsics['fw_poly_1']
        
        K = np.array([
            [f, 0, cx],
            [0, f, cy],
            [0, 0, 1]
        ])
        
        return K
    
    def quaternion_to_rotation_matrix(
        self, 
        qx: float, 
        qy: float, 
        qz: float, 
        qw: float
    ) -> np.ndarray:
        """
        Convert quaternion to rotation matrix.
        
        Args:
            qx, qy, qz, qw (float): Quaternion components
            
        Returns:
            np.ndarray: 3x3 rotation matrix
        """
        # Normalize quaternion
        norm = np.sqrt(qx**2 + qy**2 + qz**2 + qw**2)
        qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm
        
        # Convert to rotation matrix
        R = np.array([
            [1 - 2*(qy**2 + qz**2), 2*(qx*qy - qw*qz), 2*(qx*qz + qw*qy)],
            [2*(qx*qy + qw*qz), 1 - 2*(qx**2 + qz**2), 2*(qy*qz - qw*qx)],
            [2*(qx*qz - qw*qy), 2*(qy*qz + qw*qx), 1 - 2*(qx**2 + qy**2)]
        ])
        
        return R
    
    def get_transformation_matrix(self, extrinsics: pd.Series) -> np.ndarray:
        """
        Get 4x4 transformation matrix from extrinsic parameters.
        
        Args:
            extrinsics (pd.Series): Sensor extrinsic parameters
            
        Returns:
            np.ndarray: 4x4 transformation matrix
        """
        R = self.quaternion_to_rotation_matrix(
            extrinsics['qx'],
            extrinsics['qy'],
            extrinsics['qz'],
            extrinsics['qw']
        )
        
        t = np.array([extrinsics['x'], extrinsics['y'], extrinsics['z']])
        
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        
        return T
    
    def transform_points(
        self, 
        points: np.ndarray,
        transformation: np.ndarray
    ) -> np.ndarray:
        """
        Transform 3D points using a transformation matrix.
        
        Args:
            points (np.ndarray): Points (N, 3)
            transformation (np.ndarray): 4x4 transformation matrix
            
        Returns:
            np.ndarray: Transformed points (N, 3)
        """
        # Convert to homogeneous coordinates
        points_homo = np.hstack([points, np.ones((len(points), 1))])
        
        # Apply transformation
        transformed = (transformation @ points_homo.T).T
        
        # Convert back to 3D
        return transformed[:, :3]
    
    def project_points_to_camera(
        self,
        points_3d: np.ndarray,
        camera_intrinsics: pd.Series,
        camera_extrinsics: pd.Series
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Project 3D points to camera image plane.
        
        Note: This uses simplified pinhole projection. For accurate projection,
        use the full f-theta model.
        
        Args:
            points_3d (np.ndarray): 3D points in world coordinates (N, 3)
            camera_intrinsics (pd.Series): Camera intrinsic parameters
            camera_extrinsics (pd.Series): Camera extrinsic parameters
            
        Returns:
            tuple: (points_2d, valid_mask)
                - points_2d: 2D image coordinates (N, 2)
                - valid_mask: Boolean mask for points in front of camera
        """
        # Transform points to camera coordinate system
        T_cam = self.get_transformation_matrix(camera_extrinsics)
        T_cam_inv = np.linalg.inv(T_cam)
        points_cam = self.transform_points(points_3d, T_cam_inv)
        
        # Filter points behind camera
        valid_mask = points_cam[:, 2] > 0
        
        # Get camera matrix
        K = self.get_camera_matrix(camera_intrinsics)
        
        # Project to image plane (simplified)
        points_2d_homo = (K @ points_cam.T).T
        points_2d = points_2d_homo[:, :2] / points_2d_homo[:, 2:3]
        
        return points_2d, valid_mask
    
    def get_rig_coordinate_info(self) -> dict:
        """
        Get information about the rig coordinate system.
        
        Returns:
            dict: Description of rig coordinate frame
        """
        return {
            'origin': 'Center of the rear axle, projected onto the ground plane',
            'x_axis': 'Points forward',
            'y_axis': 'Points left (when looking forward)',
            'z_axis': 'Points up',
            'units': 'meters'
        }


if __name__ == "__main__":
    print("Calibration utilities for PhysicalAI-Autonomous-Vehicles dataset")
    print("Usage: from utils.calibration_utils import CalibrationLoader")
