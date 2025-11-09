"""
Flask Web Application for Air Pollution Analysis Dashboard
"""

from flask import Flask, render_template, jsonify, Response
import json
import os
import sys
import time
from datetime import datetime
import random

# Add analysis module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis'))

from pollution_analyzer import PollutionAnalyzer

app = Flask(__name__)

# Initialize analyzer
analyzer = PollutionAnalyzer(data_dir=os.path.join(os.path.dirname(__file__), 'data'))

# Load data on startup
try:
    analyzer.load_data()
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats/<city>')
def get_stats(city):
    """Get basic statistics for a city"""
    try:
        stats = analyzer.get_basic_stats(city)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeseries/<city>/<pollutant>')
def get_timeseries(city, pollutant):
    """Get time series data"""
    try:
        data = analyzer.get_time_series_data(city, pollutant)
        # Return sampled data for performance (every 6th point)
        sampled_data = data[::6]
        return jsonify(sampled_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily/<city>/<pollutant>')
def get_daily(city, pollutant):
    """Get daily averages"""
    try:
        data = analyzer.get_daily_averages(city, pollutant)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hourly/<city>/<pollutant>')
def get_hourly(city, pollutant):
    """Get hourly pattern"""
    try:
        data = analyzer.get_hourly_pattern(city, pollutant)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly/<city>/<pollutant>')
def get_monthly(city, pollutant):
    """Get monthly pattern"""
    try:
        data = analyzer.get_monthly_pattern(city, pollutant)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare')
def compare():
    """Compare cities"""
    try:
        data = analyzer.compare_cities()
        # Return sampled comparison data
        sampled_comparison = data['comparison_data'][::6]
        data['comparison_data'] = sampled_comparison
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/who-limits/<city>')
def who_limits(city):
    """Check WHO limits"""
    try:
        data = analyzer.check_who_limits(city)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary')
def summary():
    """Get comprehensive summary"""
    try:
        data = analyzer.get_summary()
        # Simplify comparison data for summary
        if 'comparison' in data:
            data['comparison']['comparison_data'] = data['comparison']['comparison_data'][::20]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/<city>')
def get_realtime(city):
    """Get simulated real-time pollution data"""
    try:
        # Get historical stats to base simulation on
        stats = analyzer.get_basic_stats(city)
        
        # Simulate real-time data with some variation
        pm25_mean = stats['pm25']['mean']
        pm25_std = stats['pm25']['std']
        
        # Add time-based variation (higher during rush hours)
        hour = datetime.now().hour
        rush_hour_factor = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            rush_hour_factor = 1.3
        
        # Generate simulated current reading
        current_pm25 = max(0, random.gauss(pm25_mean * rush_hour_factor, pm25_std * 0.5))
        
        # Calculate AQI category
        aqi_category = get_aqi_category(current_pm25)
        
        result = {
            'city': city,
            'timestamp': datetime.now().isoformat(),
            'pm25': round(current_pm25, 2),
            'aqi_category': aqi_category,
            'who_compliant': current_pm25 <= analyzer.WHO_PM25_ANNUAL,
            'trend': random.choice(['rising', 'falling', 'stable'])
        }
        
        # Add PM10 for Bogota
        if city == 'Bogota' and 'pm10' in stats:
            pm10_mean = stats['pm10']['mean']
            pm10_std = stats['pm10']['std']
            current_pm10 = max(0, random.gauss(pm10_mean * rush_hour_factor, pm10_std * 0.5))
            result['pm10'] = round(current_pm10, 2)
            result['pm10_who_compliant'] = current_pm10 <= analyzer.WHO_PM10_ANNUAL
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime/stream')
def stream_realtime():
    """Server-Sent Events stream for real-time updates"""
    def generate():
        while True:
            try:
                # Get data for both cities
                nyc_data = get_simulated_data('NYC')
                bogota_data = get_simulated_data('Bogota')
                
                data = {
                    'nyc': nyc_data,
                    'bogota': bogota_data,
                    'timestamp': datetime.now().isoformat()
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(5)  # Update every 5 seconds
            except GeneratorExit:
                break
            except Exception as e:
                print(f"Stream error: {e}")
                break
    
    return Response(generate(), mimetype='text/event-stream')

def get_simulated_data(city):
    """Helper function to get simulated real-time data"""
    stats = analyzer.get_basic_stats(city)
    pm25_mean = stats['pm25']['mean']
    pm25_std = stats['pm25']['std']
    
    hour = datetime.now().hour
    rush_hour_factor = 1.0
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        rush_hour_factor = 1.3
    
    current_pm25 = max(0, random.gauss(pm25_mean * rush_hour_factor, pm25_std * 0.5))
    
    data = {
        'city': city,
        'pm25': round(current_pm25, 2),
        'aqi_category': get_aqi_category(current_pm25),
        'who_compliant': current_pm25 <= analyzer.WHO_PM25_ANNUAL,
        'alert': current_pm25 > analyzer.WHO_PM25_24H
    }
    
    if city == 'Bogota' and 'pm10' in stats:
        pm10_mean = stats['pm10']['mean']
        pm10_std = stats['pm10']['std']
        current_pm10 = max(0, random.gauss(pm10_mean * rush_hour_factor, pm10_std * 0.5))
        data['pm10'] = round(current_pm10, 2)
        data['pm10_alert'] = current_pm10 > analyzer.WHO_PM10_24H
    
    return data

def get_aqi_category(pm25):
    """Get AQI category based on PM2.5 value"""
    if pm25 <= 12:
        return {'level': 'Good', 'color': '#00e400'}
    elif pm25 <= 35.4:
        return {'level': 'Moderate', 'color': '#ffff00'}
    elif pm25 <= 55.4:
        return {'level': 'Unhealthy for Sensitive Groups', 'color': '#ff7e00'}
    elif pm25 <= 150.4:
        return {'level': 'Unhealthy', 'color': '#ff0000'}
    elif pm25 <= 250.4:
        return {'level': 'Very Unhealthy', 'color': '#8f3f97'}
    else:
        return {'level': 'Hazardous', 'color': '#7e0023'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
