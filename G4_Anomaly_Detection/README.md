# G4 - Anomaly Detection Engine & ROI Calculator

**Projet SDID 2025/2026 - Groupe 4**  
Système de Détection d'Anomalies en Temps Réel pour la Surveillance Énergétique

---

## 📋 Description

Ce module implémente un **moteur de détection d'anomalies** en temps réel utilisant l'algorithme **Isolation Forest** pour identifier les comportements anormaux dans les données de consommation électrique. Il calcule également le **ROI (Return on Investment)** du système.

### Fonctionnalités principales

1. **Synchronisation avec G3** : Utilise les paramètres de normalisation et l'ACP fournis par le Groupe 3
2. **Entraînement du modèle** : Isolation Forest sur données historiques propres
3. **Scoring en temps réel** : Moteur "consommateur" qui interroge PostgreSQL régulièrement
4. **Alertes automatiques** : Mise à jour du champ `is_anomaly` dans la base de données
5. **Calcul du ROI** : Évaluation financière (pannes évitées vs fausses alertes)
6. **Statistiques de performance** : Métriques transmises au Groupe 1

---

## 🏗️ Architecture

```
G4_Anomaly_Detection/
├── config/
│   └── config.py              # Configuration (DB, modèle, ROI)
├── src/
│   ├── database.py            # Connexion PostgreSQL
│   ├── preprocessor.py        # Chargement paramètres G3 + transformation
│   ├── anomaly_detector.py    # Modèle Isolation Forest
│   ├── scoring_engine.py      # Moteur de scoring temps réel
│   └── roi_calculator.py      # Calcul du ROI
├── models/
│   ├── g3_scaler.pkl          # Scaler du G3 (à récupérer)
│   ├── g3_pca.pkl             # PCA du G3 (à récupérer)
│   └── anomaly_detector.pkl   # Modèle entraîné
├── docs/
│   ├── score_distribution.png # Visualisation des scores
│   └── roi_report.txt         # Rapport ROI
├── notebooks/
│   └── analysis.ipynb         # Analyses exploratoires
├── tests/
│   └── test_*.py              # Tests unitaires
├── .env                       # Variables d'environnement (à créer)
├── .env.example               # Exemple de configuration
├── requirements.txt           # Dépendances Python
├── train_model.py             # Script d'entraînement
└── README.md                  # Ce fichier
```

---

## 🚀 Installation




---

## 🐳 Utilisation avec Docker

### Démarrage rapide
```bash
# Depuis la racine du projet
docker-compose up -d g4_anomaly_detection

# Vérifier les logs
docker logs -f g4_anomaly_detection

# Voir les statistiques
docker exec -it sdid_postgres psql -U sdid_user -d sdid_db -c "SELECT COUNT(*) as total, SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomalies FROM power_consumption;"
```

### Services Docker disponibles

- **g4_anomaly_detection** : Scoring engine en mode continu
- **g4_roi** : Calculateur de ROI (lancer avec `docker-compose run --rm g4_roi`)

### Variables d'environnement Docker

Les variables sont configurées dans `docker-compose.yml` :
- `DB_HOST=db` (nom du service PostgreSQL)
- `DB_PORT=5432`
- `ANOMALY_THRESHOLD=-0.5468`
- `SCORING_INTERVAL=60`





### 1. Prérequis

- Python 3.8+
- PostgreSQL (fourni par G2)
- Paramètres G3 (scaler + PCA)

### 2. Installation des dépendances

```bash
cd G4_Anomaly_Detection
pip install -r requirements.txt
```

### 3. Configuration

Créez un fichier `.env` à partir de `.env.example` :

```bash
cp .env.example .env
```

Modifiez `.env` avec vos paramètres :

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=power_consumption_db
DB_USER=votre_user
DB_PASSWORD=votre_password

# Model
ANOMALY_THRESHOLD=-0.5
CONTAMINATION=0.01
N_ESTIMATORS=100

# ROI
COST_PREVENTED_FAILURE=5000
COST_FALSE_ALARM=50
ENERGY_COST_PER_KWH=0.15
```

### 4. Récupération des paramètres G3

Placez les fichiers du Groupe 3 dans le dossier `models/` :

```bash
# À récupérer depuis le dépôt G3
models/g3_scaler.pkl
models/g3_pca.pkl
```

---

## 📊 Utilisation

### Étape 1 : Entraînement du modèle

```bash
python train_model.py
```

Options disponibles :
```bash
python train_model.py --samples 10000  # Limiter à 10k échantillons
python train_model.py --algorithm lof  # Utiliser LOF au lieu d'Isolation Forest
python train_model.py --validate       # Valider après entraînement
```

**Sortie attendue** :
- Modèle sauvegardé : `models/anomaly_detector.pkl`
- Graphique : `docs/score_distribution.png`
- Logs avec statistiques d'entraînement

### Étape 2 : Scoring en temps réel

**Mode continu** (recommandé pour production) :
```bash
python src/scoring_engine.py --mode continuous --interval 60
```

**Mode unique** (pour tests ou cron) :
```bash
python src/scoring_engine.py --mode once
```

**Sortie attendue** :
- Mise à jour automatique de la colonne `is_anomaly` en base
- Logs des anomalies détectées en temps réel
- Statistiques de performance

### Étape 3 : Calcul du ROI

```bash
python src/roi_calculator.py
```

**Sortie attendue** :
- Rapport détaillé : `docs/roi_report.txt`
- Affichage console des métriques financières

---

## 🔧 Développement

### Tests unitaires

```bash
pytest tests/
```

### Analyse exploratoire

Ouvrir le notebook Jupyter :
```bash
jupyter notebook notebooks/analysis.ipynb
```

### Ajuster le seuil d'anomalie

1. Observer `docs/score_distribution.png`
2. Modifier `ANOMALY_THRESHOLD` dans `.env`
3. Re-exécuter le scoring engine

---

## 📈 Métriques clés

Le système fournit les métriques suivantes (transmises à G1) :

### Métriques de détection
- Taux d'anomalies détectées
- Distribution des scores
- Fréquence des alertes

### Métriques financières (ROI)
- Coût total du système
- Bénéfices (pannes évitées + économies d'énergie)
- ROI en %
- Période de retour sur investissement
- Ratio bénéfices/coûts

### Exemples de résultats

```
Total records analyzed:    5,000
Anomalies detected:        ~300
Anomaly rate:              ~6%

Anomaly threshold:         -0.5468 (5th percentile)


Top anomalies detected:
- Overconsumption: 5.4-5.9 kW (vs normal 2-4 kW)
- Underconsumption: 1.0-1.6 kW
- Voltage anomalies: 235-245 V (vs normal 220-240 V)



Energy cost savings:       $1,875.00
Value of prevention:       $218,750.00
False alarm cost:          $312.50

NET BENEFIT:               $210,312.50
ROI:                       2003.12%
Payback period:            18 days
```

---

## 🔄 Intégration avec les autres groupes

### Dépendances en entrée

| Groupe | Fichier(s) requis | Description |
|--------|------------------|-------------|
| **G2** | Base PostgreSQL | Table `power_consumption` avec flux temps réel |
| **G3** | `g3_scaler.pkl`<br>`g3_pca.pkl` | Paramètres de normalisation et ACP |

### Sorties vers les autres groupes

| Groupe | Livrable | Description |
|--------|----------|-------------|
| **G1** | Mini-rapport technique | Méthodologie + résultats + code |
| **G1** | Statistiques | Métriques de performance JSON/CSV |
| **G5** | Colonne `is_anomaly` | Champ mis à jour en temps réel pour dashboard |

---

## 🛠️ Résolution de problèmes

### Problème : "G3 parameters not found"
**Solution** : Vérifier que `models/g3_scaler.pkl` et `models/g3_pca.pkl` existent. Si non, contacter G3.

### Problème : "Failed to connect to database"
**Solution** : 
1. Vérifier que PostgreSQL est démarré (G2)
2. Vérifier les credentials dans `.env`
3. Tester : `python src/database.py`

### Problème : Trop de fausses alertes
**Solution** : 
1. Analyser `docs/score_distribution.png`
2. Augmenter `ANOMALY_THRESHOLD` dans `.env` (ex: -0.3 au lieu de -0.5)
3. Re-exécuter le scoring

### Problème : Pas assez d'anomalies détectées
**Solution** : 
1. Diminuer `ANOMALY_THRESHOLD` (ex: -0.7)
2. Augmenter `CONTAMINATION` dans `.env`

---

## 📝 Livrables pour G1

### 1. Code
- ✅ Dépôt GitHub avec branche `g4-anomaly-detection`
- ✅ Code commenté et structuré
- ✅ Tests unitaires

### 2. Documentation
- ✅ README complet (ce fichier)
- ✅ Mini-rapport technique (docs/technical_report.md)
- ✅ Rapport ROI (docs/roi_report.txt)

### 3. Résultats
- ✅ Modèle entraîné (`models/anomaly_detector.pkl`)
- ✅ Graphiques de distribution
- ✅ Statistiques de performance (JSON)

---

## 👥 Contributeurs

**Groupe 4 - SDID 2025/2026**

- [2309 23644 23658] - Lead Developer
  - Développement du modèle Isolation Forest
  - Moteur de scoring temps réel
  - Calcul du ROI et métriques financières
  - Intégration Docker et CI/CD
---

## 📚 Références

- Dataset UCI : "Individual Household Electric Power Consumption"
- Algorithme : Isolation Forest (Liu et al., 2008)
- Alternative : Local Outlier Factor (Breunig et al., 2000)

---

## 📧 Contact

Pour toute question technique, contacter le Groupe 4 via le canal Slack `#g4-anomalies` ou ouvrir une issue sur GitHub.

---

**Dernière mise à jour** : Janvier 2026
