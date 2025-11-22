# 📊 PleIAs SYNTH Dataset Project

[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/datasets/PleIAs/SYNTH)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

A comprehensive Python toolkit for working with the PleIAs SYNTH dataset - a synthetic data collection available on HuggingFace for machine learning and data science applications.

## 📊 Dataset Overview

The **PleIAs SYNTH** dataset is a synthetic dataset designed for machine learning research and development. Synthetic datasets are valuable for:
- Training models when real data is scarce or sensitive
- Testing ML pipelines without privacy concerns
- Augmenting existing datasets
- Benchmarking algorithms
- Educational purposes

### 🎯 Dataset Access
The dataset is available on HuggingFace: [PleIAs/SYNTH](https://huggingface.co/datasets/PleIAs/SYNTH)

## 🎯 Features

This project provides:
- 📦 Easy data loading utilities for the SYNTH dataset
- 🔍 Data exploration and analysis tools
- 📊 Visualization utilities
- 🛠️ Data preprocessing pipelines
- 📝 Comprehensive documentation
- 💻 Example notebooks

## 🚀 Quick Start

### Installation

```bash
# Clone this repository
git clone https://github.com/yss107/project.git
cd project/SYNTH_Dataset_Project

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from utils import SYNTHLoader, DataExplorer, DataVisualizer

# Initialize the dataset loader
loader = SYNTHLoader()

# Load the dataset
dataset = loader.load_dataset()

# Explore the dataset
explorer = DataExplorer(dataset)
explorer.print_summary()
explorer.show_statistics()

# Visualize data
visualizer = DataVisualizer(dataset)
visualizer.plot_distributions()
visualizer.create_correlation_matrix()
```

### Loading Dataset from HuggingFace

```python
from datasets import load_dataset

# Load the complete dataset
dataset = load_dataset("PleIAs/SYNTH")

# Load a specific split
train_data = load_dataset("PleIAs/SYNTH", split="train")
test_data = load_dataset("PleIAs/SYNTH", split="test")

# Load with streaming (for large datasets)
dataset = load_dataset("PleIAs/SYNTH", streaming=True)
```

## 📁 Project Structure

```
SYNTH_Dataset_Project/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup file
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── data_loader.py        # Dataset loading utilities
│   ├── data_explorer.py      # Data exploration tools
│   ├── data_visualizer.py    # Visualization tools
│   └── preprocessing.py      # Data preprocessing utilities
├── examples/                 # Example notebooks
│   ├── 01_getting_started.ipynb
│   ├── 02_data_analysis.ipynb
│   └── 03_model_training.ipynb
├── docs/                     # Documentation
│   ├── DATA_FORMAT.md
│   ├── USAGE_GUIDE.md
│   └── API_REFERENCE.md
└── data/                     # Local data directory (cached)
    └── .gitkeep
```

## 📚 Key Components

### 1. Data Loaders (`utils/`)
- `data_loader.py`: Main dataset loading utilities
- `data_explorer.py`: Tools for exploring dataset characteristics
- `data_visualizer.py`: Visualization and plotting functions
- `preprocessing.py`: Data preprocessing and transformation utilities

### 2. Documentation (`docs/`)
- `DATA_FORMAT.md`: Data format specifications
- `USAGE_GUIDE.md`: Detailed usage guide
- `API_REFERENCE.md`: Complete API documentation

### 3. Examples (`examples/`)
- `01_getting_started.ipynb`: Dataset exploration and basic usage
- `02_data_analysis.ipynb`: In-depth data analysis
- `03_model_training.ipynb`: Training ML models with the dataset

## 🔬 Use Cases

This dataset and toolkit are ideal for:
- 🤖 Machine Learning model training and evaluation
- 📊 Data science research and development
- 🎓 Educational projects and tutorials
- 🔍 Algorithm benchmarking
- 🧪 Testing ML pipelines
- 📈 Data augmentation strategies

## 🛠️ Requirements

- Python 3.8+
- datasets (HuggingFace)
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- jupyter

See `requirements.txt` for complete list.

## 📖 Documentation

Detailed documentation available in `docs/`:
- [Data Format Specification](docs/DATA_FORMAT.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)

## 🎓 Examples

### Load and Display Dataset Info
```python
from utils import SYNTHLoader

loader = SYNTHLoader()
info = loader.get_dataset_info()
print(f"Dataset: {info['name']}")
print(f"Features: {info['features']}")
print(f"Size: {info['num_rows']} rows")
```

### Preprocess Data
```python
from utils import DataPreprocessor

preprocessor = DataPreprocessor()
processed_data = preprocessor.apply_pipeline(dataset)
```

### Train a Model
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from utils import SYNTHLoader

# Load dataset
loader = SYNTHLoader()
X, y = loader.prepare_for_training()

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)
score = model.score(X_test, y_test)
print(f"Model Accuracy: {score:.2%}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report issues
- Submit pull requests
- Suggest features
- Improve documentation

## 📧 Contact

For questions or collaboration:
- **Author**: Yash Kumar
- **LinkedIn**: [yash-kumar09](https://www.linkedin.com/in/yash-kumar09/)
- **GitHub**: [yss107](https://github.com/yss107)

## 🙏 Acknowledgments

Dataset provided by **PleIAs** and made available on HuggingFace.

Special thanks to the HuggingFace team for providing an excellent platform for dataset sharing and the PleIAs team for creating and sharing the SYNTH dataset.

---

<div align="center">

**Made with ❤️ for Data Science and Machine Learning**

⭐ Star this repository if you find it useful!

</div>

## 📄 License

This project is provided for educational and research purposes. Please refer to the [HuggingFace dataset page](https://huggingface.co/datasets/PleIAs/SYNTH) for the dataset's specific license terms.

---

<div align="center">

Made with ❤️ by Yash Kumar | © 2025

</div>
