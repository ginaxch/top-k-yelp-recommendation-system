print("HELLO FROM QUERY")

from src.ranking import run_query
from results.plot_results import plot_scores
from results.save_results import save_results

if __name__ == "__main__":
    print("Running query...")

    results = run_query(
        data_path="data/yelp_academic_dataset_business.json",
        keywords=["chinese", "spicy"],
        k=5,
        min_rating=3.0,
        limit=5000
    )

    print("\n--- Top Results ---")
    print(results[["name", "stars", "review_count", "score"]])

    print("Number of results:", len(results))

    # Save results
    save_results(results)

    # Plot results
    plot_scores(results)