import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

def plot_scores(df):
    """
    Plot top-k restaurant scores
    """
    plt.figure()

    names = df["name"]
    scores = df["score"]

    plt.barh(names, scores)
    plt.xlabel("Score")
    plt.ylabel("Restaurant")
    plt.title("Top-K Restaurant Ranking")

    plt.gca().invert_yaxis()
    plt.tight_layout()

    plt.savefig("results/top_k_plot.png")
    plt.show()