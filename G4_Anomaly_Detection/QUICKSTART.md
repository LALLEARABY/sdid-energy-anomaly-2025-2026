# 🚀 Guide de Démarrage Rapide - G4

## Configuration en 5 minutes

### Étape 1 : Installation (2 min)

```bash
# Cloner le dépôt (si pas déjà fait)
git clone <url-du-repo>
cd G4_Anomaly_Detection

# Installer les dépendances
pip install -r requirements.txt
# OU avec make
make install
```

### Étape 2 : Configuration (1 min)

```bash
# Créer le fichier de configuration
cp .env.example .env

# Éditer avec vos informations
nano .env  # ou vim, code, etc.
```

**Modifier ces valeurs dans `.env`** :
```
DB_HOST=localhost          # Adresse PostgreSQL (fournie par G2)
DB_PORT=5432
DB_NAME=power_consumption_db
DB_USER=votre_username     # À modifier
DB_PASSWORD=votre_password # À modifier
```

### Étape 3 : Récupérer les fichiers G3 (1 min)

```bash
# Copier les fichiers depuis le dépôt G3
cp ../G3_Data_Mining/models/scaler.pkl models/g3_scaler.pkl
cp ../G3_Data_Mining/models/pca.pkl models/g3_pca.pkl
```

### Étape 4 : Vérification (1 min)

```bash
# Tester la configuration
python quickstart.py
# OU avec make
make setup
```

Vous devriez voir :
```
✓ .env file found
✓ All dependencies installed
✓ Database connection successful
✓ Preprocessor working correctly
```

---

## Utilisation quotidienne

### Entraîner le modèle

```bash
python train_model.py
# OU
make train
```

**Durée** : 2-5 secondes  
**Sortie** : `models/anomaly_detector.pkl`

### Lancer le scoring en temps réel

```bash
# Mode continu (production)
python src/scoring_engine.py --mode continuous --interval 60

# Mode test (une seule fois)
python src/scoring_engine.py --mode once

# Avec make
make score       # continu
make score-once  # une fois
```

### Calculer le ROI

```bash
python src/roi_calculator.py
# OU
make roi
```

---

## Commandes utiles

```bash
# Voir l'aide
make help

# Tester la connexion DB
make db-test

# Voir les stats DB
make db-stats

# Info sur le modèle
make model-info

# Nettoyer les fichiers temporaires
make clean

# Lancer Jupyter
make notebook
```

---

## Résolution rapide des problèmes

### ❌ "Failed to connect to database"
```bash
# Vérifier que PostgreSQL tourne
sudo systemctl status postgresql

# Vérifier les credentials dans .env
cat .env | grep DB_
```

### ❌ "G3 parameters not found"
```bash
# Vérifier les fichiers G3
ls -l models/g3_*.pkl

# Si absents, contacter G3 ou utiliser les params par défaut
# (le système créera des params par défaut automatiquement)
```

### ❌ "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

---

## Workflow complet (première fois)

```bash
# 1. Installation
make install

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos credentials

# 3. Vérification
make setup

# 4. Entraînement
make train

# 5. Scoring
make score
```

**Temps total** : ~10 minutes

---

## Intégration Git

```bash
# Créer une branche pour G4
git checkout -b g4-anomaly-detection

# Ajouter vos modifications
git add .
git commit -m "G4: Initial implementation of anomaly detection"

# Pousser vers GitHub
git push origin g4-anomaly-detection

# Créer une Pull Request vers main
```

---

## Fichiers importants

| Fichier | Description | Action requise |
|---------|-------------|----------------|
| `.env` | Configuration DB | ✏️ À créer et modifier |
| `models/g3_scaler.pkl` | Scaler du G3 | 📥 À récupérer depuis G3 |
| `models/g3_pca.pkl` | PCA du G3 | 📥 À récupérer depuis G3 |
| `models/anomaly_detector.pkl` | Votre modèle | ✅ Créé par `make train` |

---

## Checklist avant de pusher sur Git

- [ ] `.env` est dans `.gitignore` (ne PAS commit les passwords !)
- [ ] Code testé localement
- [ ] README mis à jour si nécessaire
- [ ] Mini-rapport technique complété
- [ ] Modèle entraîné et fonctionnel
- [ ] Tests passent (`make test`)

---

## Support

**Questions** : Canal Slack `#g4-anomalies`  
**Issues GitHub** : https://github.com/[votre-repo]/issues  
**Documentation** : Voir `README.md` complet

---

**Bon courage ! 🚀**
