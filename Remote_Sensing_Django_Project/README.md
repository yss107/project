# Remote Sensing Django Project

A Django web application for working with the **Major-TOM/Core-AlphaEarth-Embeddings** dataset from HuggingFace, designed for remote sensing applications.

![Django](https://img.shields.io/badge/Django-5.2.8-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Datasets-yellow)

## 📸 Screenshot

![Home Page Screenshot](https://github.com/user-attachments/assets/a956238a-7570-4f89-8f34-642cbead112f)

*Advanced home page featuring dashboard overview, quick search, interactive map preview, quick actions, and comprehensive feature cards*

## 📋 Overview

This project provides a comprehensive web interface for managing and analyzing satellite imagery data from the Major-TOM/Core-AlphaEarth-Embeddings dataset. It combines Django's powerful web framework with HuggingFace's datasets library to create a seamless platform for remote sensing applications.

## ✨ Features

### Core Features
- 🌍 **HuggingFace Dataset Integration** - Direct integration with Major-TOM/Core-AlphaEarth-Embeddings dataset
- 📊 **Data Management** - Store and organize satellite imagery metadata with rich filtering options
- 🔍 **Advanced Search** - Filter images by dataset split, grid cell, timestamp, and more
- 📈 **Analysis Tracking** - Record and manage analysis results for satellite images
- 🎨 **Modern UI** - Responsive design built with Bootstrap 5 and Font Awesome icons
- 🔐 **Admin Interface** - Full-featured Django admin panel for data management
- 📱 **Mobile-Friendly** - Fully responsive design that works on all devices

### Advanced Features (New!)
- 🔎 **Quick Search** - Instantly search satellite images by grid cell from the home page
- 🗺️ **Interactive Map Preview** - Visual representation of global satellite coverage
- 📊 **Dashboard Overview** - Real-time statistics including image count, analyses, and embedding dimensions
- ⚡ **Quick Actions Panel** - One-click access to common tasks (Browse Images, Training Data, Dataset Info, Admin)
- 📋 **Dataset Overview Section** - Comprehensive information about available data splits (Train/Validation/Test)
- 🏷️ **Technology Stack Display** - Visual showcase of the technologies powering the application
- 🎯 **Enhanced Feature Cards** - Detailed feature descriptions with capability lists

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd Remote_Sensing_Django_Project
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set up your admin username, email, and password.

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser and navigate to:**
   - Main Application: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```
Remote_Sensing_Django_Project/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── remote_sensing_project/        # Main project configuration
│   ├── __init__.py
│   ├── settings.py               # Project settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── sensing/                       # Main application
│   ├── __init__.py
│   ├── admin.py                  # Admin interface configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── urls.py                   # App URL configuration
│   ├── utils.py                  # Utility functions for HuggingFace integration
│   ├── tests.py                  # Test cases
│   └── migrations/               # Database migrations
├── templates/                     # HTML templates
│   └── sensing/
│       ├── base.html             # Base template
│       ├── index.html            # Home page
│       ├── image_list.html       # Image listing
│       ├── image_detail.html     # Image details
│       ├── dataset_info.html     # Dataset information
│       └── about.html            # About page
└── static/                        # Static files (CSS, JS, images)
    ├── css/
    └── js/
```

## 💾 Database Models

### SatelliteImage
Stores satellite image metadata:
- Image ID and grid cell information
- Temporal information (timestamp)
- Spatial information (latitude, longitude)
- Image properties (cloud cover, spatial resolution)
- Dataset split (train/validation/test)
- Embedding vectors

### RemoteSensingAnalysis
Stores analysis results:
- Reference to satellite image
- Analysis type and results
- Confidence scores
- Performance timestamps and notes

## 🔧 Usage

### Accessing the Admin Panel

1. Navigate to `http://127.0.0.1:8000/admin/`
2. Log in with your superuser credentials
3. Add, edit, or delete satellite images and analyses

### Loading Data from HuggingFace

You can use the utility functions in `sensing/utils.py` to load data from the dataset:

```python
from sensing.utils import load_dataset_sample, load_dataset_info

# Load dataset information
info = load_dataset_info()

# Load a sample of images
samples = load_dataset_sample(split='train', num_samples=10)
```

### Adding Data via Django Shell

```bash
python manage.py shell
```

```python
from sensing.models import SatelliteImage
from datetime import datetime

# Create a sample satellite image
image = SatelliteImage.objects.create(
    image_id='sample_001',
    grid_cell='A1B2',
    timestamp=datetime.now(),
    latitude=40.7128,
    longitude=-74.0060,
    cloud_cover=15.5,
    spatial_resolution=10.0,
    dataset_split='train'
)
```

## 🌐 Available Pages

- **Home** (`/`) - Overview with statistics and recent images
- **Images** (`/images/`) - Browse and filter satellite images
- **Image Detail** (`/images/<id>/`) - Detailed information about a specific image
- **Dataset Info** (`/dataset-info/`) - Information about the HuggingFace dataset
- **About** (`/about/`) - Project information and documentation
- **Admin** (`/admin/`) - Django admin interface

## 🔍 Features in Detail

### Filtering and Search
- Filter images by dataset split (train/validation/test)
- Search by grid cell
- Browse paginated results (20 images per page)

### Data Management
- Add images manually through admin panel
- Import data from HuggingFace dataset
- Track analyses and results
- Store embedding vectors

### Responsive Design
- Mobile-friendly interface
- Bootstrap 5 components
- Font Awesome icons
- Clean and modern UI

## 📚 Dataset Information

This project uses the **Major-TOM/Core-AlphaEarth-Embeddings** dataset from HuggingFace:

- **Source**: [HuggingFace Datasets](https://huggingface.co/datasets/Major-TOM/Core-AlphaEarth-Embeddings)
- **Purpose**: Remote sensing and satellite imagery analysis
- **Features**: Pre-computed embeddings for efficient analysis

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Making Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

For production deployment:

```bash
python manage.py collectstatic
```

## 📝 Requirements

- Django==5.2.8
- datasets==4.4.1
- huggingface_hub==1.1.5
- numpy==2.3.5
- pillow==12.0.0

See `requirements.txt` for complete list.

## 🚦 Future Enhancements

Potential areas for expansion:
- Image upload and storage
- Advanced visualization of embeddings
- Machine learning model integration
- Batch data import from HuggingFace
- RESTful API endpoints
- User authentication and permissions
- Advanced analytics dashboard
- Export functionality

## 🤝 Contributing

This project is part of a portfolio of data science and machine learning projects. Feel free to fork and extend it for your own use cases.

## 📄 License

This project is provided for educational and reference purposes.

## 👤 Author

**Yash Kumar**
- Portfolio: [yss107.github.io](https://yss107.github.io)
- LinkedIn: [yash-kumar09](https://www.linkedin.com/in/yash-kumar09/)

## 🙏 Acknowledgments

- HuggingFace for providing the datasets library and hosting the Major-TOM dataset
- Django community for the excellent web framework
- Bootstrap team for the UI components

---

**Built with ❤️ using Django and HuggingFace Datasets**
