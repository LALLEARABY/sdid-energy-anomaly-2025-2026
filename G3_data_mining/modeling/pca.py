import joblib
from sklearn.decomposition import PCA
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = BASE_DIR / "artifacts" / "pca.pkl"

def apply_pca(X_scaled):
    print("Application de l'analyse en composantes principales (ACP)")

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(pca, ARTIFACT_PATH)

    return X_pca, pca
