"""
G4 — Moteur de Détection d'Anomalies
Pipeline principal: charge données → normalise avec scaler G3 → PCA G3 → Isolation Forest → score → UPDATE BD
"""

from G4_anomaly_engine.data_access.fetch_data import fetch_unscored, fetch_historical
from G4_anomaly_engine.preprocessing.transform import load_g3_params, preprocess
from G4_anomaly_engine.modeling.train import train_isolation_forest
from G4_anomaly_engine.modeling.score import score_batch
from G4_anomaly_engine.modeling.roi import calculate_roi, print_roi_report
from G4_anomaly_engine.data_access.update_db import update_anomaly_flags
import joblib
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [G4] %(levelname)s: %(message)s")
logger = logging.getLogger("G4")

# Chemins des artefacts G3 (partagés via le repo)
SCALER_PATH = "../G3_data_mining/artifacts/scaler.pkl"
PCA_PATH = "../G3_data_mining/artifacts/pca.pkl"
MODEL_PATH = "G4_anomaly_engine/shared_models/isolation_forest.pkl"
THRESHOLD_PATH = "G4_anomaly_engine/shared_models/threshold.pkl"

BATCH_SIZE = 200
POLL_INTERVAL = 10  # secondes entre chaque cycle


def train_phase():
    """Phase 1 : Entraînement du modèle sur données historiques."""
    logger.info("=== PHASE ENTRAÎNEMENT ===")

    # 1. Charger données historiques (lignes déjà scorées ou suffisamment anciennes)
    df_train = fetch_historical(limit=10000)
    logger.info(f"Données historiques chargées : {len(df_train)} lignes")

    # 2. Charger scaler + pca produits par G3
    scaler, pca = load_g3_params(SCALER_PATH, PCA_PATH)

    # 3. Prétraiter avec les params G3
    X_train = preprocess(df_train, scaler, pca)
    logger.info(f"Données prétraitées : shape {X_train.shape}")

    # 4. Entraîner Isolation Forest + calculer seuil
    model, threshold = train_isolation_forest(X_train)
    logger.info(f"Modèle entraîné. Seuil (τ) = {threshold:.4f}")

    # 5. Sauvegarder modèle + seuil
    joblib.dump(model, MODEL_PATH)
    joblib.dump(threshold, THRESHOLD_PATH)
    logger.info("Modèle et seuil sauvegardés.")


def monitoring_loop():
    """Phase 2 : Boucle de monitoring continu."""
    logger.info("=== PHASE MONITORING (Ctrl+C pour arrêter) ===")

    # Charger modèle entraîné
    model = joblib.load(MODEL_PATH)
    threshold = joblib.load(THRESHOLD_PATH)
    scaler, pca = load_g3_params(SCALER_PATH, PCA_PATH)

    total_processed = 0
    total_anomalies = 0

    while True:
        # 1. Récupérer lignes non scorées (scored_at IS NULL)
        df_batch = fetch_unscored(limit=BATCH_SIZE)

        if df_batch.empty:
            logger.info("Aucune ligne non scorée. Attente...")
            time.sleep(POLL_INTERVAL)
            continue

        logger.info(f"Batch récupéré : {len(df_batch)} lignes")

        # 2. Prétraiter
        X_batch = preprocess(df_batch, scaler, pca)

        # 3. Scorer avec le modèle
        is_anomaly_list, scores_list = score_batch(model, threshold, X_batch)

        # 4. UPDATE dans la BD
        ids = df_batch["id"].tolist()
        update_anomaly_flags(ids, is_anomaly_list, scores_list)

        # 5. Compteurs
        n_anomalies = sum(is_anomaly_list)
        total_processed += len(df_batch)
        total_anomalies += n_anomalies
        logger.info(f"Scoré {len(df_batch)} lignes → {n_anomalies} anomalies détectées")

        # 6. Afficher ROI toutes les 5 itérations
        if total_processed % (BATCH_SIZE * 5) == 0:
            roi = calculate_roi(total_processed, total_anomalies)
            print_roi_report(roi)

        time.sleep(POLL_INTERVAL)


def main():
    logger.info("============================================")
    logger.info("   G4 — Moteur de Détection d'Anomalies")
    logger.info("============================================")

    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "train":
        train_phase()
    elif mode == "monitor":
        monitoring_loop()
    else:  # full
        train_phase()
        monitoring_loop()


if __name__ == "__main__":
    main()
