import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR = Path("outputs") / "plots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

baseline = pd.read_csv(DATA_DIR / "baseline_dec_2006.csv")
current  = pd.read_csv(DATA_DIR / "current_data.csv")

# Variables à visualiser (adapter au schéma DB)
FEATURES = [
    "global_active_power_kw",
    "global_intensity_a",
    "voltage_v",
]

def safe_numeric(s):
    return pd.to_numeric(s, errors="coerce").dropna().values

def plot_hist(feature: str, bins: int = 20):
    b = safe_numeric(baseline.get(feature, pd.Series(dtype=float)))
    c = safe_numeric(current.get(feature, pd.Series(dtype=float)))

    if len(b) == 0 or len(c) == 0:
        print(f"[SKIP] {feature}: données insuffisantes (baseline={len(b)}, current={len(c)})")
        return

    # mêmes bornes pour comparer
    lo = float(min(b.min(), c.min()))
    hi = float(max(b.max(), c.max()))
    if lo == hi:
        hi = lo + 1e-6

    edges = np.linspace(lo, hi, bins + 1)

    plt.figure()
    plt.hist(b, bins=edges, alpha=0.5, label="Baseline (Dec 2006)", density=True)
    plt.hist(c, bins=edges, alpha=0.5, label="Current (May 2007)", density=True)
    plt.title(f"Distribution: {feature}")
    plt.xlabel(feature)
    plt.ylabel("Density")
    plt.legend()
    out = OUT_DIR / f"hist_{feature}.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    print(f"[OK] {out}")

def plot_psi_bar():
    psi_file = Path("outputs") / "psi_scores.csv"
    if not psi_file.exists():
        print("[WARN] outputs/psi_scores.csv introuvable. Lance d'abord drift_detection.py")
        return

    df = pd.read_csv(psi_file)
    df = df.dropna(subset=["psi"])
    if df.empty:
        print("[WARN] psi_scores.csv ne contient pas de PSI numérique.")
        return

    plt.figure()
    plt.bar(df["feature"], df["psi"])
    plt.xticks(rotation=45, ha="right")
    plt.title("PSI par variable")
    plt.ylabel("PSI")
    out = OUT_DIR / "psi_bar.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    print(f"[OK] {out}")

if __name__ == "__main__":
    # Graphes baseline vs current
    for f in FEATURES:
        plot_hist(f, bins=20)

    # Bar chart PSI
    plot_psi_bar()

    print("✅ Graphes générés dans outputs/plots/")
