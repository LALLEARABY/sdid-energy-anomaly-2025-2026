"""
G4 — Mise à jour des résultats dans la BD
Contrat : UPDATE is_anomaly, anomaly_score, scored_at pour chaque ligne scorée.
"""

from common.db import get_connection
from typing import List
import logging

logger = logging.getLogger("G4")


def update_anomaly_flags(ids: List[int], is_anomaly_list: List[bool], scores_list: List[float]):
    """
    Met à jour les champs de scoring dans power_consumption.

    Args:
        ids: Liste des id des lignes à mettre à jour
        is_anomaly_list: Liste de booléens (True = anomalie)
        scores_list: Liste des scores Isolation Forest
    """
    query = """
        UPDATE power_consumption
        SET is_anomaly   = %s,
            anomaly_score = %s,
            scored_at     = NOW()
        WHERE id = %s
    """

    # Préparer les tuples pour executemany
    params = [
        (bool(is_anom), float(score), int(row_id))
        for row_id, is_anom, score in zip(ids, is_anomaly_list, scores_list)
    ]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(query, params)
        conn.commit()
        logger.info(f"update_anomaly_flags → {len(ids)} lignes mises à jour")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors du UPDATE : {e}")
        raise
    finally:
        cur.close()
        conn.close()
