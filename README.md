# top-k-yelp-recommendation-system
This project implements a query-driven Top-K recommendation system using the Yelp dataset. It combines structured data (e.g., ratings, review counts) with unstructured signals (e.g., keyword matching from categories) to rank and return the most relevant businesses for a given user query.

The system simulates how real-world search and recommendation engines work by processing user-defined constraints and producing ranked results based on a custom scoring function.
## Key Features
- Top-K Query Processing
  Retrieve the top k businesses that best match user input.
- Ranking-Based Recommendation
  - Custom scoring function combining multiple signals:
    - Star ratings
    - Review counts
    - Keyword relevance
- Structured + Unstructured Data Integration
  - Leverages both numerical attributes and text-based matching.
- Baseline vs Proposed Method Comparison
  - Enables evaluation of ranking improvements over simple baselines (e.g., rating-only).
- End-to-End Pipeline
  - From raw data → preprocessing → ranking → results → visualization.

## System Architecture
```
Data (Yelp JSON)
        ↓
Data Loading
        ↓
Preprocessing (cleaning, filtering)
        ↓
Ranking Algorithm (scoring function)
        ↓
Top-K Selection
        ↓
Output (CSV + Visualization)
```
## Project Structure
```top-k-yelp-recommendation-system/
│
├── src/
│   ├── query.py          # Entry point for running queries
│   ├── ranking.py        # Ranking algorithm
│   ├── load_data.py      # Data loading logic
│   └── preprocess.py     # Data cleaning & filtering
│
├── results/
│   ├── plot_results.py   # Visualization (bar chart)
│   └── save_results.py   # Save results to CSV
│
├── data/
│   └── yelp_academic_dataset_business.json
│
└── README.md
```
## How it works

### 1. Query Input

- Users define:
  - Keywords (e.g., "chinese", "spicy")
  - Minimum rating
  - Number of results (k)
### 2. Data Processing
- Load dataset (JSON lines format)
- Clean missing values
- Normalize data types
- Filter based on constraints
### 3. Ranking Function
Each business is scored using:
```
score = w_rating * rating_score
      + w_reviews * review_score
      + w_keyword * keyword_score
```
Where:
- rating_score = normalized star rating
- review_score = normalized review count
- keyword_score = keyword match relevance

### 4. Output
- Top-k ranked businesses
- Saved to CSV (results/top_k_results.csv)
- Visualization via horizontal bar chart

## How to Run
From project Root:
```
python -m src.query
```
Example output:
```
--- Top Results ---
name                          stars   reviews   score
-----------------------------------------------------
Prep & Pastry                 4.5     2126      0.75
District Donuts Sliders Brew  4.5     2062      0.75
...
```

## Team Responsibilities
### Core System (Gina)
- Data pipeline
- Ranking algorithm
- Query execution
- Output + visualization
### Improvements (Chiebuka)
- Improve ranking model
- Run experiments & comparisons
- Generate analysis & plots
- Contribute to final report

## Goal
To design and evaluate an effective Top-K query and ranking system that demonstrates how structured and unstructured data can be combined for real-world recommendation tasks.
