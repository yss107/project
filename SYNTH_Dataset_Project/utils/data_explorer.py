"""
Data Explorer Utilities for PleIAs SYNTH Dataset

This module provides utilities for exploring and analyzing the SYNTH dataset.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datasets import Dataset, DatasetDict


class DataExplorer:
    """
    Explorer class for analyzing the SYNTH dataset.
    
    Provides methods to explore dataset characteristics, statistics,
    and data quality.
    
    Attributes:
        data: The dataset to explore (pandas DataFrame or HuggingFace Dataset)
    """
    
    def __init__(self, data):
        """
        Initialize the Data Explorer.
        
        Args:
            data: Dataset to explore (pd.DataFrame, Dataset, or DatasetDict)
        """
        self.data = data
        self._df = None
        self._prepare_dataframe()
    
    def _prepare_dataframe(self):
        """Convert dataset to pandas DataFrame if needed."""
        if isinstance(self.data, pd.DataFrame):
            self._df = self.data
        elif isinstance(self.data, Dataset):
            self._df = self.data.to_pandas()
        elif isinstance(self.data, DatasetDict):
            # Use first split
            first_split = list(self.data.keys())[0]
            self._df = self.data[first_split].to_pandas()
        else:
            raise TypeError(f"Unsupported data type: {type(self.data)}")
    
    def print_summary(self):
        """
        Print a comprehensive summary of the dataset.
        
        Example:
            >>> explorer = DataExplorer(dataset)
            >>> explorer.print_summary()
        """
        print("=" * 80)
        print("SYNTH DATASET SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Dataset Shape: {self._df.shape[0]:,} rows × {self._df.shape[1]} columns")
        print(f"\n📋 Columns: {', '.join(self._df.columns.tolist())}")
        
        print("\n" + "-" * 80)
        print("COLUMN INFORMATION")
        print("-" * 80)
        print(self._df.info())
        
        print("\n" + "-" * 80)
        print("FIRST FEW ROWS")
        print("-" * 80)
        print(self._df.head())
        
        print("\n" + "=" * 80)
    
    def show_statistics(self, columns: Optional[List[str]] = None):
        """
        Show statistical summary of the dataset.
        
        Args:
            columns (list, optional): Specific columns to analyze
            
        Example:
            >>> explorer.show_statistics()
            >>> explorer.show_statistics(columns=['feature1', 'feature2'])
        """
        print("=" * 80)
        print("STATISTICAL SUMMARY")
        print("=" * 80)
        
        if columns:
            df_subset = self._df[columns]
        else:
            df_subset = self._df
        
        # Numeric columns
        numeric_cols = df_subset.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            print("\n📈 Numeric Columns:")
            print(df_subset[numeric_cols].describe())
        
        # Categorical columns
        categorical_cols = df_subset.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            print("\n📝 Categorical Columns:")
            for col in categorical_cols:
                print(f"\n  {col}:")
                print(f"    Unique values: {df_subset[col].nunique()}")
                print(f"    Top 5 values:")
                print(df_subset[col].value_counts().head().to_string().replace('\n', '\n    '))
        
        print("\n" + "=" * 80)
    
    def check_missing_values(self) -> pd.DataFrame:
        """
        Check for missing values in the dataset.
        
        Returns:
            pd.DataFrame: DataFrame with missing value statistics
            
        Example:
            >>> explorer.check_missing_values()
        """
        missing = pd.DataFrame({
            'Column': self._df.columns,
            'Missing_Count': self._df.isnull().sum().values,
            'Missing_Percentage': (self._df.isnull().sum().values / len(self._df) * 100).round(2)
        })
        missing = missing[missing['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
        
        print("=" * 80)
        print("MISSING VALUES ANALYSIS")
        print("=" * 80)
        
        if len(missing) == 0:
            print("\n✓ No missing values found!")
        else:
            print(f"\n⚠ Found missing values in {len(missing)} columns:\n")
            print(missing.to_string(index=False))
        
        print("\n" + "=" * 80)
        return missing
    
    def analyze_column(self, column_name: str) -> Dict[str, Any]:
        """
        Perform detailed analysis of a specific column.
        
        Args:
            column_name (str): Name of the column to analyze
            
        Returns:
            dict: Dictionary containing column analysis
            
        Example:
            >>> analysis = explorer.analyze_column('feature1')
        """
        if column_name not in self._df.columns:
            raise ValueError(f"Column '{column_name}' not found in dataset")
        
        col = self._df[column_name]
        analysis = {
            'name': column_name,
            'dtype': str(col.dtype),
            'count': len(col),
            'missing': col.isnull().sum(),
            'missing_pct': (col.isnull().sum() / len(col) * 100).round(2),
            'unique': col.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(col):
            analysis.update({
                'mean': col.mean(),
                'std': col.std(),
                'min': col.min(),
                'max': col.max(),
                'median': col.median(),
                'q25': col.quantile(0.25),
                'q75': col.quantile(0.75)
            })
        elif pd.api.types.is_string_dtype(col) or pd.api.types.is_categorical_dtype(col):
            value_counts = col.value_counts()
            analysis.update({
                'most_common': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_common_count': value_counts.values[0] if len(value_counts) > 0 else 0,
                'top_5_values': value_counts.head().to_dict()
            })
        
        print("=" * 80)
        print(f"COLUMN ANALYSIS: {column_name}")
        print("=" * 80)
        for key, value in analysis.items():
            if key not in ['top_5_values']:
                print(f"{key:20}: {value}")
        if 'top_5_values' in analysis:
            print("\nTop 5 values:")
            for val, count in analysis['top_5_values'].items():
                print(f"  {val:30}: {count}")
        print("=" * 80)
        
        return analysis
    
    def get_correlations(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric columns.
        
        Args:
            method (str): Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            pd.DataFrame: Correlation matrix
            
        Example:
            >>> corr = explorer.get_correlations()
        """
        numeric_df = self._df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            print("⚠ No numeric columns found for correlation analysis")
            return pd.DataFrame()
        
        corr = numeric_df.corr(method=method)
        
        print("=" * 80)
        print(f"CORRELATION MATRIX ({method.upper()})")
        print("=" * 80)
        print(corr)
        print("=" * 80)
        
        return corr
    
    def find_duplicates(self) -> pd.DataFrame:
        """
        Find duplicate rows in the dataset.
        
        Returns:
            pd.DataFrame: Duplicate rows
            
        Example:
            >>> duplicates = explorer.find_duplicates()
        """
        duplicates = self._df[self._df.duplicated(keep=False)]
        
        print("=" * 80)
        print("DUPLICATE ANALYSIS")
        print("=" * 80)
        print(f"\nTotal rows: {len(self._df)}")
        print(f"Duplicate rows: {len(duplicates)}")
        print(f"Percentage: {(len(duplicates) / len(self._df) * 100):.2f}%")
        
        if len(duplicates) > 0:
            print(f"\nShowing first 10 duplicate rows:")
            print(duplicates.head(10))
        
        print("=" * 80)
        
        return duplicates
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Get the underlying pandas DataFrame."""
        return self._df
