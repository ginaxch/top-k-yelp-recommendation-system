

import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the dataset.
    """
    df = df.copy()

    # Drop rows with missing critical fields
    df = df.dropna(subset=["name", "stars", "review_count", "categories"])

    # Ensure correct types
    df["stars"] = pd.to_numeric(df["stars"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")

    # Drop rows that became NaN after conversion
    df = df.dropna(subset=["stars", "review_count"])

    # Normalize categories (lowercase + strip spaces)
    df["categories"] = df["categories"].str.lower().str.strip()

    return df


def filter_data(df: pd.DataFrame, min_rating: float = 0.0) -> pd.DataFrame:
    """
    Basic filtering (baseline method).
    """
    df = df.copy()

    # Filter by minimum rating
    df = df[df["stars"] >= min_rating]

    return df


def limit_data(df: pd.DataFrame, limit: int = 5000) -> pd.DataFrame:
    """
    Limit dataset size for faster experimentation.
    """
    return df.head(limit)