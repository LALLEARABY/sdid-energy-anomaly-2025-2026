import pandas as pd

df = pd.read_csv("data/current_data.csv")

precision_baseline = 0.95
precision_current = 1 - df["is_anomaly"].mean()

loss = precision_baseline - precision_current

print(f"📉 Perte de précision : {loss*100:.2f}%")

if loss > 0.10:
    print("🚨 Modèle dégradé → Ré-entraînement conseillé")
