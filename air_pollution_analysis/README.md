# Air Pollution Analysis Dashboard 🌍

A real-time web dashboard for analyzing and comparing air pollution data (PM2.5 and PM10) from New York City and Bogota. This project analyzes historical air quality data and provides interactive visualizations to understand pollution patterns, trends, and WHO guideline compliance.

## 📋 Overview

This project analyzes air pollution data from two monitoring stations:
- **New York City** - Queens College Station (PM2.5 data)
- **Bogota** - San Cristobal Station (PM2.5 and PM10 data)

**Data Period:** September 2016 - April 2017 (hourly measurements)

## ✨ Features

### 1. **Interactive Dashboard**
- Modern, responsive web interface
- Real-time data visualization using Plotly.js
- Multiple analysis views with tabbed navigation

### 2. **Comprehensive Analysis**
- **Time Series Analysis**: Hourly and daily pollution trends
- **Pattern Recognition**: Hourly and monthly pollution patterns
- **City Comparison**: Direct comparison between NYC and Bogota
- **WHO Compliance**: Check against World Health Organization air quality guidelines

### 3. **Key Insights**
- Statistical summaries (mean, median, std dev, min/max)
- Correlation analysis between cities
- Seasonal pattern detection
- Exceedance detection for WHO limits

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd air_pollution_analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate sample data (if needed):**
   ```bash
   cd data
   python generate_sample_data.py
   cd ..
   ```

### Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## 📊 Dashboard Sections

### Overview Tab
- Quick statistics for both cities
- Key insights and comparisons
- WHO compliance summary

### Time Series Tab
- Hourly PM2.5 measurements
- Daily averages
- Toggle between cities
- WHO guideline reference lines

### Patterns Tab
- **Hourly Pattern**: Average pollution by hour of day
- **Monthly Pattern**: Average pollution by month
- Identify peak pollution times

### City Comparison Tab
- Side-by-side comparison of NYC vs Bogota
- Correlation coefficient
- Percentage of time NYC pollution exceeds Bogota

### WHO Limits Tab
- Annual mean compliance check
- 24-hour exceedance detection
- Timeline of exceedance events
- PM10 compliance (Bogota only)

## 📈 Analysis Highlights

### WHO Air Quality Guidelines (2021)
- **PM2.5 Annual Mean**: ≤ 5 μg/m³
- **PM2.5 24-hour Mean**: ≤ 15 μg/m³
- **PM10 Annual Mean**: ≤ 15 μg/m³
- **PM10 24-hour Mean**: ≤ 45 μg/m³

### Key Findings
1. **Pollution Levels**: Analysis shows average pollution levels and variability in both cities
2. **Temporal Patterns**: Identifies when pollution is highest/lowest during the day and year
3. **Comparative Analysis**: Shows correlation and differences between the two cities
4. **Compliance**: Tracks WHO guideline compliance and exceedance events

## 🛠️ Technical Stack

- **Backend**: Flask (Python web framework)
- **Data Analysis**: pandas, numpy, scipy
- **Visualization**: Plotly.js
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Format**: Pipe-delimited text files (|)

## 📁 Project Structure

```
air_pollution_analysis/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   ├── StationData-NY_QueensCollege.txt
│   ├── StationData-Bogota_SanCristobal.txt
│   └── generate_sample_data.py
├── analysis/
│   └── pollution_analyzer.py   # Data analysis module
├── templates/
│   └── index.html              # Main dashboard template
└── static/
    ├── css/
    │   └── style.css           # Dashboard styles
    └── js/
        └── dashboard.js        # Dashboard interactions
```

## 🔧 API Endpoints

- `GET /` - Main dashboard page
- `GET /api/stats/<city>` - Basic statistics for a city
- `GET /api/timeseries/<city>/<pollutant>` - Time series data
- `GET /api/daily/<city>/<pollutant>` - Daily averages
- `GET /api/hourly/<city>/<pollutant>` - Hourly pattern
- `GET /api/monthly/<city>/<pollutant>` - Monthly pattern
- `GET /api/compare` - City comparison data
- `GET /api/who-limits/<city>` - WHO compliance data
- `GET /api/summary` - Comprehensive summary

## 📝 Data Sources

- **NYC Data**: New York State Department of Environmental Conservation
- **Bogota Data**: Red de Monitoreo de Calidad del Aire de Bogotá (RMCAB) - Bogota Air Quality Monitoring Network

## 🤝 Contributing

This project was created as a data science assignment. Feel free to fork and enhance it with:
- Additional visualizations
- More statistical analyses
- Machine learning predictions
- Additional cities/stations
- Real-time data integration

## 📄 License

This project is created for educational and demonstration purposes.

## 👥 Authors

Created as a take-home assignment for World Health Organization data science positions.

## 🙏 Acknowledgments

- World Health Organization for air quality guidelines
- NYC Department of Environmental Conservation
- Bogota Air Quality Monitoring Network (RMCAB)
- Plotly for visualization library

---

**Note**: The sample data provided is generated for demonstration purposes. For production use, replace with actual air quality monitoring data from official sources.
