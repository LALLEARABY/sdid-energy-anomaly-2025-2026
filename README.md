# sdid-energy-anomaly-2025-2026
# Projet : Détection d’anomalies dans la consommation électrique

## 1. Objectif du projet

L’objectif de ce projet est de concevoir un système complet de surveillance de la consommation électrique permettant de détecter automatiquement des comportements anormaux à partir de données réelles.  
Le projet couvre l’ensemble de la chaîne de traitement des données, depuis leur ingestion jusqu’à leur visualisation, en passant par l’analyse et la détection d’anomalies.

Ce travail s’inscrit dans une logique de systèmes décisionnels et de monitoring énergétique, similaires à ceux utilisés dans les réseaux électriques intelligents et les environnements industriels.

---

## 2. Principe général de fonctionnement

Le projet repose sur une architecture de type **pipeline de données**, dans laquelle les données sont traitées par étapes successives.  
Chaque mesure de consommation électrique suit le cycle suivant :

1. Ingestion des données brutes
2. Stockage centralisé dans une base de données
3. Analyse des comportements normaux
4. Détection automatique des anomalies
5. Visualisation et suivi des résultats

Chaque étape est prise en charge par un module distinct, développé par un groupe spécifique.

---

## 3. Organisation du projet par groupes

Le projet est organisé en sept groupes, chacun ayant un rôle clairement défini.

### G1 — Coordination, Git et standardisation
- Création et gestion du dépôt GitHub centralisé
- Définition du dictionnaire de données
- Définition des contrats d’interface entre les modules
- Garantie de la cohérence globale du projet

### G2 — Ingestion des données
- Lecture des données brutes (CSV)
- Nettoyage des données et gestion des valeurs manquantes
- Construction du timestamp à partir des champs date et heure
- Insertion des données dans la base PostgreSQL

### G3 — Analyse des patterns
- Lecture des données depuis la base
- Analyse des comportements normaux de consommation
- Identification des structures et relations entre variables
- Production des paramètres et modèles nécessaires à la détection d’anomalies

### G4 — Détection des anomalies
- Lecture des données non encore analysées
- Application des modèles fournis par G3
- Calcul d’un score d’anomalie
- Mise à jour de la base de données avec les résultats

### G5 — Dashboard et visualisation
- Lecture des données depuis la base
- Visualisation des séries temporelles
- Affichage des anomalies détectées
- Aide à la surveillance et à la prise de décision

### G6 — Déploiement et sécurité
- Gestion de la configuration du système
- Sécurisation des accès et des services
- Support au déploiement des différents modules

### G7 — Analyse de dérive des données
- Analyse de l’évolution des données dans le temps
- Détection de changements structurels ou comportementaux à long terme

---

## 4. Base de données centrale

Le cœur du projet est une base de données PostgreSQL qui constitue la source unique de vérité pour l’ensemble des modules.

### Table principale : `power_consumption`

Chaque ligne de la table représente une mesure de consommation électrique à un instant précis.  
La table contient :
- un timestamp représentant le moment exact de la mesure,
- les variables de consommation électrique,
- les résultats de la détection d’anomalies,
- des champs de traçabilité système.

Les données brutes sont insérées une seule fois et ne sont jamais modifiées.  
Les résultats d’analyse sont ajoutés séparément afin de préserver l’intégrité des données.

---

## 5. Standardisation et cohérence

Afin d’assurer la cohérence du travail collaboratif, deux documents de référence sont fournis :

- **Dictionnaire de données** (`docs/data_dictionary.md`)  
  Définit les tables, les colonnes et les types SQL utilisés dans la base.

- **Contrats d’interface** (`docs/interface_contracts.md`)  
  Précisent les règles d’échange entre les modules (lecture et écriture des données).

Ces documents garantissent que tous les groupes travaillent avec les mêmes conventions et évitent les conflits d’implémentation.

---

## 6. Flux global des données

## 7. Résultats attendus

À l’issue du projet, le système doit permettre :
- le suivi de l’évolution de la consommation électrique dans le temps,
- la détection automatique des comportements anormaux,
- la visualisation claire et interprétable des anomalies,
- une meilleure compréhension des phénomènes énergétiques observés.

---

## 8. Conclusion

Ce projet met en œuvre une architecture complète de traitement de données, combinant ingestion, stockage, analyse, détection et visualisation.  
Il illustre de manière concrète la conception d’un système décisionnel basé sur les données, proche des systèmes utilisés en conditions réelles.

