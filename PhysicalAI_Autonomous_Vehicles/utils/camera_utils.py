"""
Camera data utilities for PhysicalAI-Autonomous-Vehicles dataset.

This module provides utilities for loading and processing camera data,
including video loading, frame extraction, and timestamp handling.
"""

import os
import zipfile
from pathlib import Path
from typing import Optional, Tuple, List
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm


class CameraLoader:
    """
    Utility class for loading and processing camera data.
    
    Supports loading MP4 videos from chunk files and extracting frames
    with corresponding timestamps.
    """
    
    def __init__(self, dataset_root: str):
        """
        Initialize camera loader.
        
        Args:
            dataset_root (str): Root directory of the dataset
        """
        self.dataset_root = Path(dataset_root)
        self.camera_dir = self.dataset_root / 'camera'
        
    def load_video_from_chunk(
        self, 
        clip_id: str, 
        camera_name: str,
        chunk_file: Optional[str] = None
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Load video data and timestamps for a specific clip and camera.
        
        Args:
            clip_id (str): UUID of the clip
            camera_name (str): Name of the camera sensor
            chunk_file (str, optional): Path to chunk file (auto-detected if None)
            
        Returns:
            tuple: (frames array, timestamps dataframe)
                - frames: numpy array of shape (n_frames, height, width, 3)
                - timestamps: pandas DataFrame with frame timestamps
        """
        if chunk_file is None:
            chunk_file = self._find_chunk_for_clip(clip_id, camera_name)
            if chunk_file is None:
                raise FileNotFoundError(f"Chunk file not found for clip {clip_id}")
        
        video_filename = f"{clip_id}.{camera_name}.mp4"
        timestamp_filename = f"{clip_id}.{camera_name}_timestamps.parquet"
        
        frames = []
        timestamps = None
        
        with zipfile.ZipFile(chunk_file, 'r') as zf:
            # Load video
            if video_filename in zf.namelist():
                video_bytes = zf.read(video_filename)
                frames = self._decode_video_bytes(video_bytes)
            else:
                raise FileNotFoundError(f"Video file not found in chunk: {video_filename}")
            
            # Load timestamps
            if timestamp_filename in zf.namelist():
                timestamp_bytes = zf.read(timestamp_filename)
                timestamps = pd.read_parquet(timestamp_bytes)
        
        return frames, timestamps
    
    def _decode_video_bytes(self, video_bytes: bytes) -> np.ndarray:
        """
        Decode video bytes to numpy array of frames.
        
        Args:
            video_bytes (bytes): Video file bytes
            
        Returns:
            np.ndarray: Array of frames (n_frames, height, width, 3)
        """
        # Write to temporary file for OpenCV to read
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        try:
            cap = cv2.VideoCapture(tmp_path)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            
            cap.release()
            
            return np.array(frames)
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
    
    def _find_chunk_for_clip(self, clip_id: str, camera_name: str) -> Optional[str]:
        """
        Find which chunk file contains the clip for specified camera.
        
        Args:
            clip_id (str): UUID of the clip
            camera_name (str): Name of the camera sensor
            
        Returns:
            str: Path to chunk file or None if not found
        """
        camera_sensor_dir = self.camera_dir / camera_name
        
        if not camera_sensor_dir.exists():
            return None
        
        chunk_files = sorted(camera_sensor_dir.glob('*.zip'))
        
        for chunk_file in chunk_files:
            try:
                with zipfile.ZipFile(chunk_file, 'r') as zf:
                    file_list = zf.namelist()
                    for file_name in file_list:
                        if clip_id in file_name and file_name.endswith('.mp4'):
                            return str(chunk_file)
            except Exception:
                continue
        
        return None
    
    def extract_frame(
        self, 
        clip_id: str, 
        camera_name: str,
        frame_idx: int,
        chunk_file: Optional[str] = None
    ) -> np.ndarray:
        """
        Extract a single frame from a video clip.
        
        Args:
            clip_id (str): UUID of the clip
            camera_name (str): Name of the camera sensor
            frame_idx (int): Frame index to extract
            chunk_file (str, optional): Path to chunk file
            
        Returns:
            np.ndarray: Single frame (height, width, 3)
        """
        frames, _ = self.load_video_from_chunk(clip_id, camera_name, chunk_file)
        
        if frame_idx >= len(frames):
            raise IndexError(f"Frame index {frame_idx} out of range (max: {len(frames)-1})")
        
        return frames[frame_idx]
    
    def get_video_info(
        self, 
        clip_id: str, 
        camera_name: str,
        chunk_file: Optional[str] = None
    ) -> dict:
        """
        Get information about a video clip without loading all frames.
        
        Args:
            clip_id (str): UUID of the clip
            camera_name (str): Name of the camera sensor
            chunk_file (str, optional): Path to chunk file
            
        Returns:
            dict: Video information (fps, frame_count, resolution, duration)
        """
        if chunk_file is None:
            chunk_file = self._find_chunk_for_clip(clip_id, camera_name)
            if chunk_file is None:
                raise FileNotFoundError(f"Chunk file not found for clip {clip_id}")
        
        video_filename = f"{clip_id}.{camera_name}.mp4"
        
        with zipfile.ZipFile(chunk_file, 'r') as zf:
            if video_filename not in zf.namelist():
                raise FileNotFoundError(f"Video file not found: {video_filename}")
            
            video_bytes = zf.read(video_filename)
        
        # Write to temporary file to get info
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        try:
            cap = cv2.VideoCapture(tmp_path)
            
            info = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration_sec': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
            }
            
            cap.release()
            
            return info
        finally:
            os.unlink(tmp_path)
    
    def create_video_mosaic(
        self,
        clip_id: str,
        camera_names: List[str],
        frame_idx: int = 0,
        layout: str = '2x4'
    ) -> np.ndarray:
        """
        Create a mosaic view from multiple cameras.
        
        Args:
            clip_id (str): UUID of the clip
            camera_names (list): List of camera names to include
            frame_idx (int): Frame index to extract
            layout (str): Layout pattern (e.g., '2x4' for 2 rows, 4 columns)
            
        Returns:
            np.ndarray: Mosaic image
        """
        frames = []
        
        for camera_name in camera_names:
            try:
                frame = self.extract_frame(clip_id, camera_name, frame_idx)
                frames.append(frame)
            except Exception as e:
                print(f"Warning: Could not load {camera_name}: {e}")
                # Create blank frame
                frames.append(np.zeros((1080, 1920, 3), dtype=np.uint8))
        
        # Parse layout
        rows, cols = map(int, layout.split('x'))
        
        # Resize all frames to same size
        target_size = (640, 360)  # Smaller size for mosaic
        resized_frames = [cv2.resize(f, target_size) for f in frames]
        
        # Create mosaic
        mosaic_rows = []
        for i in range(rows):
            row_frames = resized_frames[i*cols:(i+1)*cols]
            if len(row_frames) < cols:
                # Pad with blank frames
                while len(row_frames) < cols:
                    row_frames.append(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8))
            mosaic_rows.append(np.hstack(row_frames))
        
        mosaic = np.vstack(mosaic_rows)
        
        return mosaic


def undistort_image(
    image: np.ndarray,
    camera_intrinsics: pd.Series
) -> np.ndarray:
    """
    Undistort image using f-theta camera model.
    
    Args:
        image (np.ndarray): Distorted image
        camera_intrinsics (pd.Series): Camera intrinsic parameters
        
    Returns:
        np.ndarray: Undistorted image
    """
    # Extract parameters
    height, width = image.shape[:2]
    cx = camera_intrinsics['cx']
    cy = camera_intrinsics['cy']
    
    # Backward polynomial coefficients for undistortion
    bw_poly = [
        camera_intrinsics['bw_poly_0'],
        camera_intrinsics['bw_poly_1'],
        camera_intrinsics['bw_poly_2'],
        camera_intrinsics['bw_poly_3'],
        camera_intrinsics['bw_poly_4']
    ]
    
    # Create undistortion map (simplified version)
    # Full implementation would use the f-theta model
    # This is a placeholder for the actual undistortion logic
    
    # For now, return the original image
    # TODO: Implement full f-theta undistortion
    print("Warning: Full f-theta undistortion not yet implemented")
    return image


if __name__ == "__main__":
    print("Camera utilities for PhysicalAI-Autonomous-Vehicles dataset")
    print("Usage: from utils.camera_utils import CameraLoader")
