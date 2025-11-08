import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data for NYC
np.random.seed(42)
start_date = datetime(2016, 9, 1)
end_date = datetime(2017, 4, 1)
date_range = pd.date_range(start=start_date, end=end_date, freq='H')

# NYC PM2.5 data (typically lower pollution)
nyc_pm25 = np.random.normal(10, 5, len(date_range))
# Add seasonal pattern (higher in winter)
seasonal = 5 * np.sin(np.linspace(0, 2*np.pi, len(date_range)))
nyc_pm25 = np.maximum(0, nyc_pm25 + seasonal)

nyc_data = pd.DataFrame({
    'Date': date_range.strftime('%Y-%m-%d'),
    'Time': date_range.strftime('%H:%M:%S'),
    'PM2.5': nyc_pm25.round(2)
})

# Save NYC data
nyc_data.to_csv('StationData-NY_QueensCollege.txt', sep='|', index=False)
print(f"NYC data generated: {len(nyc_data)} records")

# Generate sample data for Bogota
# Bogota PM2.5 and PM10 data (typically higher pollution)
bogota_pm25 = np.random.normal(25, 10, len(date_range))
bogota_pm10 = bogota_pm25 * 2.5 + np.random.normal(0, 5, len(date_range))
# Add seasonal pattern
bogota_pm25 = np.maximum(0, bogota_pm25 + seasonal * 2)
bogota_pm10 = np.maximum(0, bogota_pm10 + seasonal * 3)

bogota_data = pd.DataFrame({
    'Date': date_range.strftime('%Y-%m-%d'),
    'Time': date_range.strftime('%H:%M:%S'),
    'PM2.5': bogota_pm25.round(2),
    'PM10': bogota_pm10.round(2)
})

# Save Bogota data
bogota_data.to_csv('StationData-Bogota_SanCristobal.txt', sep='|', index=False)
print(f"Bogota data generated: {len(bogota_data)} records")
