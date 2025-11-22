"""
Setup script for SYNTH Dataset Project
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="synth-dataset-project",
    version="1.0.0",
    author="Yash Kumar",
    author_email="yash.kumar@example.com",
    description="A comprehensive Python toolkit for working with the PleIAs SYNTH dataset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yss107/project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "datasets>=2.0.0",
        "huggingface-hub>=0.10.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pyarrow>=6.0.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "jupyter>=1.0.0",
            "ipywidgets>=7.6.0",
            "notebook>=6.4.0",
        ],
    },
    keywords="dataset, synthetic-data, machine-learning, data-science, huggingface",
    project_urls={
        "Dataset": "https://huggingface.co/datasets/PleIAs/SYNTH",
        "Source": "https://github.com/yss107/project",
    },
)
