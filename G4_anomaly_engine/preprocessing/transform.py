"""
G4 — Prétraitement des données
Charge les paramètres (scaler + PCA) produits par G3 et les applique
pour garantir la cohérence avec leur pipeline.

G3 pipeline : fetch → scale_data(scaler) → apply_pca(pca) → dbscan
G4 pipeline : fetch → [même scaler] → [même pca] → Isolation Forest
"""

import numpy as np
import pandas as pd
import joblib
import logging
from typing import Tuple

logger = logging.getLogger("G4")

# Colonnes features dans l'ordre exact utilisé par G3
FEATURE_COLUMNS = [
    "global_active_power_kw",
    "global_reactive_power_kw",
    "voltage_v",
    "global_intensity_a",
    "sub_metering_1_wh",
    "sub_metering_2_wh",
    "sub_metering_3_wh",
]


def load_g3_params(scaler_path: str, pca_path: str) -> Tuple:
    """
    Charge le scaler et le PCA sauvegardés par G3 (via joblib).
    Ces fichiers sont partagés dans le dossier shared_models/ du repo.

    Returns:
        (scaler, pca) — objets scikit-learn déjà fittés
    """
    try:
        scaler = joblib.load(scaler_path)
        logger.info(f"Scaler G3 chargé depuis {scaler_path}")
    except FileNotFoundError:
        logger.warning(f"Scaler G3 non trouvé à {scaler_path}. Utilisation d'un StandardScaler par défaut.")
        from sklearn.preprocessing import StandardScaler
        scaler = None  # sera géré dans preprocess()

    try:
        pca = joblib.load(pca_path)
        logger.info(f"PCA G3 chargé depuis {pca_path}")
    except FileNotFoundError:
        logger.warning(f"PCA G3 non trouvé à {pca_path}. Pas de réduction dimensionnelle.")
        pca = None

    return scaler, pca


def preprocess(df: pd.DataFrame, scaler, pca) -> np.ndarray:
    """
    Applique la même chaîne de transformation que G3 :
      1. Extraire les colonnes features
      2. Imputer les NaN par la moyenne (sécurité)
      3. Scaler avec le scaler de G3
      4. Appliquer PCA de G3 (si disponible)

    Args:
        df: DataFrame avec au moins les colonnes FEATURE_COLUMNS
        scaler: StandardScaler fitté par G3 (ou None)
        pca: PCA fitté par G3 (ou None)

    Returns:
        X: numpy array prêt pour Isolation Forest
    """
    # 1. Extraire features
    X = df[FEATURE_COLUMNS].copy()

    # 2. Imputer NaN par la moyenne (sécurité avant scaling)
    X = X.fillna(X.mean())

    # 3. Scaler
    if scaler is not None:
        X_scaled = scaler.transform(X.values)
        logger.info("Scaling appliqué avec le scaler G3")
    else:
        # Fallback : on fit un scaler local (uniquement si G3 pas prêt)
        from sklearn.preprocessing import StandardScaler
        scaler_local = StandardScaler()
        X_scaled = scaler_local.fit_transform(X.values)
        logger.warning("Scaler G3 absent → StandardScaler local utilisé (résultats moins cohérents)")

    # 4. PCA
    if pca is not None:
        X_final = pca.transform(X_scaled)
        logger.info(f"PCA appliqué : {X_scaled.shape[1]} dims → {X_final.shape[1]} dims")
    else:
        X_final = X_scaled
        logger.warning("PCA G3 absent → données utilisées après scaling seulement")

    return X_final
