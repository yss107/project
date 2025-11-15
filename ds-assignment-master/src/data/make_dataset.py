import pandas as pd

from src.utils.config import load_config
from src.utils.store import AssignmentStore


def main():
    store = AssignmentStore()
    config = load_config()

    booking_df = store.get_raw("booking_log.csv")
    booking_df = clean_booking_df(booking_df)

    participant_df = store.get_raw("participant_log.csv")
    participant_df = clean_participant_df(participant_df)

    dataset = merge_dataset(booking_df, participant_df)
    dataset = create_target(dataset, config["target"])

    store.put_processed("dataset.csv", dataset)


def clean_booking_df(df: pd.DataFrame) -> pd.DataFrame:
    unique_columns = [
        "order_id",
        "trip_distance",
        "pickup_latitude",
        "pickup_longitude",
    ]
    df = df.drop_duplicates(subset=unique_columns)
    return df[unique_columns]


def clean_participant_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean participant data by removing duplicates and keeping only the final outcome.
    
    For each driver-order pair, we want only the final status (ACCEPTED/IGNORED/REJECTED),
    not the intermediate CREATED status. This prevents having duplicate rows for the same
    allocation decision.
    """
    df = df.drop_duplicates()
    
    # Remove CREATED events if there's a subsequent outcome event for the same driver-order pair
    # Keep only rows where participant_status is not CREATED, OR where it's CREATED but
    # there's no other status for that driver-order pair
    df = df.sort_values(['driver_id', 'order_id', 'event_timestamp'])
    
    # For each driver-order pair, keep the last event (final outcome)
    df = df.groupby(['driver_id', 'order_id'], as_index=False).last()
    
    return df


def merge_dataset(bookings: pd.DataFrame, participants: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(participants, bookings, on="order_id", how="left")

    return df


def create_target(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    df[target_col] = df["participant_status"].apply(lambda x: int(x == "ACCEPTED"))
    return df


if __name__ == "__main__":
    main()
