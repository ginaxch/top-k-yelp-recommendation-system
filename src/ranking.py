from src.load_data import load_business_data
from src.preprocess import clean_data, filter_data

def run_query(
    data_path: str,
    keywords: list,
    k: int = 5,
    min_rating: float = 0.0,
    limit: int = 5000
):
    """
    Full pipeline:
    1. Load data
    2. Preprocess
    3. Filter (baseline)
    4. Rank (our method)
    """

    # Step 1: Load
    df = load_business_data(data_path, limit=limit)

    # Step 2: Clean
    df = clean_data(df)

    # Step 3: Filter (baseline)
    df = filter_data(df, min_rating=min_rating)

    # Step 4: Rank
    ranker = Ranker()
    results = ranker.rank(df, keywords=keywords, k=k)

    return results


if __name__ == "__main__":
    results = run_query(
        data_path="../data/yelp_academic_dataset_business.json",
        keywords=["chinese", "spicy"],
        k=5,
        min_rating=4.0,
        limit=5000
    )

    print("\nTop Results:\n")
    print(results[["name", "stars", "review_count", "score"]])

import pandas as pd
from typing import List, Dict

class Ranker:
    def __init__(self, w_rating=0.5, w_reviews=0.3, w_keyword=0.2):
        """
        Initialize weights for ranking function.
        """
        self.w_rating = w_rating
        self.w_reviews = w_reviews
        self.w_keyword = w_keyword

    def keyword_match_score(self, categories: str, keywords: List[str]) -> float:
        """
        Simple keyword match: counts how many keywords appear in categories.
        """
        if pd.isna(categories):
            return 0.0
        
        categories = categories.lower()
        score = sum(1 for kw in keywords if kw.lower() in categories)
        return score / len(keywords) if keywords else 0.0

    def compute_score(self, row: pd.Series, keywords: List[str]) -> float:
        """
        Compute ranking score for one business.
        """
        rating_score = row.get("stars", 0) / 5.0
        review_score = min(row.get("review_count", 0) / 1000.0, 1.0)
        keyword_score = self.keyword_match_score(row.get("categories", ""), keywords)

        score = (
            self.w_rating * rating_score +
            self.w_reviews * review_score +
            self.w_keyword * keyword_score
        )
        return score

    def rank(self, df: pd.DataFrame, keywords: List[str], k: int = 5) -> pd.DataFrame:
        """
        Rank businesses and return top-k.
        """
        df = df.copy()

        df["score"] = df.apply(lambda row: self.compute_score(row, keywords), axis=1)
        df_sorted = df.sort_values(by="score", ascending=False)

        return df_sorted.head(k)