import os
import pandas as pd

def save_results(df: pd.DataFrame, filename: str = "results/top_k_results.csv"):
    """
    Save results to CSV for analysis/report
    """
    os.makedirs("results", exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")