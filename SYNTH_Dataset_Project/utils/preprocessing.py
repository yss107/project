"""
Data Preprocessing Utilities for PleIAs SYNTH Dataset

This module provides preprocessing utilities for the SYNTH dataset.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from datasets import Dataset


class DataPreprocessor:
    """
    Preprocessor class for cleaning and transforming the SYNTH dataset.
    
    Provides methods for handling missing values, encoding categorical variables,
    scaling features, and other preprocessing tasks.
    """
    
    def __init__(self):
        """Initialize the Data Preprocessor."""
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = 'mean',
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df (pd.DataFrame): Input dataframe
            strategy (str): Imputation strategy ('mean', 'median', 'most_frequent', 'constant')
            columns (list, optional): Specific columns to impute
            
        Returns:
            pd.DataFrame: Dataframe with imputed values
            
        Example:
            >>> preprocessor = DataPreprocessor()
            >>> df_clean = preprocessor.handle_missing_values(df, strategy='median')
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.columns[df_copy.isnull().any()].tolist()
        
        if not columns:
            print("✓ No missing values to handle")
            return df_copy
        
        # Separate numeric and categorical columns
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df_copy[col])]
        categorical_cols = [col for col in columns if col not in numeric_cols]
        
        # Handle numeric columns
        if numeric_cols:
            imputer = SimpleImputer(strategy=strategy if strategy != 'most_frequent' else 'mean')
            df_copy[numeric_cols] = imputer.fit_transform(df_copy[numeric_cols])
            self.imputers['numeric'] = imputer
        
        # Handle categorical columns
        if categorical_cols:
            imputer = SimpleImputer(strategy='most_frequent')
            df_copy[categorical_cols] = imputer.fit_transform(df_copy[categorical_cols])
            self.imputers['categorical'] = imputer
        
        print(f"✓ Handled missing values in {len(columns)} columns")
        return df_copy
    
    def encode_categorical(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'label',
        drop_first: bool = False
    ) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list, optional): Columns to encode. If None, all object/category columns
            method (str): Encoding method ('label', 'onehot')
            drop_first (bool): For onehot encoding, whether to drop first category
            
        Returns:
            pd.DataFrame: Dataframe with encoded variables
            
        Example:
            >>> df_encoded = preprocessor.encode_categorical(df, method='onehot')
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not columns:
            print("✓ No categorical columns to encode")
            return df_copy
        
        if method == 'label':
            for col in columns:
                encoder = LabelEncoder()
                df_copy[col] = encoder.fit_transform(df_copy[col].astype(str))
                self.encoders[col] = encoder
        
        elif method == 'onehot':
            df_copy = pd.get_dummies(df_copy, columns=columns, drop_first=drop_first)
        
        else:
            raise ValueError(f"Unknown encoding method: {method}")
        
        print(f"✓ Encoded {len(columns)} categorical columns using {method} encoding")
        return df_copy
    
    def scale_features(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'standard'
    ) -> pd.DataFrame:
        """
        Scale numeric features.
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list, optional): Columns to scale. If None, all numeric columns
            method (str): Scaling method ('standard', 'minmax')
            
        Returns:
            pd.DataFrame: Dataframe with scaled features
            
        Example:
            >>> df_scaled = preprocessor.scale_features(df, method='minmax')
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        
        if not columns:
            print("✓ No numeric columns to scale")
            return df_copy
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        df_copy[columns] = scaler.fit_transform(df_copy[columns])
        self.scalers[method] = scaler
        
        print(f"✓ Scaled {len(columns)} columns using {method} scaling")
        return df_copy
    
    def remove_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from numeric columns.
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list, optional): Columns to check for outliers
            method (str): Method to detect outliers ('iqr', 'zscore')
            threshold (float): Threshold for outlier detection
            
        Returns:
            pd.DataFrame: Dataframe with outliers removed
            
        Example:
            >>> df_clean = preprocessor.remove_outliers(df, method='iqr')
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        
        if not columns:
            print("✓ No numeric columns to check for outliers")
            return df_copy
        
        original_len = len(df_copy)
        
        if method == 'iqr':
            for col in columns:
                Q1 = df_copy[col].quantile(0.25)
                Q3 = df_copy[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df_copy = df_copy[(df_copy[col] >= lower_bound) & (df_copy[col] <= upper_bound)]
        
        elif method == 'zscore':
            for col in columns:
                z_scores = np.abs((df_copy[col] - df_copy[col].mean()) / df_copy[col].std())
                df_copy = df_copy[z_scores < threshold]
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        removed = original_len - len(df_copy)
        print(f"✓ Removed {removed} outliers ({removed/original_len*100:.2f}%)")
        
        return df_copy
    
    def apply_pipeline(
        self,
        df: pd.DataFrame,
        steps: Optional[List[Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        """
        Apply a preprocessing pipeline with multiple steps.
        
        Args:
            df (pd.DataFrame): Input dataframe
            steps (list): List of preprocessing steps as dictionaries
            
        Returns:
            pd.DataFrame: Fully preprocessed dataframe
            
        Example:
            >>> steps = [
            ...     {'method': 'handle_missing_values', 'strategy': 'median'},
            ...     {'method': 'encode_categorical', 'method': 'onehot'},
            ...     {'method': 'scale_features', 'method': 'standard'}
            ... ]
            >>> df_processed = preprocessor.apply_pipeline(df, steps)
        """
        if steps is None:
            # Default pipeline
            steps = [
                {'method': 'handle_missing_values', 'strategy': 'median'},
                {'method': 'encode_categorical', 'method': 'label'},
                {'method': 'scale_features', 'method': 'standard'}
            ]
        
        df_processed = df.copy()
        
        print("=" * 80)
        print("APPLYING PREPROCESSING PIPELINE")
        print("=" * 80)
        
        for i, step in enumerate(steps, 1):
            method_name = step.pop('method')
            print(f"\nStep {i}: {method_name}")
            
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                df_processed = method(df_processed, **step)
            else:
                print(f"⚠ Unknown method: {method_name}")
        
        print("\n" + "=" * 80)
        print(f"✓ Pipeline complete! Final shape: {df_processed.shape}")
        print("=" * 80)
        
        return df_processed
    
    def train_test_split_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> tuple:
        """
        Split data into train and test sets.
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column
            test_size (float): Proportion of test set
            random_state (int): Random seed for reproducibility
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
            
        Example:
            >>> X_train, X_test, y_train, y_test = preprocessor.train_test_split_data(
            ...     df, target_column='label'
            ... )
        """
        from sklearn.model_selection import train_test_split
        
        y = df[target_column]
        X = df.drop(columns=[target_column])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        print(f"✓ Split data: {len(X_train)} train, {len(X_test)} test")
        
        return X_train, X_test, y_train, y_test
