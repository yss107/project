"""
Flask Web Application for Air Pollution Analysis Dashboard
"""

from flask import Flask, render_template, jsonify
import json
import os
import sys

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
