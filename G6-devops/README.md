\# G6 – DevOps (Docker / Compose / Security / Env / Networks)



Ce dossier contient le travail du \*\*Groupe 6\*\* : mise en place d’une base \*\*PostgreSQL\*\* isolée via Docker Compose, avec gestion des variables d’environnement, réseau dédié, volume persistant, healthcheck et durcissement de base (security options + init SQL).



---



\## Structure



G6-devops/

├─ docker-compose.yml

├─ .env.example

├─ config/

│ └─ postgres\_security.sql

└─ README.md



yaml

Copier le code



---



\## Prérequis



\- Docker Desktop (mode Linux containers)

\- Docker Compose v2 (commande `docker compose`)

\- Git



---



\## Variables d’environnement



⚠️ \*\*Ne jamais pousser\*\* un fichier `.env` réel sur GitHub.



1\) Copier l’exemple :

```bash

cp .env.example .env

Modifier .env selon votre machine / besoins (exemple) :



env

Copier le code

POSTGRES\_DB=sdid\_db

POSTGRES\_USER=sdid\_user

POSTGRES\_PASSWORD=sdid\_password

DB\_HOST=db

DB\_PORT=5432

