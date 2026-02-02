Mini-rapport — Groupe 6 (G6) : DevOps (Docker/Compose/Security/Env/Networks)

1\) Contexte du projet



Le projet SDID Energy Anomaly 2025–2026 regroupe plusieurs composants (ingestion, analyse, dashboard, etc.). Pour garantir un déploiement simple et identique pour tous, le groupe G6 met en place l’infrastructure Docker / Docker Compose, avec une configuration propre des variables d’environnement, des réseaux et des règles de sécurité.



2\) Rôle du groupe G6



Le groupe G6 est responsable de :



Fournir une orchestration Docker Compose claire et reproductible.



Déployer et configurer PostgreSQL comme service central.



Standardiser la gestion des variables d’environnement via .env et .env.example.



Ajouter des règles de sécurité (options de sécurité Docker + init SQL).



Définir les réseaux (isolation des services, réseau interne).



Proposer une procédure de lancement et de validation.



3\) Livrables (ce que G6 fournit)

3.1 Compose dédié G6



Fichier :



G6-devops/docker-compose.yml



Contenu :



Service db (PostgreSQL 15) : composant obligatoire.



Services optionnels (templates) activables via profiles: \["full"] :



ingestion (G2)



analysis (G4)



dashboard (G5)



3.2 Variables d’environnement



.env : fichier local (non versionné) contenant les paramètres sensibles.



.env.example : modèle versionné sur GitHub, sans secrets, pour aider les autres à configurer rapidement.



3.3 Sécurité PostgreSQL (init SQL)



Script d’initialisation monté en lecture seule :



G6-devops/config/postgres\_security.sql



Objectif : appliquer des paramètres/bonnes pratiques de sécurité à l’initialisation.



3.4 Réseau et isolation



Réseau backend avec internal: true pour limiter l’exposition externe.



Limitation des privilèges via :



security\_opt: \["no-new-privileges:true"]

