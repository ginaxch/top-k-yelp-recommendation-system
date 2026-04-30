"""
Experiments comparing Baseline Ranker vs. ImprovedRanker across:
  1. Multi-query comparison (3 queries)
  2. Precision@K evaluation
  3. Keyword weight sensitivity analysis
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.load_data import load_business_data
from src.preprocess import clean_data, filter_data
from src.ranking import Ranker
from src.improved_ranking import ImprovedRanker

DATA_PATH = "data/yelp_academic_dataset_business.json"
OUT_DIR = "results"
LIMIT = 5000
MIN_RATING = 3.0
K = 5

QUERIES = [
    ["chinese", "spicy"],
    ["pizza", "italian"],
    ["coffee", "brunch"],
]


def load_df():
    df = load_business_data(DATA_PATH, limit=LIMIT)
    df = clean_data(df)
    df = filter_data(df, min_rating=MIN_RATING)
    return df


def precision_at_k(results: pd.DataFrame, keywords: list, k: int) -> float:
    """
    Fraction of top-k results where at least one keyword appears in categories.
    Treats categories field as ground-truth relevance signal.
    """
    relevant = 0
    for _, row in results.head(k).iterrows():
        cats = str(row.get("categories") or "").lower()
        if any(kw.lower() in cats for kw in keywords):
            relevant += 1
    return relevant / k


# ── Experiment 1: Multi-query comparison ─────────────────────────────────────

def experiment_multi_query(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Multi-Query Comparison (Baseline vs Improved)")
    print("=" * 60)

    baseline_ranker = Ranker()
    improved_ranker = ImprovedRanker()

    fig, axes = plt.subplots(len(QUERIES), 2, figsize=(14, 4 * len(QUERIES)))
    fig.suptitle("Baseline vs. Improved Ranker — Top-K Results by Query", fontsize=13)

    for i, keywords in enumerate(QUERIES):
        label = " + ".join(keywords)

        b_results = baseline_ranker.rank(df, keywords=keywords, k=K)
        max_reviews = df["review_count"].max()
        i_results = improved_ranker.rank(df, keywords=keywords, k=K)

        b_prec = precision_at_k(b_results, keywords, K)
        i_prec = precision_at_k(i_results, keywords, K)

        print(f"\nQuery: {label}")
        print(f"  Baseline  Precision@{K}: {b_prec:.2f}")
        print(f"  Improved  Precision@{K}: {i_prec:.2f}")
        print(f"\n  {'Baseline':^40} | {'Improved':^40}")
        print(f"  {'-'*40}-+-{'-'*40}")
        for (_, br), (_, ir) in zip(b_results.iterrows(), i_results.iterrows()):
            b_name = br["name"][:38]
            i_name = ir["name"][:38]
            print(f"  {b_name:<40} | {i_name:<40}")

        # Baseline plot
        ax_b = axes[i][0]
        ax_b.barh(b_results["name"].str[:30][::-1], b_results["score"][::-1], color="#5b8db8")
        ax_b.set_title(f'Baseline — "{label}" (P@{K}={b_prec:.2f})', fontsize=10)
        ax_b.set_xlabel("Score")

        # Improved plot
        ax_i = axes[i][1]
        ax_i.barh(i_results["name"].str[:30][::-1], i_results["score"][::-1], color="#e07b54")
        ax_i.set_title(f'Improved — "{label}" (P@{K}={i_prec:.2f})', fontsize=10)
        ax_i.set_xlabel("Score")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "exp1_multi_query.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n[saved] {path}")


# ── Experiment 2: Precision@K summary table ───────────────────────────────────

def experiment_precision(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Precision@K (k=1,3,5,10)")
    print("=" * 60)

    ks = [1, 3, 5, 10]
    baseline_ranker = Ranker()
    improved_ranker = ImprovedRanker()

    rows = []
    for keywords in QUERIES:
        label = " + ".join(keywords)
        b_results = baseline_ranker.rank(df, keywords=keywords, k=max(ks))
        i_results = improved_ranker.rank(df, keywords=keywords, k=max(ks))
        for k in ks:
            rows.append({
                "query": label,
                "k": k,
                "baseline_precision": precision_at_k(b_results, keywords, k),
                "improved_precision": precision_at_k(i_results, keywords, k),
            })

    table = pd.DataFrame(rows)
    print(table.to_string(index=False))

    # Plot: grouped bar per query at k=5
    k5 = table[table["k"] == 5]
    x = range(len(k5))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([xi - width/2 for xi in x], k5["baseline_precision"], width, label="Baseline", color="#5b8db8")
    ax.bar([xi + width/2 for xi in x], k5["improved_precision"], width, label="Improved", color="#e07b54")
    ax.set_xticks(list(x))
    ax.set_xticklabels(k5["query"], rotation=10, ha="right")
    ax.set_ylabel("Precision@5")
    ax.set_ylim(0, 1.1)
    ax.set_title("Precision@5: Baseline vs. Improved by Query")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "exp2_precision_at_k.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n[saved] {path}")

    return table


# ── Experiment 3: Keyword weight sensitivity ──────────────────────────────────

def experiment_weight_sensitivity(df: pd.DataFrame):
    """
    Fix w_rating + w_reviews proportionally and sweep w_keyword from 0 → 0.6.
    Track Precision@5 and mean score of relevant vs. irrelevant results.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Keyword Weight Sensitivity (w_keyword sweep)")
    print("=" * 60)

    keywords = ["chinese", "spicy"]
    w_kw_values = np.arange(0.0, 0.65, 0.05)

    precisions = []
    mean_rel_scores = []
    mean_irrel_scores = []

    for w_kw in w_kw_values:
        remaining = 1.0 - w_kw
        # Keep original ratio of rating:reviews = 5:3
        w_rat = remaining * (5 / 8)
        w_rev = remaining * (3 / 8)

        ranker = ImprovedRanker(w_rating=w_rat, w_reviews=w_rev, w_keyword=w_kw)
        results = ranker.rank(df, keywords=keywords, k=K)

        prec = precision_at_k(results, keywords, K)
        precisions.append(prec)

        # Score gap: relevant vs irrelevant in top-k
        rel_scores = []
        irrel_scores = []
        max_reviews = df["review_count"].max()
        for _, row in results.iterrows():
            s = ranker.compute_score(row, keywords, max_reviews)
            cats = str(row.get("categories") or "").lower()
            if any(kw.lower() in cats for kw in keywords):
                rel_scores.append(s)
            else:
                irrel_scores.append(s)
        mean_rel_scores.append(np.mean(rel_scores) if rel_scores else 0)
        mean_irrel_scores.append(np.mean(irrel_scores) if irrel_scores else 0)

        print(f"  w_keyword={w_kw:.2f}  P@5={prec:.2f}  "
              f"mean_relevant={mean_rel_scores[-1]:.4f}  "
              f"mean_irrelevant={mean_irrel_scores[-1]:.4f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Keyword Weight Sensitivity (query: "chinese + spicy")', fontsize=12)

    ax1.plot(w_kw_values, precisions, marker="o", color="#e07b54")
    ax1.axvline(x=0.3, color="gray", linestyle="--", label="chosen w_keyword=0.3")
    ax1.set_xlabel("w_keyword")
    ax1.set_ylabel("Precision@5")
    ax1.set_ylim(-0.05, 1.1)
    ax1.set_title("Precision@5 vs. Keyword Weight")
    ax1.legend()

    ax2.plot(w_kw_values, mean_rel_scores, marker="o", label="Relevant", color="#4caf50")
    ax2.plot(w_kw_values, mean_irrel_scores, marker="s", label="Irrelevant", color="#f44336")
    ax2.axvline(x=0.3, color="gray", linestyle="--", label="chosen w_keyword=0.3")
    ax2.set_xlabel("w_keyword")
    ax2.set_ylabel("Mean Score in Top-K")
    ax2.set_title("Score Gap: Relevant vs. Irrelevant")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "exp3_weight_sensitivity.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n[saved] {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading data...")
    df = load_df()
    print(f"Dataset size after preprocessing: {len(df)} businesses")

    experiment_multi_query(df)
    experiment_precision(df)
    experiment_weight_sensitivity(df)

    print("\nAll experiments complete. Plots saved to results/")
