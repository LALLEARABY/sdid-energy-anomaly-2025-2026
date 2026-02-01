"""
G4 — Suite de tests
Teste l'ensemble du pipeline sans connexion à la base de données.
Utilise des données synthétiques pour valider chaque étape.

Exécution : python test_g4.py
"""

import numpy as np
import pandas as pd
import sys
import os
import logging

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TEST] %(levelname)s: %(message)s")
logger = logging.getLogger("TEST")

# Colonnes exactes du projet
FEATURE_COLUMNS = [
    "global_active_power_kw",
    "global_reactive_power_kw",
    "voltage_v",
    "global_intensity_a",
    "sub_metering_1_wh",
    "sub_metering_2_wh",
    "sub_metering_3_wh",
]


# ===========================================================================
# GÉNÉRATION DE DONNÉES SYNTHÉTIQUES
# ===========================================================================
def generate_synthetic_data(n_normal=800, n_anomaly=50, seed=42):
    """
    Génère un DataFrame synthétique qui ressemble aux données UCI.
    Les anomalies ont des valeurs extrêmes sur plusieurs colonnes.
    """
    np.random.seed(seed)

    # Données normales (distributions réalistes)
    normal = pd.DataFrame({
        "id": range(1, n_normal + 1),
        "global_active_power_kw": np.random.normal(1.5, 0.5, n_normal).clip(0.01, 5.0),
        "global_reactive_power_kw": np.random.normal(0.3, 0.1, n_normal).clip(0.0, 1.0),
        "voltage_v": np.random.normal(240, 3, n_normal).clip(220, 260),
        "global_intensity_a": np.random.normal(6.5, 2.0, n_normal).clip(0.1, 20.0),
        "sub_metering_1_wh": np.random.normal(1.2, 0.5, n_normal).clip(0, 5),
        "sub_metering_2_wh": np.random.normal(1.0, 0.3, n_normal).clip(0, 4),
        "sub_metering_3_wh": np.random.normal(6.5, 2.0, n_normal).clip(0, 20),
        "label": [False] * n_normal,
    })

    # Données anormales (pics et creux extrêmes)
    anomaly = pd.DataFrame({
        "id": range(n_normal + 1, n_normal + n_anomaly + 1),
        "global_active_power_kw": np.random.choice([0.01, 8.0, 10.0], n_anomaly),
        "global_reactive_power_kw": np.random.normal(1.5, 0.5, n_anomaly).clip(0.8, 3.0),
        "voltage_v": np.random.choice([215, 265, 270], n_anomaly).astype(float),
        "global_intensity_a": np.random.normal(18, 3, n_anomaly).clip(12, 25),
        "sub_metering_1_wh": np.random.normal(4.0, 1.0, n_anomaly).clip(2, 8),
        "sub_metering_2_wh": np.random.normal(3.5, 0.8, n_anomaly).clip(2, 6),
        "sub_metering_3_wh": np.random.normal(15, 4, n_anomaly).clip(8, 25),
        "label": [True] * n_anomaly,
    })

    df = pd.concat([normal, anomaly], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


# ===========================================================================
# SIMULER les artefacts G3 (scaler + pca)
# ===========================================================================
def simulate_g3_artifacts(df_train, scaler_path, pca_path):
    """
    Simule ce que G3 fait : fit un scaler et un PCA sur les données,
    puis les sauvegarde avec joblib (comme G3 le fait dans leur pipeline).
    """
    X = df_train[FEATURE_COLUMNS].fillna(df_train[FEATURE_COLUMNS].mean()).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, scaler_path)

    pca = PCA(n_components=3, random_state=42)
    pca.fit(X_scaled)
    joblib.dump(pca, pca_path)

    logger.info(f"Artefacts G3 simulés : scaler → {scaler_path}, pca → {pca_path}")
    return scaler, pca


# ===========================================================================
# TESTS
# ===========================================================================

def test_1_preprocess():
    """Test : prétraitement avec scaler + PCA simulés de G3."""
    logger.info("\n--- TEST 1 : Prétraitement ---")

    df = generate_synthetic_data(n_normal=500, n_anomaly=0)

    # Simuler artefacts G3
    scaler_path = "../G3_data_mining/artifacts/scaler.pkl"
    pca_path = "../G3_data_mining/artifacts/pca.pkl"
    scaler, pca = simulate_g3_artifacts(df, scaler_path, pca_path)

    # Importer et tester preprocess
    from G4_anomaly_engine.preprocessing.transform import preprocess, load_g3_params

    scaler_loaded, pca_loaded = load_g3_params(scaler_path, pca_path)
    X = preprocess(df, scaler_loaded, pca_loaded)

    assert X.shape[0] == len(df), f"Nombre de lignes incorrect : {X.shape[0]} vs {len(df)}"
    assert X.shape[1] == 3, f"PCA devrait réduire à 3 dimensions, got {X.shape[1]}"
    assert not np.isnan(X).any(), "Il y a des NaN après prétraitement"

    logger.info(f"  ✓ Shape correcte : {X.shape}")
    logger.info(f"  ✓ Pas de NaN")
    return scaler, pca


def test_2_train():
    """Test : entraînement du modèle Isolation Forest."""
    logger.info("\n--- TEST 2 : Entraînement ---")

    df = generate_synthetic_data(n_normal=800, n_anomaly=0)
    scaler_path = "../G3_data_mining/artifacts/test_scaler.pkl"
    pca_path = "../G3_data_mining/artifacts/test_pca.pkl"
    simulate_g3_artifacts(df, scaler_path, pca_path)

    from G4_anomaly_engine.preprocessing.transform import preprocess, load_g3_params
    from G4_anomaly_engine.modeling.train import train_isolation_forest

    scaler, pca = load_g3_params(scaler_path, pca_path)
    X_train = preprocess(df, scaler, pca)

    model, threshold = train_isolation_forest(X_train)

    assert model is not None, "Modèle est None"
    assert isinstance(threshold, float), "Threshold n'est pas un float"

    logger.info(f"  ✓ Modèle entraîné avec succès")
    logger.info(f"  ✓ Seuil τ = {threshold:.4f}")
    return model, threshold


def test_3_score():
    """Test : scoring avec détection des anomalies synthétiques."""
    logger.info("\n--- TEST 3 : Scoring & Détection ---")

    # Données d'entraînement (saines)
    df_train = generate_synthetic_data(n_normal=800, n_anomaly=0)
    scaler_path = "../G3_data_mining/artifacts/test_scaler.pkl"
    pca_path = "../G3_data_mining/artifacts/test_pca.pkl"
    simulate_g3_artifacts(df_train, scaler_path, pca_path)

    from G4_anomaly_engine.preprocessing.transform import preprocess, load_g3_params
    from G4_anomaly_engine.modeling.train import train_isolation_forest
    from G4_anomaly_engine.modeling.score import score_batch

    scaler, pca = load_g3_params(scaler_path, pca_path)
    X_train = preprocess(df_train, scaler, pca)
    model, threshold = train_isolation_forest(X_train)

    # Données de test (avec anomalies)
    df_test = generate_synthetic_data(n_normal=200, n_anomaly=30)
    X_test = preprocess(df_test, scaler, pca)
    y_true = df_test["label"].values

    # Scorer
    is_anomaly_list, scores_list = score_batch(model, threshold, X_test)
    y_pred = np.array(is_anomaly_list)

    # Calculer métriques
    tp = np.sum(y_pred & y_true)
    fp = np.sum(y_pred & ~y_true)
    fn = np.sum(~y_pred & y_true)
    tn = np.sum(~y_pred & ~y_true)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / len(y_true)

    logger.info(f"  Confusion Matrix : TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    logger.info(f"  ✓ Precision  : {precision:.2%}")
    logger.info(f"  ✓ Recall     : {recall:.2%}")
    logger.info(f"  ✓ F1-Score   : {f1:.2%}")
    logger.info(f"  ✓ Accuracy   : {accuracy:.2%}")

    assert accuracy > 0.70, f"Accuracy trop basse : {accuracy:.2%}"
    logger.info(f"  ✓ Accuracy > 70% : PASS")

    return tp, fp, fn, tn


def test_4_roi():
    """Test : calcul du ROI."""
    logger.info("\n--- TEST 4 : Calcul ROI ---")

    from G4_anomaly_engine.modeling.roi import calculate_roi, print_roi_report

    roi = calculate_roi(total_processed=3000, total_anomalies=150)

    assert roi["total_processed"] == 3000
    assert roi["total_anomalies"] == 150
    assert roi["benefice_net_eur"] > 0, "Le bénéfice net devrait être positif"
    assert roi["roi_pct"] > 0, "Le ROI devrait être positif"

    print_roi_report(roi)

    logger.info(f"  ✓ ROI calculé correctement : {roi['roi_pct']}%")
    logger.info(f"  ✓ Bénéfice net positif : {roi['benefice_net_eur']:,.2f} €")


def test_5_full_pipeline():
    """Test : pipeline complet du début à la fin."""
    logger.info("\n--- TEST 5 : Pipeline Complet ---")

    # Simuler G3
    df_all = generate_synthetic_data(n_normal=1000, n_anomaly=50)
    scaler_path = "../G3_data_mining/artifacts/test_scaler.pkl"
    pca_path = "../G3_data_mining/artifacts/test_pca.pkl"
    simulate_g3_artifacts(df_all, scaler_path, pca_path)

    from G4_anomaly_engine.preprocessing.transform import preprocess, load_g3_params
    from G4_anomaly_engine.modeling.train import train_isolation_forest
    from G4_anomaly_engine.modeling.score import score_batch
    from G4_anomaly_engine.modeling.roi import calculate_roi

    # 1. Charger params G3
    scaler, pca = load_g3_params(scaler_path, pca_path)

    # 2. Entraîner sur données historiques
    df_train = df_all[df_all["label"] == False].head(800)
    X_train = preprocess(df_train, scaler, pca)
    model, threshold = train_isolation_forest(X_train)

    # 3. Scorer un batch (comme le monitoring le fait)
    df_batch = df_all.sample(n=200, random_state=42)
    X_batch = preprocess(df_batch, scaler, pca)
    is_anomaly_list, scores_list = score_batch(model, threshold, X_batch)

    # 4. Calculer ROI
    n_anom = sum(is_anomaly_list)
    roi = calculate_roi(total_processed=200, total_anomalies=n_anom)

    logger.info(f"  ✓ Pipeline complet terminé")
    logger.info(f"  ✓ {n_anom} anomalies détectées sur 200 lignes")
    logger.info(f"  ✓ ROI : {roi['roi_pct']}%")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("\n" + "=" * 60)
    print("   G4 — SUITE DE TESTS")
    print("=" * 60 + "\n")

    tests = [
        ("Prétraitement", test_1_preprocess),
        ("Entraînement", test_2_train),
        ("Scoring & Détection", test_3_score),
        ("Calcul ROI", test_4_roi),
        ("Pipeline Complet", test_5_full_pipeline),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
            logger.info(f"  ✅ {name} : PASSED\n")
        except Exception as e:
            failed += 1
            logger.error(f"  ❌ {name} : FAILED — {e}\n")

    print("\n" + "=" * 60)
    print(f"   RÉSULTATS : {passed} passed, {failed} failed sur {len(tests)} tests")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
