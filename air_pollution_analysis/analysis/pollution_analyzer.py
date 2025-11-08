"""
Air Pollution Data Analysis Module
Analyzes PM2.5 and PM10 data from NYC and Bogota stations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import json

class PollutionAnalyzer:
    """Analyzes air pollution data from multiple stations"""
    
    # WHO Air Quality Guidelines (2021)
    WHO_PM25_ANNUAL = 5  # μg/m³
    WHO_PM25_24H = 15    # μg/m³
    WHO_PM10_ANNUAL = 15  # μg/m³
    WHO_PM10_24H = 45     # μg/m³
    
    def __init__(self, data_dir='data'):
        """Initialize analyzer with data directory"""
        self.data_dir = data_dir
        self.nyc_data = None
        self.bogota_data = None
        
    def load_data(self):
        """Load data from both stations"""
        # Load NYC data
        nyc_file = f"{self.data_dir}/StationData-NY_QueensCollege.txt"
        self.nyc_data = pd.read_csv(nyc_file, sep='|')
        self.nyc_data['DateTime'] = pd.to_datetime(
            self.nyc_data['Date'] + ' ' + self.nyc_data['Time']
        )
        self.nyc_data.set_index('DateTime', inplace=True)
        
        # Load Bogota data
        bogota_file = f"{self.data_dir}/StationData-Bogota_SanCristobal.txt"
        self.bogota_data = pd.read_csv(bogota_file, sep='|')
        self.bogota_data['DateTime'] = pd.to_datetime(
            self.bogota_data['Date'] + ' ' + self.bogota_data['Time']
        )
        self.bogota_data.set_index('DateTime', inplace=True)
        
        return True
    
    def get_basic_stats(self, city='NYC'):
        """Get basic statistics for a city"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        
        stats_dict = {
            'city': city,
            'pm25': {
                'mean': float(data['PM2.5'].mean()),
                'median': float(data['PM2.5'].median()),
                'std': float(data['PM2.5'].std()),
                'min': float(data['PM2.5'].min()),
                'max': float(data['PM2.5'].max()),
                'count': int(data['PM2.5'].count())
            }
        }
        
        if 'PM10' in data.columns:
            stats_dict['pm10'] = {
                'mean': float(data['PM10'].mean()),
                'median': float(data['PM10'].median()),
                'std': float(data['PM10'].std()),
                'min': float(data['PM10'].min()),
                'max': float(data['PM10'].max()),
                'count': int(data['PM10'].count())
            }
        
        return stats_dict
    
    def get_time_series_data(self, city='NYC', pollutant='PM2.5'):
        """Get time series data for visualization"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        
        time_series = []
        for idx, value in data[pollutant].items():
            time_series.append({
                'date': idx.strftime('%Y-%m-%d %H:%M:%S'),
                'value': float(value)
            })
        
        return time_series
    
    def get_daily_averages(self, city='NYC', pollutant='PM2.5'):
        """Calculate daily averages"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        daily_avg = data[pollutant].resample('D').mean()
        
        result = []
        for idx, value in daily_avg.items():
            result.append({
                'date': idx.strftime('%Y-%m-%d'),
                'value': float(value)
            })
        
        return result
    
    def get_hourly_pattern(self, city='NYC', pollutant='PM2.5'):
        """Get average pollution by hour of day"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        hourly = data.groupby(data.index.hour)[pollutant].mean()
        
        result = []
        for hour, value in hourly.items():
            result.append({
                'hour': int(hour),
                'value': float(value)
            })
        
        return result
    
    def get_monthly_pattern(self, city='NYC', pollutant='PM2.5'):
        """Get average pollution by month"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        monthly = data.groupby(data.index.month)[pollutant].mean()
        
        result = []
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month, value in monthly.items():
            result.append({
                'month': month_names[int(month)-1],
                'value': float(value)
            })
        
        return result
    
    def compare_cities(self):
        """Compare pollution between NYC and Bogota"""
        # Align data by timestamp
        merged = pd.merge(
            self.nyc_data[['PM2.5']],
            self.bogota_data[['PM2.5']],
            left_index=True,
            right_index=True,
            suffixes=('_nyc', '_bogota')
        )
        
        # Calculate correlation
        correlation = merged['PM2.5_nyc'].corr(merged['PM2.5_bogota'])
        
        # Find when NYC > Bogota
        nyc_higher = merged[merged['PM2.5_nyc'] > merged['PM2.5_bogota']]
        
        comparison = []
        for idx, row in merged.iterrows():
            comparison.append({
                'date': idx.strftime('%Y-%m-%d %H:%M:%S'),
                'nyc': float(row['PM2.5_nyc']),
                'bogota': float(row['PM2.5_bogota']),
                'nyc_higher': bool(row['PM2.5_nyc'] > row['PM2.5_bogota'])
            })
        
        return {
            'correlation': float(correlation),
            'nyc_higher_count': int(len(nyc_higher)),
            'total_count': int(len(merged)),
            'nyc_higher_percent': float(len(nyc_higher) / len(merged) * 100),
            'comparison_data': comparison
        }
    
    def check_who_limits(self, city='NYC'):
        """Check compliance with WHO limits"""
        data = self.nyc_data if city == 'NYC' else self.bogota_data
        
        # Annual mean
        pm25_annual = data['PM2.5'].mean()
        
        # 24-hour means
        pm25_daily = data['PM2.5'].resample('D').mean()
        exceedances_24h = pm25_daily[pm25_daily > self.WHO_PM25_24H]
        
        exceedance_periods = []
        for idx, value in exceedances_24h.items():
            exceedance_periods.append({
                'date': idx.strftime('%Y-%m-%d'),
                'value': float(value),
                'limit': self.WHO_PM25_24H,
                'exceeded_by': float(value - self.WHO_PM25_24H)
            })
        
        result = {
            'city': city,
            'pm25_annual_mean': float(pm25_annual),
            'who_annual_limit': self.WHO_PM25_ANNUAL,
            'annual_compliant': bool(pm25_annual <= self.WHO_PM25_ANNUAL),
            'who_24h_limit': self.WHO_PM25_24H,
            'exceedances_24h': exceedance_periods,
            'exceedance_count': int(len(exceedances_24h)),
            'total_days': int(len(pm25_daily)),
            'exceedance_percent': float(len(exceedances_24h) / len(pm25_daily) * 100)
        }
        
        if 'PM10' in data.columns:
            pm10_annual = data['PM10'].mean()
            pm10_daily = data['PM10'].resample('D').mean()
            exceedances_pm10 = pm10_daily[pm10_daily > self.WHO_PM10_24H]
            
            result['pm10_annual_mean'] = float(pm10_annual)
            result['who_pm10_annual_limit'] = self.WHO_PM10_ANNUAL
            result['pm10_annual_compliant'] = bool(pm10_annual <= self.WHO_PM10_ANNUAL)
            result['who_pm10_24h_limit'] = self.WHO_PM10_24H
            result['pm10_exceedance_count'] = int(len(exceedances_pm10))
        
        return result
    
    def get_summary(self):
        """Get comprehensive summary of all analyses"""
        return {
            'nyc_stats': self.get_basic_stats('NYC'),
            'bogota_stats': self.get_basic_stats('Bogota'),
            'nyc_who_limits': self.check_who_limits('NYC'),
            'bogota_who_limits': self.check_who_limits('Bogota'),
            'comparison': self.compare_cities()
        }
