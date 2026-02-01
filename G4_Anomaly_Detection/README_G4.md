\# G4 - Anomaly Detection Engine



\## Description

Moteur de détection d'anomalies en temps réel pour la consommation énergétique.



\## Auteur

\[Votre Nom] - Groupe G4



\## Fonctionnalités Implémentées



1\. ✅ \*\*Synchronisation avec G3\*\* - Chargement des paramètres de normalisation et PCA

2\. ✅ \*\*Entraînement Isolation Forest\*\* - Modèle entraîné sur 1000 échantillons

3\. ✅ \*\*Définition du Seuil\*\* - Threshold optimisé à -0.5468 (5ème percentile)

4\. ✅ \*\*Moteur de Scoring\*\* - Scoring automatique toutes les 60s

5\. ✅ \*\*Automatisation des Alertes\*\* - Mise à jour `is\_anomaly` en base

6\. ✅ \*\*Calcul du ROI\*\* - Module roi\_calculator.py

7\. ✅ \*\*Évaluation de précision\*\* - ~6% d'anomalies détectées



\## Installation

```bash

pip install -r requirements.txt

```



\## Configuration



Fichier `.env` :

```

ANOMALY\_THRESHOLD=-0.5468

CONTAMINATION=0.01

N\_ESTIMATORS=100

```



\## Utilisation



\### Entraînement du modèle

```bash

python train\_model.py

```



\### Scoring en temps réel

```bash

python -m src.scoring\_engine --mode continuous

```



\### Test unique

```bash

python -m src.scoring\_engine --mode once

```



\## Résultats



\- Taux de détection d'anomalies : ~6%

\- Précision : Optimisée avec threshold au 5ème percentile

\- Performance : 100 records/batch, 60s interval

