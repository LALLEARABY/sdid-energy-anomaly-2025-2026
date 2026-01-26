import joblib
from sklearn.preprocessing import RobustScaler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = BASE_DIR / "artifacts" / "scaler.pkl"

def scale_data(df):
    print("Normalisation des données avec RobustScaler")

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(df)

    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(scaler, ARTIFACT_PATH)

    return X_scaled, scaler
