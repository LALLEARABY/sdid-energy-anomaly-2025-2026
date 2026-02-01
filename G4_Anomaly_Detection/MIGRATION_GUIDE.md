# Migration Guide: G4_anomaly_engine → G4_Anomaly_Detection

## Vue d'ensemble
Ce guide décrit la migration de l'ancien projet **G4_anomaly_engine** vers le nouveau **G4_Anomaly_Detection**.

## Changements principaux

### Structure du projet
- Nouvelle organisation modulaire
- Séparation claire entre config, src, docs, notebooks et tests
- Ajout de fichiers de configuration (.env.example)

### Fonctionnalités améliorées
- Nouveau système de détection d'anomalies
- Calcul ROI optimisé
- Base de données mise à jour
- Meilleur système de scoring

## Étapes de migration

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
- Copier .env.example vers .env
- Configurer les paramètres dans config/config.py

### 3. Migration des données
```bash
python migrate.py
```

### 4. Entraînement du modèle
```bash
python train_model.py
```

### 5. Démarrage rapide
```bash
python quickstart.py
```

## Support
Pour toute question, consultez la documentation dans docs/technical_report.md
