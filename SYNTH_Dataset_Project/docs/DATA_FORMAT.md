# Data Format Specification - SYNTH Dataset

## Overview

The PleIAs SYNTH dataset is a synthetic dataset available on HuggingFace. This document describes the expected data format and structure.

## Dataset Structure

### Accessing the Dataset

The dataset can be accessed through HuggingFace's `datasets` library:

```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("PleIAs/SYNTH")

# Load specific split
train_data = load_dataset("PleIAs/SYNTH", split="train")
test_data = load_dataset("PleIAs/SYNTH", split="test")
```

### Dataset Splits

The dataset may contain multiple splits:
- `train`: Training data
- `test`: Test data
- `validation`: Validation data (if available)

## Data Fields

The exact fields in the dataset depend on its specific configuration. Common fields in synthetic datasets include:

### Numeric Features
- Continuous variables (floats)
- Discrete variables (integers)
- Binary indicators (0/1)

### Categorical Features
- Text labels
- Category codes
- Enumerated types

### Target Variable
- Classification labels
- Regression targets
- Multi-label outputs

## Data Types

### Supported Types
- `int64`: Integer values
- `float64`: Floating-point values
- `string`: Text values
- `category`: Categorical values
- `bool`: Boolean values

## File Formats

The dataset supports various formats:
- **Parquet**: Columnar storage format (default)
- **CSV**: Comma-separated values
- **JSON**: JavaScript Object Notation
- **Arrow**: Apache Arrow format

## Data Quality

### Completeness
- Check for missing values using `df.isnull().sum()`
- Handle missing data appropriately

### Consistency
- Verify data types are consistent
- Check for unexpected values

### Validity
- Ensure values fall within expected ranges
- Validate categorical values against known categories

## Loading Examples

### Load as Pandas DataFrame
```python
from datasets import load_dataset
import pandas as pd

dataset = load_dataset("PleIAs/SYNTH", split="train")
df = dataset.to_pandas()
```

### Streaming Large Datasets
```python
dataset = load_dataset("PleIAs/SYNTH", streaming=True)
for example in dataset:
    # Process example
    pass
```

### Load Specific Columns
```python
dataset = load_dataset("PleIAs/SYNTH", columns=["feature1", "feature2", "label"])
```

## Caching

The dataset is automatically cached locally after first download:
- Default cache location: `~/.cache/huggingface/datasets/`
- Custom cache: Specify `cache_dir` parameter

## Data Version

Always check the dataset version and any updates:
```python
from datasets import load_dataset_builder

builder = load_dataset_builder("PleIAs/SYNTH")
print(builder.info.version)
```

## Additional Resources

- [HuggingFace Datasets Documentation](https://huggingface.co/docs/datasets)
- [SYNTH Dataset on HuggingFace](https://huggingface.co/datasets/PleIAs/SYNTH)

## Notes

- This is a synthetic dataset, meaning the data is artificially generated
- Synthetic data is useful for testing, development, and privacy-preserving analysis
- Always verify the data characteristics match your use case requirements
