# Groupe 7 – Drift Detection

Objectif :
Détecter la dérive des données dans le temps afin de décider du ré-entraînement des modèles.

Méthodes :
- Population Stability Index (PSI)
- Kolmogorov-Smirnov Test (KS)

Pipeline :
PostgreSQL → Extraction → Baseline vs Current → PSI / KS → Rapport

Sorties :
- outputs/psi_scores.csv
- outputs/drift_report.json
