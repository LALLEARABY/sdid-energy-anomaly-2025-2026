import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import json
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

baseline = pd.read_csv(DATA_DIR / "baseline_dec_2006.csv")
current  = pd.read_csv(DATA_DIR / "current_data.csv")

# Colonnes numériques disponibles dans la DB (adaptées au schéma du projet)
CANDIDATES = [
    "global_active_power_kw",
    "global_reactive_power_kw",
    "voltage_v",
    "global_intensity_a",
    "sub_metering_1_wh",
    "sub_metering_2_wh",
    "sub_metering_3_wh",
]

# Garder seulement celles qui existent vraiment
cols = [c for c in CANDIDATES if c in baseline.columns and c in current.columns]

def psi(expected, actual, buckets=10):
    expected = pd.to_numeric(expected, errors="coerce").dropna().values
    actual = pd.to_numeric(actual, errors="coerce").dropna().values
    if len(expected) == 0 or len(actual) == 0:
        return np.nan

    breakpoints = np.linspace(0, 100, buckets + 1)
    exp_bins = np.percentile(expected, breakpoints)
    act_bins = np.percentile(actual, breakpoints)

    psi_val = 0.0
    for i in range(buckets):
        e = ((expected >= exp_bins[i]) & (expected < exp_bins[i+1])).mean()
        a = ((actual >= act_bins[i]) & (actual < act_bins[i+1])).mean()
        # éviter log(0)
        e = max(e, 1e-6)
        a = max(a, 1e-6)
        psi_val += (a - e) * np.log(a / e)
    return float(psi_val)

results = {}
for col in cols:
    psi_val = psi(baseline[col], current[col])
    ks_stat, ks_p = ks_2samp(
        pd.to_numeric(baseline[col], errors="coerce").dropna().values,
        pd.to_numeric(current[col], errors="coerce").dropna().values
    )
    results[col] = {"psi": psi_val, "ks_stat": float(ks_stat), "ks_pvalue": float(ks_p)}

# Sauvegardes
psi_df = pd.DataFrame(
    [{"feature": k, "psi": v["psi"], "ks_stat": v["ks_stat"], "ks_pvalue": v["ks_pvalue"]} for k, v in results.items()]
)
psi_df.to_csv(OUT_DIR / "psi_scores.csv", index=False)

report = {
    "baseline_file": str(DATA_DIR / "baseline_dec_2006.csv"),
    "current_file": str(DATA_DIR / "current_data.csv"),
    "features_checked": cols,
    "results": results,
    "interpretation": {
        "psi_threshold_alert": 0.25,
        "psi_threshold_critical": 0.50
    }
}
(OUT_DIR / "drift_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("Drift calculé ✅  Résultats dans outputs/psi_scores.csv et outputs/drift_report.json")
