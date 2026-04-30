# Project Status Report
**Top-K Yelp Recommendation System**
Team: Gina + Chiebuka

---

## What We Have Built (Done)

### Core System — Gina

Gina built the entire foundation of the project from scratch. This includes:

- **Data loading**: reads the Yelp dataset (150k+ businesses in JSON format) and pulls out the four fields we care about — name, star rating, review count, and categories.
- **Preprocessing**: cleans the data by dropping rows with missing values, fixing data types, and lowercasing the categories text so keyword matching works consistently.
- **Baseline ranking model**: scores each business using a weighted formula that combines star rating (50% weight), review count (30%), and keyword match against categories (20%). Review count is normalized by capping at 1000 reviews. Keyword matching checks whether the user's query words appear in the business category string.
- **Query pipeline**: ties everything together — you call `run_query()` with a keyword list, minimum rating, and k, and it returns the top k businesses.
- **Output**: saves results to a CSV file and generates a horizontal bar chart showing the top-k scores.

The system runs end-to-end with a single command: `python -m src.query`

---

### Improved Ranking Model — Chiebuka

After studying the baseline, Chiebuka identified and fixed three concrete weaknesses:

**Problem 1 — Review count was poorly normalized.**
The baseline treats any business with more than 1,000 reviews the same (it caps the score at 1.0). So a restaurant with 1,001 reviews looks identical to one with 50,000. We fixed this by switching to a log-scale normalization, where scores are computed relative to the most-reviewed business in the dataset. This compresses the gap between extremely popular places and still rewards genuine popularity.

**Problem 2 — Keyword matching was too narrow.**
The baseline only checked whether query keywords appear in the categories field. If someone searches "chinese" and a restaurant is called "Han Dynasty" but lists "Szechuan" as its only category, it might not match. We extended matching to also check the business name, giving it half-credit compared to a category match.

**Problem 3 — Keyword relevance had too little influence.**
With keyword weight at 0.2, a non-Chinese restaurant with thousands of reviews could easily outscore an actual Chinese restaurant. We raised the keyword weight to 0.3 and adjusted the other weights proportionally. Experiments confirmed that 0.3 is past the threshold where relevant results consistently beat irrelevant ones.

The improved model lives in `src/improved_ranking.py` as the `ImprovedRanker` class.

---

### Experiments — Chiebuka

Three experiments were run comparing the baseline and improved rankers, all saved as plots in the `results/` folder.

**Experiment 1 — Multi-query comparison** (`exp1_multi_query.png`)
We ran both rankers on three different queries: "chinese + spicy", "pizza + italian", and "coffee + brunch". For each query, we checked how many of the top 5 results were actually relevant (i.e., the query keywords appear in the business's categories). The baseline scored 0.20, 0.40, and 1.00 across the three queries. The improved ranker scored 1.00 on all three. The most dramatic failure of the baseline: when searching "chinese + spicy", its top 3 results were Prep & Pastry, District Donuts, and Katie's Restaurant — none of which are Chinese restaurants. They ranked high purely because of high star ratings and review counts.

**Experiment 2 — Precision at different k values** (`exp2_precision_at_k.png`)
We measured precision not just at k=5 but also at k=1, 3, and 10. The improved ranker held a perfect score at every k and every query. The baseline degraded as k grew larger, because popular-but-irrelevant businesses kept getting pulled into lower ranks. This shows the baseline's problem is structural, not just a fluke at k=5.

**Experiment 3 — Weight sensitivity analysis** (`exp3_weight_sensitivity.png`)
We swept the keyword weight from 0.0 to 0.6 and measured how precision changed. The key finding: below a keyword weight of 0.25, irrelevant results dominate. At exactly 0.25, the system flips to returning only relevant results. We chose 0.30 to sit safely past that threshold. This experiment justifies our weight choice with data rather than just intuition.

---

### Report Sections Written — Chiebuka

A LaTeX draft of the full Method and Experimental Results sections is saved in `report_sections.tex`. It covers:
- Gina's pipeline description (data loading, preprocessing, filtering, output) written on her behalf
- The full mathematical description of both the baseline and improved scoring functions
- Justification for log normalization and expanded keyword matching
- All three experiments with tables and figure references
- A discussion section covering limitations and future work

---

## What Still Needs to Be Done

### For the Report

**1. Introduction / Problem Definition & Motivation (3% of grade) — team**
This section needs to answer: what is the Top-K retrieval problem, why does it matter for recommendation systems, and what specific gap does this project address (popularity bias in ranking). About 1–2 paragraphs. Either team member can write this.

**2. Related Work (2% of grade) — team**
We need to cite and briefly summarize at least 2–3 papers. Good candidates:
- A paper on Top-K query processing (classic database/IR work)
- A paper on learning-to-rank or scoring functions for recommendation
- The original Yelp dataset paper or a paper using it
For each paper: one sentence on what it does, one sentence on how it connects to our work.

**3. Conclusion — team**
A short paragraph summarizing what we built, what the experiments showed, and what we would do next if we had more time. The future work ideas from Chiebuka's draft (business-type filtering, word embeddings, learned weights) can go here.

**4. Individual contributions paragraph — both**
The rubric specifically requires this. One short paragraph per person stating clearly what they did. This affects individual grades.

**5. Assemble the full document**
All sections need to be combined into one PDF, checked for consistent notation, and trimmed to stay within 10 pages.

---

### For the Poster Presentation (10% of grade)

The poster should cover:
- Problem statement (1 panel) — what is Top-K retrieval and why does it matter
- System architecture diagram (1 panel) — the pipeline from data → ranking → output
- Scoring function comparison (1 panel) — baseline formula vs improved formula, side by side
- Results (1–2 panels) — the precision@k table and the weight sensitivity plot are the strongest visuals
- Conclusion + future work (1 panel)

Key things to be able to explain out loud:
- Why the baseline fails ("it's dominated by popularity — a restaurant with thousands of reviews will rank above an actual Chinese restaurant when you search for Chinese food")
- What log normalization does in plain English ("instead of treating 1,001 reviews and 50,000 reviews the same, we use a log scale so extremely popular places don't completely drown out everything else")
- What precision@k means ("out of the top 5 results, how many were actually relevant to the query")
- The weight sensitivity finding ("we didn't just pick 0.3 randomly — we ran an experiment showing that anything below 0.25 fails, and 0.3 puts us safely past that threshold")

---

## File Overview

```
src/
  load_data.py          — loads and trims the Yelp JSON dataset (Gina)
  preprocess.py         — cleans and filters the data (Gina)
  ranking.py            — baseline Ranker class + run_query (Gina)
  improved_ranking.py   — ImprovedRanker class + improved_run_query (Chiebuka)
  query.py              — entry point, runs baseline pipeline (Gina)

results/
  experiments.py        — all three comparison experiments (Chiebuka)
  save_results.py       — saves output to CSV (Gina)
  plot_results.py       — bar chart of top-k scores (Gina)
  exp1_multi_query.png  — multi-query bar charts (generated)
  exp2_precision_at_k.png — precision@k grouped bar chart (generated)
  exp3_weight_sensitivity.png — weight sweep line plots (generated)
  top_k_results.csv     — last run output

report_sections.tex     — LaTeX draft of full Method + Results sections (both)
```
