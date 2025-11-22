# Usage Guide - SYNTH Dataset Project

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Loading Data](#loading-data)
4. [Exploring Data](#exploring-data)
5. [Visualization](#visualization)
6. [Preprocessing](#preprocessing)
7. [Model Training](#model-training)
8. [Advanced Usage](#advanced-usage)

## Installation

### Requirements
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd SYNTH_Dataset_Project
pip install -r requirements.txt
```

### Verify Installation

```python
from utils import SYNTHLoader
print("✓ Installation successful!")
```

## Quick Start

### Load and Explore Dataset

```python
from utils import SYNTHLoader, DataExplorer

# Load dataset
loader = SYNTHLoader()
dataset = loader.load_dataset()

# Explore
explorer = DataExplorer(dataset)
explorer.print_summary()
```

## Loading Data

### Basic Loading

```python
from utils import SYNTHLoader

loader = SYNTHLoader()

# Load entire dataset
dataset = loader.load_dataset()

# Load specific split
train_data = loader.load_dataset(split='train')
```

### Load as Pandas DataFrame

```python
# Load first 1000 rows
df = loader.load_as_pandas(split='train', max_rows=1000)

# Load all data
df = loader.load_as_pandas(split='train')
```

### Streaming Mode (for Large Datasets)

```python
# Stream data instead of loading all at once
dataset = loader.load_dataset(streaming=True)

for example in dataset:
    # Process one example at a time
    pass
```

### Custom Cache Directory

```python
loader = SYNTHLoader(cache_dir='/path/to/cache')
dataset = loader.load_dataset()
```

## Exploring Data

### Dataset Information

```python
from utils import DataExplorer

explorer = DataExplorer(dataset)

# Print comprehensive summary
explorer.print_summary()

# Show statistics
explorer.show_statistics()

# Check missing values
missing = explorer.check_missing_values()

# Find duplicates
duplicates = explorer.find_duplicates()
```

### Column Analysis

```python
# Analyze specific column
analysis = explorer.analyze_column('column_name')

# Get correlations
correlations = explorer.get_correlations(method='pearson')
```

## Visualization

### Basic Plots

```python
from utils import DataVisualizer

visualizer = DataVisualizer(dataset)

# Plot distributions
visualizer.plot_distributions()

# Plot categorical variables
visualizer.plot_categorical(top_n=10)

# Create correlation heatmap
visualizer.create_correlation_matrix()
```

### Advanced Visualizations

```python
# Box plots for outlier detection
visualizer.plot_boxplots()

# Scatter plot matrix
visualizer.plot_scatter_matrix()

# Pairplot with color coding
visualizer.plot_pairplot(hue='label_column')

# Missing values visualization
visualizer.plot_missing_values()
```

## Preprocessing

### Handle Missing Values

```python
from utils import DataPreprocessor

preprocessor = DataPreprocessor()

# Impute missing values
df_clean = preprocessor.handle_missing_values(
    df, 
    strategy='median'  # or 'mean', 'most_frequent'
)
```

### Encode Categorical Variables

```python
# Label encoding
df_encoded = preprocessor.encode_categorical(
    df,
    method='label'
)

# One-hot encoding
df_encoded = preprocessor.encode_categorical(
    df,
    method='onehot',
    drop_first=True
)
```

### Scale Features

```python
# Standard scaling (z-score normalization)
df_scaled = preprocessor.scale_features(
    df,
    method='standard'
)

# Min-max scaling
df_scaled = preprocessor.scale_features(
    df,
    method='minmax'
)
```

### Remove Outliers

```python
# Using IQR method
df_clean = preprocessor.remove_outliers(
    df,
    method='iqr',
    threshold=1.5
)

# Using Z-score method
df_clean = preprocessor.remove_outliers(
    df,
    method='zscore',
    threshold=3
)
```

### Complete Pipeline

```python
# Define preprocessing steps
steps = [
    {'method': 'handle_missing_values', 'strategy': 'median'},
    {'method': 'encode_categorical', 'method': 'onehot'},
    {'method': 'scale_features', 'method': 'standard'}
]

# Apply pipeline
df_processed = preprocessor.apply_pipeline(df, steps)
```

## Model Training

### Prepare Data for Training

```python
loader = SYNTHLoader()

# Load and prepare
X, y = loader.prepare_for_training(
    target_column='label',
    split='train'
)
```

### Train-Test Split

```python
X_train, X_test, y_train, y_test = preprocessor.train_test_split_data(
    df,
    target_column='label',
    test_size=0.2,
    random_state=42
)
```

### Training Example

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
```

## Advanced Usage

### Custom Data Loading

```python
from datasets import load_dataset

# Load with specific configuration
dataset = load_dataset(
    "PleIAs/SYNTH",
    split="train",
    cache_dir="./cache",
    trust_remote_code=True
)
```

### Batch Processing

```python
# Process data in batches
batch_size = 1000
for i in range(0, len(df), batch_size):
    batch = df[i:i+batch_size]
    # Process batch
    processed_batch = preprocessor.apply_pipeline(batch)
```

### Parallel Processing

```python
from multiprocessing import Pool

def process_chunk(chunk):
    preprocessor = DataPreprocessor()
    return preprocessor.apply_pipeline(chunk)

# Split data into chunks
chunks = np.array_split(df, 4)

# Process in parallel
with Pool(4) as pool:
    results = pool.map(process_chunk, chunks)

# Combine results
df_processed = pd.concat(results)
```

## Best Practices

### Memory Management
```python
# Load data in chunks for large datasets
df = loader.load_as_pandas(max_rows=10000)

# Use streaming mode
dataset = loader.load_dataset(streaming=True)
```

### Reproducibility
```python
# Always set random seeds
import random
import numpy as np

random.seed(42)
np.random.seed(42)
```

### Data Validation
```python
# Always validate data after preprocessing
explorer = DataExplorer(df_processed)
explorer.check_missing_values()
explorer.show_statistics()
```

## Troubleshooting

### Connection Issues
```python
# If HuggingFace is unreachable, use cached data
loader = SYNTHLoader(cache_dir='./local_cache')
```

### Memory Errors
```python
# Use streaming or load smaller batches
dataset = loader.load_dataset(streaming=True)
df = loader.load_as_pandas(max_rows=5000)
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Examples

See the `examples/` directory for complete Jupyter notebooks:
- `01_getting_started.ipynb`: Basic usage and exploration
- Additional notebooks for specific use cases

## Support

For issues and questions:
- Check the documentation in `docs/`
- Review example notebooks in `examples/`
- Visit the [HuggingFace dataset page](https://huggingface.co/datasets/PleIAs/SYNTH)

## References

- [HuggingFace Datasets Documentation](https://huggingface.co/docs/datasets)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
