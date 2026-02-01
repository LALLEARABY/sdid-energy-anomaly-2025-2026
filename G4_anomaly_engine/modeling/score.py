"""
G4 — Scoring des données en temps réel
Applique le modèle Isolation Forest entraîné sur un batch de données.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Tuple, List
import logging

logger = logging.getLogger("G4")


def score_batch(
    model: IsolationForest,
    threshold: float,
    X: np.ndarray,
) -> Tuple[List[bool], List[float]]:
    """
    Score un batch de données et retourne les résultats.

    Logique :
        - score_samples() retourne un score par ligne
        - Si score < threshold (τ) → anomalie = True
        - Sinon → anomalie = False

    Args:
        model: IsolationForest entraîné
        threshold: seuil τ calculé pendant l'entraînement
        X: données prétraitées (numpy array)

    Returns:
        (is_anomaly_list, scores_list):
            - is_anomaly_list: [True/False, ...] pour chaque ligne
            - scores_list: [score, ...] pour chaque ligne
    """
    # Obtenir les scores d'anomalie
    scores = model.score_samples(X)

    # Classifier : score < τ → anomalie
    is_anomaly = (scores < threshold).tolist()
    scores_list = scores.tolist()

    n_anomalies = sum(is_anomaly)
    logger.info(f"score_batch → {len(X)} lignes scorées, {n_anomalies} anomalies détectées")
    logger.info(f"  → Scores : min={scores.min():.4f}, max={scores.max():.4f}, threshold={threshold:.4f}")

    return is_anomaly, scores_list
