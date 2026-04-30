import pandas as pd
import numpy as np
from typing import List

from src.load_data import load_business_data
from src.preprocess import clean_data, filter_data


class ImprovedRanker:
    def __init__(self, w_rating=0.4, w_reviews=0.3, w_keyword=0.3):
        """
        Weights sum to 1.0. Keyword weight raised vs. baseline (0.2 → 0.3)
        to make query relevance more competitive with popularity signals.
        """
        self.w_rating = w_rating
        self.w_reviews = w_reviews
        self.w_keyword = w_keyword

    def keyword_match_score(self, row: pd.Series, keywords: List[str]) -> float:
        """
        Improved over baseline:
        - Checks both `categories` (full credit) and `name` (half credit)
        - Returns proportion of keywords matched, so score stays in [0, 1]
        """
        if not keywords:
            return 0.0

        categories = str(row.get("categories") or "").lower()
        name = str(row.get("name") or "").lower()

        score = 0.0
        for kw in keywords:
            kw = kw.lower()
            if kw in categories:
                score += 1.0
            elif kw in name:
                score += 0.5

        return score / len(keywords)

    def compute_score(
        self, row: pd.Series, keywords: List[str], max_reviews: float
    ) -> float:
        """
        score = w_rating * (stars / 5)
              + w_reviews * log(1 + review_count) / log(1 + max_review_count)
              + w_keyword * keyword_match_score

        Log normalization for reviews prevents a business with 10k reviews
        from completely dominating one with 1k reviews (baseline capped at 1000).
        """
        rating_score = row.get("stars", 0) / 5.0

        review_count = row.get("review_count", 0)
        review_score = (
            np.log1p(review_count) / np.log1p(max_reviews)
            if max_reviews > 0
            else 0.0
        )

        keyword_score = self.keyword_match_score(row, keywords)

        return (
            self.w_rating * rating_score
            + self.w_reviews * review_score
            + self.w_keyword * keyword_score
        )

    def rank(self, df: pd.DataFrame, keywords: List[str], k: int = 5) -> pd.DataFrame:
        """
        Rank businesses and return top-k.
        Tie-breaking: higher review_count wins (more reliable popularity signal).
        """
        df = df.copy()
        max_reviews = df["review_count"].max()

        df["score"] = df.apply(
            lambda row: self.compute_score(row, keywords, max_reviews), axis=1
        )

        return df.sort_values(
            by=["score", "review_count"], ascending=[False, False]
        ).head(k)


def improved_run_query(
    data_path: str,
    keywords: List[str],
    k: int = 5,
    min_rating: float = 0.0,
    limit: int = 5000,
) -> pd.DataFrame:
    df = load_business_data(data_path, limit=limit)
    df = clean_data(df)
    df = filter_data(df, min_rating=min_rating)

    ranker = ImprovedRanker()
    return ranker.rank(df, keywords=keywords, k=k)
