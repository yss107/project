"""
Data Visualizer Utilities for PleIAs SYNTH Dataset

This module provides visualization utilities for the SYNTH dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
from datasets import Dataset, DatasetDict


class DataVisualizer:
    """
    Visualizer class for creating plots and visualizations of the SYNTH dataset.
    
    Attributes:
        data: The dataset to visualize
        style (str): Seaborn style to use
    """
    
    def __init__(self, data, style: str = 'whitegrid'):
        """
        Initialize the Data Visualizer.
        
        Args:
            data: Dataset to visualize (pd.DataFrame, Dataset, or DatasetDict)
            style (str): Seaborn style ('whitegrid', 'darkgrid', 'white', 'dark', 'ticks')
        """
        self.data = data
        self._df = None
        self._prepare_dataframe()
        
        # Set style
        sns.set_style(style)
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def _prepare_dataframe(self):
        """Convert dataset to pandas DataFrame if needed."""
        if isinstance(self.data, pd.DataFrame):
            self._df = self.data
        elif isinstance(self.data, Dataset):
            self._df = self.data.to_pandas()
        elif isinstance(self.data, DatasetDict):
            first_split = list(self.data.keys())[0]
            self._df = self.data[first_split].to_pandas()
        else:
            raise TypeError(f"Unsupported data type: {type(self.data)}")
    
    def plot_distributions(
        self, 
        columns: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (15, 10)
    ):
        """
        Plot distributions of numeric columns.
        
        Args:
            columns (list, optional): Specific columns to plot
            figsize (tuple): Figure size (width, height)
            
        Example:
            >>> visualizer = DataVisualizer(dataset)
            >>> visualizer.plot_distributions()
        """
        if columns:
            numeric_cols = [col for col in columns if col in self._df.select_dtypes(include=[np.number]).columns]
        else:
            numeric_cols = self._df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            print("⚠ No numeric columns to plot")
            return
        
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
        
        for idx, col in enumerate(numeric_cols):
            if idx < len(axes):
                sns.histplot(data=self._df, x=col, kde=True, ax=axes[idx])
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
        
        # Hide extra subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def plot_categorical(
        self,
        columns: Optional[List[str]] = None,
        top_n: int = 10,
        figsize: Tuple[int, int] = (15, 10)
    ):
        """
        Plot bar charts for categorical columns.
        
        Args:
            columns (list, optional): Specific columns to plot
            top_n (int): Number of top categories to show
            figsize (tuple): Figure size (width, height)
            
        Example:
            >>> visualizer.plot_categorical(top_n=5)
        """
        if columns:
            cat_cols = [col for col in columns if col in self._df.select_dtypes(include=['object', 'category']).columns]
        else:
            cat_cols = self._df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not cat_cols:
            print("⚠ No categorical columns to plot")
            return
        
        n_cols = min(2, len(cat_cols))
        n_rows = (len(cat_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
        
        for idx, col in enumerate(cat_cols):
            if idx < len(axes):
                value_counts = self._df[col].value_counts().head(top_n)
                value_counts.plot(kind='bar', ax=axes[idx])
                axes[idx].set_title(f'Top {top_n} values in {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Count')
                axes[idx].tick_params(axis='x', rotation=45)
        
        # Hide extra subplots
        for idx in range(len(cat_cols), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def create_correlation_matrix(
        self,
        method: str = 'pearson',
        figsize: Tuple[int, int] = (12, 10),
        annot: bool = True
    ):
        """
        Create a correlation heatmap for numeric columns.
        
        Args:
            method (str): Correlation method ('pearson', 'spearman', 'kendall')
            figsize (tuple): Figure size (width, height)
            annot (bool): Whether to annotate cells with values
            
        Example:
            >>> visualizer.create_correlation_matrix()
        """
        numeric_df = self._df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            print("⚠ No numeric columns for correlation matrix")
            return
        
        corr = numeric_df.corr(method=method)
        
        plt.figure(figsize=figsize)
        sns.heatmap(
            corr,
            annot=annot,
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8}
        )
        plt.title(f'Correlation Matrix ({method.capitalize()})')
        plt.tight_layout()
        plt.show()
    
    def plot_boxplots(
        self,
        columns: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (15, 10)
    ):
        """
        Create box plots for numeric columns to show distributions and outliers.
        
        Args:
            columns (list, optional): Specific columns to plot
            figsize (tuple): Figure size (width, height)
            
        Example:
            >>> visualizer.plot_boxplots()
        """
        if columns:
            numeric_cols = [col for col in columns if col in self._df.select_dtypes(include=[np.number]).columns]
        else:
            numeric_cols = self._df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            print("⚠ No numeric columns to plot")
            return
        
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
        
        for idx, col in enumerate(numeric_cols):
            if idx < len(axes):
                sns.boxplot(data=self._df, y=col, ax=axes[idx])
                axes[idx].set_title(f'Box Plot of {col}')
                axes[idx].set_ylabel(col)
        
        # Hide extra subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def plot_scatter_matrix(
        self,
        columns: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (15, 15),
        alpha: float = 0.5
    ):
        """
        Create a scatter plot matrix for numeric columns.
        
        Args:
            columns (list, optional): Specific columns to plot
            figsize (tuple): Figure size (width, height)
            alpha (float): Transparency of points (0-1)
            
        Example:
            >>> visualizer.plot_scatter_matrix(['feature1', 'feature2', 'feature3'])
        """
        if columns:
            numeric_cols = [col for col in columns if col in self._df.select_dtypes(include=[np.number]).columns]
        else:
            numeric_cols = self._df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            print("⚠ Need at least 2 numeric columns for scatter matrix")
            return
        
        # Limit to first 5 columns if too many
        if len(numeric_cols) > 5:
            print(f"ℹ Showing first 5 of {len(numeric_cols)} columns")
            numeric_cols = numeric_cols[:5]
        
        pd.plotting.scatter_matrix(
            self._df[numeric_cols],
            figsize=figsize,
            alpha=alpha,
            diagonal='hist'
        )
        plt.suptitle('Scatter Plot Matrix', y=1.0)
        plt.tight_layout()
        plt.show()
    
    def plot_missing_values(self, figsize: Tuple[int, int] = (12, 6)):
        """
        Visualize missing values in the dataset.
        
        Args:
            figsize (tuple): Figure size (width, height)
            
        Example:
            >>> visualizer.plot_missing_values()
        """
        missing = self._df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        
        if len(missing) == 0:
            print("✓ No missing values to visualize!")
            return
        
        plt.figure(figsize=figsize)
        missing.plot(kind='bar')
        plt.title('Missing Values by Column')
        plt.xlabel('Column')
        plt.ylabel('Number of Missing Values')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def plot_pairplot(
        self,
        columns: Optional[List[str]] = None,
        hue: Optional[str] = None,
        height: float = 2.5
    ):
        """
        Create a pairplot (scatter plot matrix with distributions).
        
        Args:
            columns (list, optional): Specific columns to plot
            hue (str, optional): Column to use for color coding
            height (float): Height of each facet
            
        Example:
            >>> visualizer.plot_pairplot(hue='label')
        """
        if columns:
            df_subset = self._df[columns + ([hue] if hue and hue not in columns else [])]
        else:
            # Use only numeric columns and optionally hue
            numeric_cols = self._df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 5:
                print(f"ℹ Showing first 5 of {len(numeric_cols)} columns")
                numeric_cols = numeric_cols[:5]
            df_subset = self._df[numeric_cols + ([hue] if hue and hue not in numeric_cols else [])]
        
        if df_subset.empty:
            print("⚠ No data to plot")
            return
        
        try:
            sns.pairplot(df_subset, hue=hue, height=height, corner=True)
        except TypeError:
            # Fallback for older seaborn versions that don't support corner parameter
            sns.pairplot(df_subset, hue=hue, height=height)
        
        plt.suptitle('Pairplot of Features', y=1.0)
        plt.tight_layout()
        plt.show()
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Get the underlying pandas DataFrame."""
        return self._df
