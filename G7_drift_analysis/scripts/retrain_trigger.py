import pandas as pd

psi_df = pd.read_csv("outputs/psi_scores.csv")

if psi_df["PSI"].max() > 0.5:
    print("🔁 DRIFT SÉVÈRE → Ré-entraînement automatique")
else:
    print("✅ Modèle stable")
