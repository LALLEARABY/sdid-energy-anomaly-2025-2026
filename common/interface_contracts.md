# Contrats d’interface entre modules

## Source de vérité
Toutes les données passent par PostgreSQL (table `power_consumption`).

---

## Module Ingestion (G2)
**Écrit dans la BD :**
- INSERT dans `power_consumption`

**Règles :**
- Construire `ts` à partir des champs Date + Time
- Remplacer "?" par NULL
- Pause entre insertions (ex: 2 secondes si demandé)

---

## Module Mining / Patterns (G3)
**Lit dans la BD :**
- colonnes numériques + ts

**Produit pour les autres modules :**
- paramètres de normalisation + axes/paramètres (format fichier partagé dans le repo)

---

## Module Anomaly Engine (G4)
**Lit :**
- lignes non scorées (`scored_at IS NULL`)

**Écrit :**
- UPDATE `is_anomaly`, `anomaly_score`, `scored_at`

---

## Module Dashboard (G5)
**Lit :**
- dernières valeurs
- anomalies (`is_anomaly = TRUE`)
- séries temporelles

**Affiche :**
- graphiques temps réel
- alertes anomalies
