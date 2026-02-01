"""
G4 — Entraînement du modèle Isolation Forest
Entraîne sur les données historiques "saines" et calcule le seuil (τ).
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Tuple
import logging

logger = logging.getLogger("G4")

# Paramètres du modèle
CONTAMINATION = 0.05       # On suppose ~5% d'anomalies dans les données
N_ESTIMATORS = 200         # Nombre d'arbres (plus = plus précis)
RANDOM_STATE = 42
THRESHOLD_PERCENTILE = 95  # Les 5% les plus bas = anomalies


def train_isolation_forest(X_train: np.ndarray) -> Tuple[IsolationForest, float]:
    """
    Entraîne un Isolation Forest sur les données historiques.

    Args:
        X_train: Données prétraitées (après scaler G3 + PCA G3)

    Returns:
        (model, threshold):
            - model: IsolationForest entraîné
            - threshold: seuil τ pour la classification
    """
    logger.info(f"Entraînement Isolation Forest sur {X_train.shape[0]} samples, {X_train.shape[1]} features")

    model = IsolationForest(
        contamination=CONTAMINATION,
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        max_samples="auto",
        n_jobs=-1,
    )
    model.fit(X_train)

    # Calculer les scores sur les données d'entraînement pour fixer le seuil
    scores_train = model.score_samples(X_train)

    # Le seuil τ : tout ce en dessous est considéré comme anomalie
    # percentile 5 = les 5% les plus bas des scores
    threshold = np.percentile(scores_train, 100 - THRESHOLD_PERCENTILE)

    logger.info(f"Modèle entraîné :")
    logger.info(f"  → Scores train : min={scores_train.min():.4f}, max={scores_train.max():.4f}, mean={scores_train.mean():.4f}")
    logger.info(f"  → Seuil τ = {threshold:.4f}")

    return model, threshold
