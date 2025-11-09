# Air Pollution Analysis Dashboard 🌍

A comprehensive real-time web dashboard for analyzing and monitoring air pollution data worldwide. This project provides **real-time air quality monitoring for any city in the world**, along with historical data analysis from New York City and Bogota.

## 📋 Overview

This project provides two main capabilities:

### 🌏 **Worldwide Real-Time Air Quality Monitor** (NEW!)
- **Search any city worldwide** - Get live air pollution data for any location
- **Real-time updates** - Current PM2.5, PM10, NO₂, SO₂, CO, and O₃ levels
- **Interactive world map** - Visual representation of air quality across major cities
- **24-hour forecast** - Predict air quality trends
- **WHO compliance checking** - Compare readings against WHO guidelines
- **Popular cities dashboard** - Monitor major urban centers globally
- Powered by OpenWeatherMap Air Pollution API (works in demo mode without API key)

### 📊 **Historical Data Analysis**
Analyzes air pollution data from two monitoring stations:
- **New York City** - Queens College Station (PM2.5 data)
- **Bogota** - San Cristobal Station (PM2.5 and PM10 data)

**Data Period:** September 2016 - April 2017 (hourly measurements)

## ✨ Features

### 1. **🌏 Worldwide City Search** (NEW!)
- **Any city, anywhere** - Search and monitor air quality for any location worldwide
- **Comprehensive pollutant data** - PM2.5, PM10, NO₂, SO₂, CO, O₃, and NH₃
- **Real-time readings** - Get current air quality status
- **24-hour forecasts** - See predicted air quality trends
- **Interactive world map** - Visualize global air quality on an interactive map
- **Popular cities monitoring** - Track air quality in major cities worldwide
- **WHO compliance indicators** - Instant comparison with WHO air quality guidelines
- **Demo mode** - Works without API key using simulated realistic data
- **Production ready** - Set `OPENWEATHER_API_KEY` environment variable for real data

### 2. **🔴 Real-Time Air Quality Monitor**
- **Live monitoring** with auto-updating pollution readings every 5 seconds (NYC & Bogota)
- **Current PM2.5 and PM10 levels** for both cities
- **AQI category badges** with color-coded air quality levels
- **WHO compliance indicators** showing real-time compliance status
- **Live trends chart** displaying last 10 updates
- **Active alerts system** warning when pollution exceeds WHO thresholds
- Server-Sent Events (SSE) for efficient real-time data streaming

### 3. **Interactive Dashboard**
- Modern, responsive web interface
- Real-time data visualization using Plotly.js
- Multiple analysis views with tabbed navigation

### 4. **Comprehensive Analysis**
- **Time Series Analysis**: Hourly and daily pollution trends
- **Pattern Recognition**: Hourly and monthly pollution patterns
- **City Comparison**: Direct comparison between NYC and Bogota
- **WHO Compliance**: Check against World Health Organization air quality guidelines

### 5. **Key Insights**
- Statistical summaries (mean, median, std dev, min/max)
- Correlation analysis between cities
- Seasonal pattern detection
- Exceedance detection for WHO limits

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- (Optional) OpenWeatherMap API key for real-time worldwide data

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd air_pollution_analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set up OpenWeatherMap API key for real data:**
   ```bash
   # Get a free API key from https://openweathermap.org/api
   export OPENWEATHER_API_KEY="your_api_key_here"
   ```
   
   **Note:** The application works without an API key in **demo mode** using simulated but realistic data.

4. **Generate sample data (if needed):**
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

### 🌏 Worldwide Search Tab (NEW!)
- **City Search**: Enter any city name to get instant air quality data
- **Search Results**: Comprehensive pollutant readings with WHO compliance status
- **Popular Cities**: Grid view of air quality in major world cities
- **World Map**: Interactive globe showing real-time air quality markers
- **Forecast View**: 24-hour air quality predictions
- **Multi-pollutant Display**: PM2.5, PM10, NO₂, SO₂, CO, O₃, NH₃

### 🔴 Real-Time Monitor Tab
- **Live Air Quality Readings**: Current PM2.5 and PM10 levels updated every 5 seconds
- **AQI Categories**: Color-coded air quality indicators (Good, Moderate, Unhealthy, etc.)
- **WHO Compliance Status**: Real-time compliance with WHO guidelines
- **Active Alerts**: Warnings when pollution exceeds safe thresholds
- **Live Trends**: Visual chart showing pollution changes over the last 10 updates
- **Rush Hour Detection**: Simulates higher pollution during peak traffic hours

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
1. **Real-Time Monitoring**: Live air quality updates every 5 seconds with intelligent alerts
2. **Pollution Levels**: Analysis shows average pollution levels and variability in both cities
3. **Temporal Patterns**: Identifies when pollution is highest/lowest during the day and year
4. **Comparative Analysis**: Shows correlation and differences between the two cities
5. **Compliance**: Tracks WHO guideline compliance and exceedance events
6. **Rush Hour Effects**: Real-time simulation accounts for traffic patterns

## 🛠️ Technical Stack

- **Backend**: Flask (Python web framework)
- **Data Analysis**: pandas, numpy, scipy
- **Real-time API**: OpenWeatherMap Air Pollution API
- **Visualization**: Plotly.js
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Format**: Pipe-delimited text files (|) for historical data
- **HTTP Client**: requests library for API integration

## 📁 Project Structure

```
air_pollution_analysis/
├── app.py                      # Flask application with worldwide API
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   ├── StationData-NY_QueensCollege.txt
│   ├── StationData-Bogota_SanCristobal.txt
│   └── generate_sample_data.py
├── analysis/
│   ├── pollution_analyzer.py   # Historical data analysis module
│   └── realtime_api.py         # NEW: Real-time worldwide API integration
├── templates/
│   └── index.html              # Main dashboard with worldwide search
└── static/
    ├── css/
    │   └── style.css           # Dashboard styles with new components
    └── js/
        └── dashboard.js        # Dashboard interactions with search features
```

## 🔧 API Endpoints

### Worldwide Real-Time Endpoints (NEW!)
- `GET /api/worldwide/search/<city_name>` - Search for any city and get current air quality
  - Example: `/api/worldwide/search/London` or `/api/worldwide/search/London,GB`
- `GET /api/worldwide/coordinates?lat=<lat>&lon=<lon>` - Get air quality by coordinates
- `GET /api/worldwide/forecast/<city_name>` - Get 24-hour forecast for a city
- `GET /api/worldwide/popular-cities` - Get air quality for 15 major world cities
- `GET /api/worldwide/stream?cities=<city1>,<city2>` - SSE stream for multiple cities

### Real-Time Endpoints
- `GET /api/realtime/<city>` - Get current simulated pollution data for a city
- `GET /api/realtime/stream` - Server-Sent Events stream for live updates

### Statistical Endpoints
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

- **Worldwide Real-time Data**: [OpenWeatherMap Air Pollution API](https://openweathermap.org/api/air-pollution)
  - Free tier available (1000 calls/day)
  - Coverage: Worldwide
  - Update frequency: Every 10 minutes
- **NYC Historical Data**: New York State Department of Environmental Conservation
- **Bogota Historical Data**: Red de Monitoreo de Calidad del Aire de Bogotá (RMCAB) - Bogota Air Quality Monitoring Network

## 🌐 Demo Mode vs Production Mode

### Demo Mode (Default)
- Works immediately without any API key
- Uses realistic simulated data based on typical patterns
- Perfect for testing and development
- All features fully functional

### Production Mode
- Requires free OpenWeatherMap API key
- Real-time data from actual monitoring stations worldwide
- Set environment variable: `export OPENWEATHER_API_KEY="your_key"`
- Get API key: https://openweathermap.org/api

## 🤝 Contributing

This project was created as a data science assignment and enhanced with worldwide real-time capabilities. Feel free to fork and enhance it with:
- Additional visualizations
- More statistical analyses
- Machine learning predictions for air quality
- Additional cities/stations
- Historical data integration from other sources
- Mobile app integration
- Air quality health recommendations

## 📄 License

This project is created for educational and demonstration purposes.

## 👥 Authors

Created as a take-home assignment for World Health Organization data science positions.

## 🙏 Acknowledgments

- World Health Organization for air quality guidelines
- OpenWeatherMap for real-time air pollution API
- NYC Department of Environmental Conservation
- Bogota Air Quality Monitoring Network (RMCAB)
- Plotly for visualization library

---

**Note**: The application works in two modes:
1. **Demo Mode** (default): Uses simulated realistic data - perfect for testing and demonstrations
2. **Production Mode**: Requires OpenWeatherMap API key for real-time worldwide data

For demo purposes, no API key is needed. The sample historical data provided is generated for demonstration. For production use with real-time data, obtain a free API key from OpenWeatherMap.
