"""
G4 — Calcul du ROI (Return on Investment)
Modèle économique : combien le système économise en détectant les anomalies
vs le coût des fausses alertes.
"""

from typing import Dict
import logging

logger = logging.getLogger("G4")

# Paramètres économiques (en €)
COST_PER_OUTAGE = 5000          # Coût moyen d'une panne électrique évitée
COST_PER_FALSE_ALERT = 50       # Coût d'une investigation de fausse alerte
TRUE_POSITIVE_RATE = 0.80       # Estimation : 80% des anomalies détectées sont réelles
PREVENTION_EFFECTIVENESS = 0.70 # 70% des vraies anomalies sont prévenues à temps


def calculate_roi(total_processed: int, total_anomalies: int) -> Dict:
    """
    Calcule le ROI à partir des compteurs du monitoring.

    Formule :
        TP estimés = anomalies × TRUE_POSITIVE_RATE
        FP estimés = anomalies − TP
        Pannes évitées = TP × PREVENTION_EFFECTIVENESS
        Économies = Pannes évitées × COST_PER_OUTAGE
        Coût investigation = anomalies × COST_PER_FALSE_ALERT
        Bénéfice net = Économies − Coût
        ROI (%) = (Bénéfice net / Coût) × 100
    """
    if total_processed == 0:
        return {"error": "Aucune donnée traitée"}

    tp = int(total_anomalies * TRUE_POSITIVE_RATE)
    fp = total_anomalies - tp
    pannes_evitees = int(tp * PREVENTION_EFFECTIVENESS)

    economies = pannes_evitees * COST_PER_OUTAGE
    cout_investigation = total_anomalies * COST_PER_FALSE_ALERT
    benefice_net = economies - cout_investigation
    roi_pct = (benefice_net / cout_investigation * 100) if cout_investigation > 0 else 0
    taux_anomalies = (total_anomalies / total_processed) * 100

    return {
        "total_processed": total_processed,
        "total_anomalies": total_anomalies,
        "taux_anomalies_pct": round(taux_anomalies, 2),
        "tp_estimes": tp,
        "fp_estimes": fp,
        "pannes_evitees": pannes_evitees,
        "economies_eur": round(economies, 2),
        "cout_investigation_eur": round(cout_investigation, 2),
        "benefice_net_eur": round(benefice_net, 2),
        "roi_pct": round(roi_pct, 2),
    }


def print_roi_report(roi: Dict):
    """Affiche le rapport ROI dans la console."""
    print("\n" + "=" * 60)
    print("   G4 — RAPPORT ROI")
    print("=" * 60)
    print(f"  Lignes traitées       : {roi['total_processed']:,}")
    print(f"  Anomalies détectées   : {roi['total_anomalies']:,}")
    print(f"  Taux d'anomalies      : {roi['taux_anomalies_pct']}%")
    print("-" * 60)
    print(f"  TP estimés            : {roi['tp_estimes']}")
    print(f"  FP estimés            : {roi['fp_estimes']}")
    print(f"  Pannes évitées        : {roi['pannes_evitees']}")
    print("-" * 60)
    print(f"  Économies             : {roi['economies_eur']:,.2f} €")
    print(f"  Coût investigation    : {roi['cout_investigation_eur']:,.2f} €")
    print(f"  Bénéfice net          : {roi['benefice_net_eur']:,.2f} €")
    print(f"  ROI                   : {roi['roi_pct']}%")
    print("=" * 60)
