# G6 – DevOps (Docker / Compose / Sécurité / Environnement / Réseaux)

## 1) Rôle du groupe G6

Le groupe G6 est responsable de la partie DevOps du projet.
Son rôle est d’assurer une exécution fiable, sécurisée et reproductible à l’aide de Docker et Docker Compose, ainsi qu’une gestion propre des variables d’environnement, des réseaux et des bonnes pratiques de sécurité.

## 2) Objectifs

Créer une configuration Docker Compose dédiée au projet (G6)

Centraliser la configuration via .env et .env.example

Isoler les services via un réseau interne (backend)

Sécuriser le déploiement (permissions, no-new-privileges, initialisation SQL)

Permettre un lancement minimal (base de données uniquement) ou un lancement full stack optionnel via les profiles

## 3) Architecture (Compose G6)

Le fichier principal du groupe G6 est :

 G6-devops/docker-compose.yml

Il contient :

Service obligatoire

db (PostgreSQL 15)

Chargement des variables depuis .env

Volume persistant postgres_data

Healthcheck avec pg_isready

Script de sécurité PostgreSQL exécuté au démarrage

Services optionnels (templates)

Ces services sont inclus comme modèles et peuvent être activés via profiles: ["full"] :

ingestion (G2)

analysis (G4)

dashboard (G5)

## 4) Variables d’environnement

Fichiers utilisés

.env (non versionné sur GitHub)

.env.example (versionné pour aider l’équipe)

Exemple de variables :

POSTGRES_DB=sdid_db

POSTGRES_USER=sdid_user

POSTGRES_PASSWORD=sdid_password

DB_HOST=db

DB_PORT=5432

Le fichier .env doit rester local et contenir uniquement des informations sensibles.

## 5) Sécurité (PostgreSQL)

Le groupe G6 ajoute un script SQL de sécurité exécuté automatiquement lors du premier démarrage :

 G6-devops/config/postgres_security.sql

Ce script peut inclure :

Des restrictions d’accès

La configuration des privilèges

La création de rôles avec des permissions limitées

## 6) Réseaux (Networks)

Le groupe G6 utilise un réseau interne dédié :

Réseau backend

Option internal: true pour éviter l’exposition directe des services

Utilisation d’un réseau de type bridge pour isoler les composants
