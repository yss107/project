"""
Setup script for PhysicalAI-Autonomous-Vehicles dataset toolkit
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="physical-ai-av-toolkit",
    version="1.0.0",
    author="Yash Kumar",
    author_email="yash.kumar09@outlook.com",  # Update with actual email
    description="Python toolkit for NVIDIA's PhysicalAI-Autonomous-Vehicles dataset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yss107/project/tree/main/PhysicalAI_Autonomous_Vehicles",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
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
        "pyarrow>=6.0.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "DracoPy>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "tqdm>=4.62.0",
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "jupyter>=1.0.0",
            "ipywidgets>=7.6.0",
            "pytest>=6.0.0",
            "black>=21.0",
            "flake8>=3.9.0",
        ],
        "viz": [
            "plotly>=5.0.0",
            "open3d>=0.13.0",
        ],
    },
    package_data={
        "": ["*.yaml", "*.md"],
    },
    include_package_data=True,
    keywords=[
        "autonomous vehicles",
        "dataset",
        "computer vision",
        "lidar",
        "radar",
        "sensor fusion",
        "self-driving",
        "nvidia",
        "physical ai",
    ],
)
