import pandas as pd

def load_business_data(path: str, limit: int = 5000) -> pd.DataFrame:
    """
    Load Yelp business dataset (JSON lines format)
    """
    df = pd.read_json(path, lines=True)

    # Keep only required columns
    df = df[["name", "stars", "review_count", "categories"]]

    return df.head(limit)
