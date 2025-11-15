import pandas as pd
from haversine import haversine

from src.utils.time import robust_hour_of_iso_date


def driver_distance_to_pickup(df: pd.DataFrame) -> pd.DataFrame:
    df["driver_distance"] = df.apply(
        lambda r: haversine(
            (r["driver_latitude"], r["driver_longitude"]),
            (r["pickup_latitude"], r["pickup_longitude"]),
        ),
        axis=1,
    )
    return df


def hour_of_day(df: pd.DataFrame) -> pd.DataFrame:
    df["event_hour"] = df["event_timestamp"].apply(robust_hour_of_iso_date)
    return df


def driver_historical_completed_bookings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the number of historical completed bookings for each driver.
    
    This feature counts the number of completed bookings (is_completed=1) that each driver
    has had before the current event timestamp. This helps predict whether a driver is likely
    to accept a booking based on their historical track record.
    
    For test/inference data without is_completed, we set this to 0 (or could use training stats).
    """
    # Check if is_completed column exists (training data)
    if 'is_completed' in df.columns:
        # Sort by driver_id and timestamp to ensure chronological order
        df = df.sort_values(['driver_id', 'event_timestamp']).reset_index(drop=True)
        
        # For each row, count the number of completed bookings by this driver before this event
        # We use cumsum and shift to avoid including the current row in the count
        df['driver_historical_completed'] = (
            df.groupby('driver_id')['is_completed']
            .cumsum()
            .shift(fill_value=0)
        )
    else:
        # For test/inference data, we don't have is_completed
        # Set to 0 as a default (could be improved by using training data statistics)
        df['driver_historical_completed'] = 0
    
    return df
