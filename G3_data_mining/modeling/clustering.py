import json
from sklearn.cluster import DBSCAN
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PARAMS_PATH = BASE_DIR / "artifacts" / "dbscan_params.json"
CLUSTERS_PATH = BASE_DIR / "artifacts" / "clusters.json"


def run_dbscan(X_pca):
    print("Exécution du clustering DBSCAN")

    eps = 0.5
    min_samples = 10

    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X_pca)

    params = {
        "eps": eps,
        "min_samples": min_samples
    }

    PARAMS_PATH.parent.mkdir(exist_ok=True)

    with open(PARAMS_PATH, "w") as f:
        json.dump(params, f, indent=2)


    unique, counts = np.unique(labels, return_counts=True)
    clusters = {str(int(k)): int(v) for k, v in zip(unique, counts)}


    with open(CLUSTERS_PATH, "w") as f:
        json.dump(clusters, f, indent=2)

    return labels, params
