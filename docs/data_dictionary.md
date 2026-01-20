# Dictionnaire de données

## Table: power_consumption
Rôle : stocker les mesures de consommation électrique (série temporelle).

| Colonne | Type SQL | NULL ? | Description |
|--------|----------|--------|-------------|
| id | BIGSERIAL (PK) | NON | Identifiant interne |
| ts | TIMESTAMP | NON | Date+heure de mesure |
| global_active_power_kw | DOUBLE PRECISION | OUI | Puissance active (kW) |
| global_reactive_power_kw | DOUBLE PRECISION | OUI | Puissance réactive (kW) |
| voltage_v | DOUBLE PRECISION | OUI | Tension (V) |
| global_intensity_a | DOUBLE PRECISION | OUI | Intensité (A) |
| sub_metering_1_wh | DOUBLE PRECISION | OUI | Sous-comptage 1 (Wh) |
| sub_metering_2_wh | DOUBLE PRECISION | OUI | Sous-comptage 2 (Wh) |
| sub_metering_3_wh | DOUBLE PRECISION | OUI | Sous-comptage 3 (Wh) |
| is_anomaly | BOOLEAN | NON | Valeur TRUE si anomalie détectée |
| anomaly_score | DOUBLE PRECISION | OUI | Score d’anomalie |
| scored_at | TIMESTAMP | OUI | Date du scoring |
| inserted_at | TIMESTAMP | NON | Date insertion (par ingestion) |
