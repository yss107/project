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


def driver_acceptance_rate(df: pd.DataFrame) -> pd.DataFrame:
    
    if 'is_completed' in df.columns:
        df = df.sort_values(['driver_id', 'event_timestamp']).reset_index(drop=True)
        
        # Calculate cumulative sum of acceptances
        cumsum_accepted = df.groupby('driver_id')['is_completed'].cumsum().shift(fill_value=0)
        
        # Calculate cumulative count of bookings
        cumsum_total = df.groupby('driver_id').cumcount()
        
        # Calculate acceptance rate (avoid division by zero)
        df['driver_acceptance_rate'] = cumsum_accepted / (cumsum_total + 1)
    else:
        df['driver_acceptance_rate'] = 0.5  # Default to neutral rate for test data
    
    return df


def time_based_features(df: pd.DataFrame) -> pd.DataFrame:
   
    # Ensure we have event_hour
    if 'event_hour' not in df.columns:
        df = hour_of_day(df)
    
    # Morning rush hour: 7-9 AM
    # Evening rush hour: 5-8 PM
    df['is_rush_hour'] = ((df['event_hour'] >= 7) & (df['event_hour'] <= 9) | 
                           (df['event_hour'] >= 17) & (df['event_hour'] <= 20)).astype(int)
    
    return df


def distance_interaction_features(df: pd.DataFrame) -> pd.DataFrame:

    # Ensure we have the distance features
    if 'driver_distance' in df.columns and 'trip_distance' in df.columns:
        # Interaction: product of trip and driver distance
        df['distance_interaction'] = df['trip_distance'] * df['driver_distance']
        
        # Ratio: trip distance to driver distance (how far the trip is compared to pickup distance)
        # Add small epsilon to avoid division by zero
        df['trip_to_driver_ratio'] = df['trip_distance'] / (df['driver_distance'] + 0.01)
    
    return df
