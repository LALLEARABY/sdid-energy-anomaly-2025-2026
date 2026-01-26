import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "visualization" / "pca_clusters.png"

def plot_clusters(X_pca, labels):
    print("Génération du graphique des clusters PCA")

    plt.figure(figsize=(8, 6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, s=5)
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.title("Clustering PCA + DBSCAN")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300)
    plt.close()
