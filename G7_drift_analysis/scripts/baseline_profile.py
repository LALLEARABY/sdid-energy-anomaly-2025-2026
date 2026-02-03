import pandas as pd
import json

df = pd.read_csv("data/baseline_dec_2006.csv")

features = ["Global_active_power", "Voltage", "Global_intensity"]

baseline = {}

for col in features:
    baseline[col] = {
        "mean": float(df[col].mean()),
        "std": float(df[col].std())
    }

with open("outputs/baseline_profile.json", "w") as f:
    json.dump(baseline, f, indent=4)

print("✅ Profil baseline créé")
