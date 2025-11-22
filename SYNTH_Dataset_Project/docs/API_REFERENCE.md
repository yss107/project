# API Reference - SYNTH Dataset Project

## Table of Contents
1. [SYNTHLoader](#synthloader)
2. [DataExplorer](#dataexplorer)
3. [DataVisualizer](#datavisualizer)
4. [DataPreprocessor](#datapreprocessor)

---

## SYNTHLoader

Class for loading and accessing the PleIAs SYNTH dataset from HuggingFace.

### Constructor

```python
SYNTHLoader(cache_dir: Optional[str] = None)
```

**Parameters:**
- `cache_dir` (str, optional): Directory to cache downloaded data. Defaults to './data/cache'

**Example:**
```python
loader = SYNTHLoader(cache_dir='/path/to/cache')
```

### Methods

#### `load_dataset()`

```python
load_dataset(
    split: Optional[str] = None,
    streaming: bool = False,
    trust_remote_code: bool = True
) -> Union[Dataset, DatasetDict]
```

Load the SYNTH dataset from HuggingFace.

**Parameters:**
- `split` (str, optional): Specific split to load ('train', 'test', etc.)
- `streaming` (bool): Whether to stream the dataset
- `trust_remote_code` (bool): Whether to trust remote code

**Returns:**
- Dataset or DatasetDict: The loaded dataset

---

#### `load_as_pandas()`

```python
load_as_pandas(
    split: Optional[str] = None,
    max_rows: Optional[int] = None
) -> pd.DataFrame
```

Load the dataset as a pandas DataFrame.

**Parameters:**
- `split` (str, optional): Specific split to load
- `max_rows` (int, optional): Maximum number of rows to load

**Returns:**
- pd.DataFrame: Dataset as a pandas DataFrame

---

#### `get_dataset_info()`

```python
get_dataset_info() -> Dict[str, Any]
```

Get information about the dataset.

**Returns:**
- dict: Dictionary containing dataset information

---

#### `prepare_for_training()`

```python
prepare_for_training(
    feature_columns: Optional[list] = None,
    target_column: str = 'label',
    split: Optional[str] = 'train'
) -> tuple
```

Prepare dataset for machine learning training.

**Parameters:**
- `feature_columns` (list, optional): List of feature column names
- `target_column` (str): Name of the target column
- `split` (str, optional): Which split to use

**Returns:**
- tuple: (X, y) where X is features and y is target

---

### Properties

#### `dataset`

```python
@property
dataset -> Union[Dataset, DatasetDict, None]
```

Get the currently loaded dataset.

---

## DataExplorer

Class for analyzing and exploring the SYNTH dataset.

### Constructor

```python
DataExplorer(data)
```

**Parameters:**
- `data`: Dataset to explore (pd.DataFrame, Dataset, or DatasetDict)

### Methods

#### `print_summary()`

```python
print_summary()
```

Print a comprehensive summary of the dataset.

---

#### `show_statistics()`

```python
show_statistics(columns: Optional[List[str]] = None)
```

Show statistical summary of the dataset.

**Parameters:**
- `columns` (list, optional): Specific columns to analyze

---

#### `check_missing_values()`

```python
check_missing_values() -> pd.DataFrame
```

Check for missing values in the dataset.

**Returns:**
- pd.DataFrame: DataFrame with missing value statistics

---

#### `analyze_column()`

```python
analyze_column(column_name: str) -> Dict[str, Any]
```

Perform detailed analysis of a specific column.

**Parameters:**
- `column_name` (str): Name of the column to analyze

**Returns:**
- dict: Dictionary containing column analysis

---

#### `get_correlations()`

```python
get_correlations(method: str = 'pearson') -> pd.DataFrame
```

Calculate correlation matrix for numeric columns.

**Parameters:**
- `method` (str): Correlation method ('pearson', 'spearman', 'kendall')

**Returns:**
- pd.DataFrame: Correlation matrix

---

#### `find_duplicates()`

```python
find_duplicates() -> pd.DataFrame
```

Find duplicate rows in the dataset.

**Returns:**
- pd.DataFrame: Duplicate rows

---

### Properties

#### `dataframe`

```python
@property
dataframe -> pd.DataFrame
```

Get the underlying pandas DataFrame.

---

## DataVisualizer

Class for creating visualizations of the SYNTH dataset.

### Constructor

```python
DataVisualizer(data, style: str = 'whitegrid')
```

**Parameters:**
- `data`: Dataset to visualize (pd.DataFrame, Dataset, or DatasetDict)
- `style` (str): Seaborn style ('whitegrid', 'darkgrid', 'white', 'dark', 'ticks')

### Methods

#### `plot_distributions()`

```python
plot_distributions(
    columns: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (15, 10)
)
```

Plot distributions of numeric columns.

**Parameters:**
- `columns` (list, optional): Specific columns to plot
- `figsize` (tuple): Figure size (width, height)

---

#### `plot_categorical()`

```python
plot_categorical(
    columns: Optional[List[str]] = None,
    top_n: int = 10,
    figsize: Tuple[int, int] = (15, 10)
)
```

Plot bar charts for categorical columns.

**Parameters:**
- `columns` (list, optional): Specific columns to plot
- `top_n` (int): Number of top categories to show
- `figsize` (tuple): Figure size (width, height)

---

#### `create_correlation_matrix()`

```python
create_correlation_matrix(
    method: str = 'pearson',
    figsize: Tuple[int, int] = (12, 10),
    annot: bool = True
)
```

Create a correlation heatmap for numeric columns.

**Parameters:**
- `method` (str): Correlation method ('pearson', 'spearman', 'kendall')
- `figsize` (tuple): Figure size (width, height)
- `annot` (bool): Whether to annotate cells with values

---

#### `plot_boxplots()`

```python
plot_boxplots(
    columns: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (15, 10)
)
```

Create box plots for numeric columns.

**Parameters:**
- `columns` (list, optional): Specific columns to plot
- `figsize` (tuple): Figure size (width, height)

---

#### `plot_scatter_matrix()`

```python
plot_scatter_matrix(
    columns: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (15, 15),
    alpha: float = 0.5
)
```

Create a scatter plot matrix for numeric columns.

**Parameters:**
- `columns` (list, optional): Specific columns to plot
- `figsize` (tuple): Figure size (width, height)
- `alpha` (float): Transparency of points (0-1)

---

#### `plot_missing_values()`

```python
plot_missing_values(figsize: Tuple[int, int] = (12, 6))
```

Visualize missing values in the dataset.

**Parameters:**
- `figsize` (tuple): Figure size (width, height)

---

#### `plot_pairplot()`

```python
plot_pairplot(
    columns: Optional[List[str]] = None,
    hue: Optional[str] = None,
    height: float = 2.5
)
```

Create a pairplot (scatter plot matrix with distributions).

**Parameters:**
- `columns` (list, optional): Specific columns to plot
- `hue` (str, optional): Column to use for color coding
- `height` (float): Height of each facet

---

### Properties

#### `dataframe`

```python
@property
dataframe -> pd.DataFrame
```

Get the underlying pandas DataFrame.

---

## DataPreprocessor

Class for preprocessing and transforming the SYNTH dataset.

### Constructor

```python
DataPreprocessor()
```

### Methods

#### `handle_missing_values()`

```python
handle_missing_values(
    df: pd.DataFrame,
    strategy: str = 'mean',
    columns: Optional[List[str]] = None
) -> pd.DataFrame
```

Handle missing values in the dataset.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `strategy` (str): Imputation strategy ('mean', 'median', 'most_frequent', 'constant')
- `columns` (list, optional): Specific columns to impute

**Returns:**
- pd.DataFrame: Dataframe with imputed values

---

#### `encode_categorical()`

```python
encode_categorical(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'label',
    drop_first: bool = False
) -> pd.DataFrame
```

Encode categorical variables.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `columns` (list, optional): Columns to encode
- `method` (str): Encoding method ('label', 'onehot')
- `drop_first` (bool): For onehot, whether to drop first category

**Returns:**
- pd.DataFrame: Dataframe with encoded variables

---

#### `scale_features()`

```python
scale_features(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'standard'
) -> pd.DataFrame
```

Scale numeric features.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `columns` (list, optional): Columns to scale
- `method` (str): Scaling method ('standard', 'minmax')

**Returns:**
- pd.DataFrame: Dataframe with scaled features

---

#### `remove_outliers()`

```python
remove_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'iqr',
    threshold: float = 1.5
) -> pd.DataFrame
```

Remove outliers from numeric columns.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `columns` (list, optional): Columns to check
- `method` (str): Detection method ('iqr', 'zscore')
- `threshold` (float): Threshold for outlier detection

**Returns:**
- pd.DataFrame: Dataframe with outliers removed

---

#### `apply_pipeline()`

```python
apply_pipeline(
    df: pd.DataFrame,
    steps: Optional[List[Dict[str, Any]]] = None
) -> pd.DataFrame
```

Apply a preprocessing pipeline with multiple steps.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `steps` (list): List of preprocessing steps as dictionaries

**Returns:**
- pd.DataFrame: Fully preprocessed dataframe

---

#### `train_test_split_data()`

```python
train_test_split_data(
    df: pd.DataFrame,
    target_column: str,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple
```

Split data into train and test sets.

**Parameters:**
- `df` (pd.DataFrame): Input dataframe
- `target_column` (str): Name of target column
- `test_size` (float): Proportion of test set
- `random_state` (int): Random seed

**Returns:**
- tuple: (X_train, X_test, y_train, y_test)

---

## Convenience Functions

### `quick_load()`

```python
quick_load(
    split: Optional[str] = None,
    max_rows: Optional[int] = None
) -> pd.DataFrame
```

Quick load the SYNTH dataset as a pandas DataFrame.

**Parameters:**
- `split` (str, optional): Specific split to load
- `max_rows` (int, optional): Maximum number of rows to load

**Returns:**
- pd.DataFrame: Dataset as a pandas DataFrame

**Example:**
```python
from utils.data_loader import quick_load
df = quick_load(split='train', max_rows=1000)
```

---

## Usage Examples

### Complete Workflow

```python
from utils import SYNTHLoader, DataExplorer, DataVisualizer, DataPreprocessor

# 1. Load data
loader = SYNTHLoader()
dataset = loader.load_dataset()
df = loader.load_as_pandas(split='train')

# 2. Explore data
explorer = DataExplorer(df)
explorer.print_summary()
explorer.show_statistics()

# 3. Visualize data
visualizer = DataVisualizer(df)
visualizer.plot_distributions()
visualizer.create_correlation_matrix()

# 4. Preprocess data
preprocessor = DataPreprocessor()
df_processed = preprocessor.apply_pipeline(df)

# 5. Prepare for training
X, y = loader.prepare_for_training(target_column='label')
```

---

For more detailed examples, see the notebooks in the `examples/` directory.
