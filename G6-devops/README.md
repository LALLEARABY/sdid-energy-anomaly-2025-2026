G6 – DevOps (Docker / Compose / Security / Env / Networks)
1) Rôle du groupe G6

Le groupe G6 est responsable de la partie DevOps du projet.
Notre travail consiste à fournir une exécution fiable, sécurisée et reproductible via Docker et Docker Compose, ainsi qu’une gestion propre des variables d’environnement, des réseaux, et des bonnes pratiques security.

2) Objectifs

Créer une configuration Docker Compose dédiée au projet (G6)

Centraliser la configuration via .env / .env.example

Isoler les services via un réseau interne (backend)

Sécuriser le déploiement (permissions, no-new-privileges, init SQL)

Permettre un lancement minimal (DB فقط) و Full stack (اختياري عبر profiles)

3) Architecture (G6 Compose)

Le fichier principal du groupe G6 est :

✅ G6-devops/docker-compose.yml

Il contient :

Service obligatoire

db (PostgreSQL 15)

Chargement des variables depuis .env

Volume persistant postgres_data

Healthcheck pg_isready

Script de sécurité PostgreSQL exécuté au démarrage

Services optionnels (templates)

Ces services sont inclus comme templates et peuvent être activés via profiles: ["full"] :

ingestion (G2)

analysis (G4)

dashboard (G5)

4) Variables d’environnement
Fichier utilisé

.env (non commité dans GitHub)

.env.example (commité pour aider l’équipe)

Exemple :

POSTGRES_DB=sdid_db
POSTGRES_USER=sdid_user
POSTGRES_PASSWORD=sdid_password
DB_HOST=db
DB_PORT=5432


📌 .env يجب يكون محلي فقط (secret).

5) Sécurité (PostgreSQL)

G6 ajoute un script SQL de sécurité exécuté automatiquement عند أول تشغيل:

📌 G6-devops/config/postgres_security.sql

Il peut contenir:

restrictions d’accès

configuration de privilèges

création rôles limitéة

6) Réseaux (Networks)

G6 يعتمد شبكة داخلية:

backend network

internal: true لتجنب التعرض المباشر للخدمات

استعمال bridge network لعزل المكونات
