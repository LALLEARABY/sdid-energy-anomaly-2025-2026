# G3 – Data Mining et Analyse de Patterns

## Rôle du groupe G3
Le groupe G3 est chargé d’identifier les **comportements normaux de consommation
électrique** à partir des données historiques stockées dans la base PostgreSQL mise en
place par le groupe G2.

Cette analyse repose sur des **méthodes non supervisées** et constitue une étape
clé pour le groupe G4 (détection d’anomalies).

---

## Objectifs
- Extraire les données historiques depuis PostgreSQL
- Normaliser les variables électriques
- Réduire la dimension des données à l’aide de l’ACP (PCA)
- Identifier des profils de consommation normaux via DBSCAN
- Générer des artefacts réutilisables par les autres groupes

---

## Méthodologie
1. Lecture des données depuis la table `power_consumption`
2. Prétraitement et normalisation robuste des variables
3. Réduction de dimension par Analyse en Composantes Principales (ACP)
4. Clustering des comportements à l’aide de DBSCAN
5. Sauvegarde des modèles et paramètres

---

## Variables utilisées
- `global_active_power_kw`
- `voltage_v`
- `global_intensity_a`

Les valeurs nulles sont exclues avant l’analyse.

---

## Artefacts produits
Les fichiers suivants sont générés automatiquement dans le dossier `artifacts/` :

- `scaler.pkl`  
  → Paramètres de normalisation (RobustScaler)

- `pca.pkl`  
  → Modèle ACP entraîné

- `dbscan_params.json`  
  → Hyperparamètres du clustering DBSCAN

- `clusters.json`  
  → Répartition des observations par cluster

Ces artefacts sont utilisés directement par le groupe G4.

---

## Visualisation
Un graphique de projection ACP + clustering est généré :

- `visualization/pca_clusters.png`

Il permet de visualiser la séparation des comportements de consommation.

---

## Exécution
Avant de lancer ce module :
- La base PostgreSQL doit être active (pipeline G2)
- Les données doivent être en cours d’ingestion ou déjà présentes

Lancement du pipeline complet :
```bash
python main.py
