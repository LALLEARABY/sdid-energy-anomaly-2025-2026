# 🚀 SDID Energy Monitor - Dashboard Web Interactif (G5)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Dashboard web interactif pour la surveillance énergétique en temps réel et la détection d'anomalies.

**Projet SDID 2025/2026** - Groupe G5

---

## 📊 Aperçu

Le dashboard SDID Energy Monitor est l'interface finale du système de surveillance énergétique. Il permet de :

- ✅ Visualiser la consommation électrique en temps réel
- ✅ Afficher 4 KPI Cards dynamiques
- ✅ Générer 4 graphiques interactifs Plotly
- ✅ Alerter lors de détection d'anomalies (intégration G4)
- ✅ Mettre à jour automatiquement toutes les 3 secondes

---

## 🎨 Captures d'Écran

### Dashboard Complet
![Dashboard](docs/screenshots/dashboard_complet.png)

### Graphiques Temps Réel
![Graphiques](docs/screenshots/graphiques.png)

### Système d'Alertes
![Alertes](docs/screenshots/alertes.png)

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  PostgreSQL │ ───► │  Flask API   │ ───► │  Dashboard  │
│     (G2)    │      │     (G5)     │      │   Browser   │
└─────────────┘      └──────────────┘      └─────────────┘
       ▲                    │
       │                    ▼
┌─────────────┐      ┌──────────────┐
│   Producer  │      │  Plotly.js   │
│     (G2)    │      │  Bootstrap   │
└─────────────┘      └──────────────┘
```

---

## 🚀 Installation Rapide

### Prérequis

- Python 3.9+
- PostgreSQL 15
- pip

### Étape 1 : Cloner le Projet

```bash
git clone https://github.com/votre-username/Projet_SDID_G5.git
cd Projet_SDID_G5
```

### Étape 2 : Installer les Dépendances

```bash
cd dashboard
pip install -r requirements.txt --break-system-packages
```

### Étape 3 : Configuration

Créer un fichier `.env` dans `dashboard/` :

```env
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=sdid_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

### Étape 4 : Lancer le Dashboard

```bash
python app.py
```

Accès : **http://127.0.0.1:5000**

---

## 🐳 Déploiement Docker

### Avec Docker Compose

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier les services
docker ps

# Voir les logs
docker logs -f sdid_dashboard
```

### Sans Docker Compose

```bash
# Construire l'image
docker build -t sdid-dashboard ./dashboard

# Lancer le conteneur
docker run -d -p 5000:5000 \
  -e DB_HOST=127.0.0.1 \
  -e DB_PORT=5433 \
  --name sdid_dashboard \
  sdid-dashboard
```

---

## 📡 APIs REST

### GET /api/data

Récupère les 100 dernières mesures de consommation.

**Réponse :**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2026-02-01T14:30:00",
      "global_active_power": 1.45,
      "voltage": 239.8,
      "is_anomaly": false,
      "anomaly_score": null
    }
  ]
}
```

### GET /api/stats

Statistiques globales du système.

**Réponse :**
```json
{
  "success": true,
  "stats": {
    "total_records": 15247,
    "total_anomalies": 0,
    "avg_power": 1.45,
    "avg_voltage": 239.8
  }
}
```

### GET /api/anomalies

Liste des anomalies récentes (10 dernières minutes).

**Réponse :**
```json
{
  "success": true,
  "anomalies": [
    {
      "timestamp": "2026-02-01T14:28:00",
      "power": 8.5,
      "voltage": 215.2,
      "score": -2.5,
      "scored_at": "2026-02-01T14:28:05"
    }
  ]
}
```

---

## 🔗 Intégration avec les Autres Groupes

### Groupe G2 : Données

- **Connexion :** PostgreSQL via `psycopg2`
- **Table :** `power_consumption`
- **Dépendance :** Producer doit être actif

### Groupe G4 : Anomalies

- **Champs utilisés :** `is_anomaly`, `anomaly_score`, `scored_at`
- **Logique :** Filtre sur `scored_at >= NOW() - INTERVAL '10 minutes'`
- **Avantage :** Évite les anomalies historiques du dataset UCI

### Groupe G6 : DevOps

- **Livrable :** Dockerfile + docker-compose.yaml
- **Réseau :** `sdid_network`
- **Port :** 5000

---

## 🎨 Technologies Utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Flask | 3.0.0 |
| Base de données | PostgreSQL | 15 |
| Driver DB | psycopg2-binary | 2.9.9 |
| Visualisation | Plotly.js | 5.18.0 |
| Frontend | Bootstrap | 5.3.2 |
| Icônes | Font Awesome | 6.5.1 |
| Conteneurisation | Docker | Latest |

---

## 📂 Structure du Projet

```
dashboard/
├── app.py                 # Application Flask principale
├── db_connection.py       # Connexion PostgreSQL
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Configuration Docker
├── .env                  # Variables d'environnement (ne pas commit)
│
├── templates/
│   └── index.html        # Interface utilisateur
│
└── static/
    ├── css/
    │   └── style.css     # Design Tech-Industrial
    └── js/
        └── dashboard.js  # Logique temps réel
```

---

## 🧪 Tests

### Test Connexion Base de Données

```bash
python db_connection.py
```

**Résultat attendu :**
```
🔗 Test de connexion à PostgreSQL...
✅ Connexion réussie !
📊 Nombre d'enregistrements dans la base : 15247
```

### Test API

```bash
# Avec curl
curl http://127.0.0.1:5000/api/data

# Avec navigateur
# http://127.0.0.1:5000/api/stats
```

---

## 📊 Performances

| Métrique | Valeur Mesurée |
|----------|----------------|
| Temps de chargement initial | 1.2s |
| Temps de réponse API /data | 45ms |
| Fréquence de mise à jour | 3s |
| Mémoire consommée | 85 MB |

---

## 🐛 Dépannage

### Problème : "Connexion refusée"

**Solution :** Vérifiez que PostgreSQL tourne sur le port 5433.

```bash
# Windows
Get-Service -Name "*postgres*"

# Linux/Mac
sudo systemctl status postgresql
```

### Problème : "Aucune donnée affichée"

**Solution :** Vérifiez que le producer G2 insère des données.

```sql
SELECT COUNT(*) FROM power_consumption;
```

### Problème : "Anomalies non affichées"

**Solution :** Vérifiez que G4 scoring engine tourne et que `scored_at` est rempli.

```sql
SELECT * FROM power_consumption 
WHERE is_anomaly = TRUE 
  AND scored_at >= NOW() - INTERVAL '10 minutes';
```

---

## 👥 Contributeurs

**Groupe G5 - Dashboard Web Interactif**

- Matricule : [VOTRE MATRICULE]
- Matricule : [MATRICULE 2]
- Matricule : [MATRICULE 3]

Licence SDID - Janvier 2026

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 📞 Support

Pour toute question ou problème :

- **Issues GitHub :** [Créer une issue](https://github.com/votre-username/Projet_SDID_G5/issues)
- **Email :** votre.email@universite.edu
- **Documentation complète :** [docs/](docs/)

---

## 🎯 Roadmap

- [x] Interface dashboard responsive
- [x] 4 graphiques Plotly interactifs
- [x] Système d'alertes temps réel
- [x] Intégration G4 (anomalies)
- [x] Conteneurisation Docker
- [ ] Tests unitaires
- [ ] Authentification utilisateurs
- [ ] Export de données (CSV/PDF)

---

## 🙏 Remerciements

- **Groupe G2** : Données et infrastructure PostgreSQL
- **Groupe G4** : Détection d'anomalies
- **Groupe G6** : Déploiement et orchestration
- **Professeurs SDID** : Encadrement du projet

---

**Made with ❤️ by Groupe G5 - SDID 2025/2026**
