"""
Data Loader Utilities for PleIAs SYNTH Dataset

This module provides utilities for loading and accessing the SYNTH dataset
from HuggingFace or local cache.
"""

import os
from typing import Optional, Dict, Any, Union
from datasets import load_dataset, Dataset, DatasetDict
import pandas as pd


class SYNTHLoader:
    """
    Loader class for the PleIAs SYNTH dataset.
    
    This class provides convenient methods to load and access the SYNTH dataset
    from HuggingFace Hub with optional caching.
    
    Attributes:
        dataset_name (str): The HuggingFace dataset identifier
        cache_dir (str): Directory for caching downloaded data
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the SYNTH dataset loader.
        
        Args:
            cache_dir (str, optional): Directory to cache downloaded data.
                                      Defaults to './data/cache'
        """
        self.dataset_name = "PleIAs/SYNTH"
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "data", "cache")
        self._dataset = None
        
    def load_dataset(
        self, 
        split: Optional[str] = None,
        streaming: bool = False,
        trust_remote_code: bool = False
    ) -> Union[Dataset, DatasetDict]:
        """
        Load the SYNTH dataset from HuggingFace.
        
        Args:
            split (str, optional): Specific split to load ('train', 'test', etc.)
            streaming (bool): Whether to stream the dataset (useful for large datasets)
            trust_remote_code (bool): Whether to trust remote code in dataset.
                                     Set to True only if you trust the dataset source.
            
        Returns:
            Dataset or DatasetDict: The loaded dataset
            
        Example:
            >>> loader = SYNTHLoader()
            >>> dataset = loader.load_dataset()
            >>> train_data = loader.load_dataset(split='train')
        """
        try:
            self._dataset = load_dataset(
                self.dataset_name,
                split=split,
                streaming=streaming,
                cache_dir=self.cache_dir,
                trust_remote_code=trust_remote_code
            )
            print(f"✓ Successfully loaded {self.dataset_name}")
            return self._dataset
        except Exception as e:
            print(f"✗ Error loading dataset: {e}")
            print(f"  Make sure you have internet connection and the dataset exists at:")
            print(f"  https://huggingface.co/datasets/{self.dataset_name}")
            raise
    
    def load_as_pandas(
        self, 
        split: Optional[str] = None,
        max_rows: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load the dataset as a pandas DataFrame.
        
        Args:
            split (str, optional): Specific split to load
            max_rows (int, optional): Maximum number of rows to load
            
        Returns:
            pd.DataFrame: Dataset as a pandas DataFrame
            
        Example:
            >>> loader = SYNTHLoader()
            >>> df = loader.load_as_pandas(split='train', max_rows=1000)
        """
        if self._dataset is None:
            self.load_dataset(split=split)
        
        if isinstance(self._dataset, DatasetDict):
            # If multiple splits, use first one or specified split
            if split and split in self._dataset:
                dataset_to_use = self._dataset[split]
            else:
                dataset_to_use = self._dataset[list(self._dataset.keys())[0]]
        else:
            dataset_to_use = self._dataset
        
        # Convert to pandas
        if max_rows:
            df = dataset_to_use.select(range(min(max_rows, len(dataset_to_use)))).to_pandas()
        else:
            df = dataset_to_use.to_pandas()
        
        return df
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about the dataset.
        
        Returns:
            dict: Dictionary containing dataset information
            
        Example:
            >>> loader = SYNTHLoader()
            >>> info = loader.get_dataset_info()
            >>> print(info['features'])
        """
        if self._dataset is None:
            self.load_dataset()
        
        info = {}
        
        if isinstance(self._dataset, DatasetDict):
            info['name'] = self.dataset_name
            info['splits'] = list(self._dataset.keys())
            info['num_rows'] = {split: len(self._dataset[split]) for split in self._dataset.keys()}
            # Get features from first split
            first_split = list(self._dataset.keys())[0]
            info['features'] = self._dataset[first_split].features
            info['column_names'] = self._dataset[first_split].column_names
        else:
            info['name'] = self.dataset_name
            info['splits'] = ['default']
            info['num_rows'] = len(self._dataset)
            info['features'] = self._dataset.features
            info['column_names'] = self._dataset.column_names
        
        return info
    
    def prepare_for_training(
        self,
        feature_columns: Optional[list] = None,
        target_column: str = 'label',
        split: Optional[str] = 'train'
    ) -> tuple:
        """
        Prepare dataset for machine learning training.
        
        Args:
            feature_columns (list, optional): List of feature column names
            target_column (str): Name of the target column
            split (str, optional): Which split to use
            
        Returns:
            tuple: (X, y) where X is features and y is target
            
        Example:
            >>> loader = SYNTHLoader()
            >>> X, y = loader.prepare_for_training(target_column='label')
        """
        df = self.load_as_pandas(split=split)
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        y = df[target_column]
        
        if feature_columns:
            X = df[feature_columns]
        else:
            # Use all columns except target
            X = df.drop(columns=[target_column])
        
        return X, y
    
    @property
    def dataset(self) -> Union[Dataset, DatasetDict, None]:
        """Get the currently loaded dataset."""
        return self._dataset


# Convenience function for quick loading
def quick_load(split: Optional[str] = None, max_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Quick load the SYNTH dataset as a pandas DataFrame.
    
    Args:
        split (str, optional): Specific split to load
        max_rows (int, optional): Maximum number of rows to load
        
    Returns:
        pd.DataFrame: Dataset as a pandas DataFrame
        
    Example:
        >>> df = quick_load(split='train', max_rows=1000)
    """
    loader = SYNTHLoader()
    return loader.load_as_pandas(split=split, max_rows=max_rows)
