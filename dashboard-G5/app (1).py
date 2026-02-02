from flask import Flask, render_template, jsonify
from db_connection import get_connection
import psycopg2
from psycopg2.extras import RealDictCursor  # ← NOUVEAU : Pour code plus propre
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    """
    Page principale du dashboard
    """
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    """
    API : Renvoie les dernières données au format JSON
    AMÉLIORÉ : 100 mesures au lieu de 50 + RealDictCursor
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)  # ← NOUVEAU : Curseur dictionnaire

        query = """
            SELECT 
                ts,
                global_active_power_kw,
                global_reactive_power_kw,
                voltage_v,
                global_intensity_a,
                sub_metering_1_wh,
                sub_metering_2_wh,
                sub_metering_3_wh,
                is_anomaly,
                anomaly_score
            FROM power_consumption
            ORDER BY ts DESC
            LIMIT 100
        """
        # ↑ AMÉLIORÉ : 100 mesures au lieu de 50 pour graphiques plus détaillés

        cur.execute(query)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        # ↓ AMÉLIORÉ : Utilisation des noms de colonnes au lieu des index
        data = []
        for row in rows:
            data.append({
                'timestamp': row['ts'].isoformat() if row['ts'] else None,
                'global_active_power': float(row['global_active_power_kw']) if row['global_active_power_kw'] is not None else None,
                'global_reactive_power': float(row['global_reactive_power_kw']) if row['global_reactive_power_kw'] is not None else None,
                'voltage': float(row['voltage_v']) if row['voltage_v'] is not None else None,
                'global_intensity': float(row['global_intensity_a']) if row['global_intensity_a'] is not None else None,
                'sub_metering_1': float(row['sub_metering_1_wh']) if row['sub_metering_1_wh'] is not None else None,
                'sub_metering_2': float(row['sub_metering_2_wh']) if row['sub_metering_2_wh'] is not None else None,
                'sub_metering_3': float(row['sub_metering_3_wh']) if row['sub_metering_3_wh'] is not None else None,
                'is_anomaly': bool(row['is_anomaly']) if row['is_anomaly'] is not None else False,
                'anomaly_score': float(row['anomaly_score']) if row['anomaly_score'] else None
            })

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        print(f"Erreur SQL : {e}")  # Ceci te dira précisément pourquoi tu as une 500
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """
    API : Renvoie les statistiques globales
    AMÉLIORÉ : RealDictCursor pour code plus lisible
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)  # ← NOUVEAU

        query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN is_anomaly = TRUE THEN 1 END) as total_anomalies,
                AVG(global_active_power_kw) as avg_power,
                MAX(global_active_power_kw) as max_power,
                AVG(voltage_v) as avg_voltage
            FROM power_consumption
        """

        cur.execute(query)
        stats = cur.fetchone()

        cur.close()
        conn.close()

        # ↓ AMÉLIORÉ : Utilisation des noms de colonnes
        return jsonify({
            'success': True,
            'stats': {
                'total_records': int(stats['total_records']) if stats['total_records'] else 0,
                'total_anomalies': int(stats['total_anomalies']) if stats['total_anomalies'] else 0,
                'avg_power': float(stats['avg_power']) if stats['avg_power'] else 0.0,
                'max_power': float(stats['max_power']) if stats['max_power'] else 0.0,
                'avg_voltage': float(stats['avg_voltage']) if stats['avg_voltage'] else 0.0
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/anomalies')
def api_anomalies():
    """
    API : Renvoie uniquement les anomalies détectées RÉCEMMENT
    AMÉLIORÉ : Logique scored_at pour éviter les vieilles anomalies du dataset
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)  # ← NOUVEAU

        # ↓ AMÉLIORÉ : Filtre sur scored_at pour anomalies récentes uniquement
        query = """
            SELECT 
                ts,
                global_active_power_kw,
                voltage_v,
                anomaly_score,
                scored_at
            FROM power_consumption
            WHERE is_anomaly = TRUE
              AND scored_at IS NOT NULL
              AND scored_at >= NOW() - INTERVAL '10 minutes'
            ORDER BY scored_at DESC
            LIMIT 20
        """
        # ↑ LOGIQUE INTELLIGENTE :
        # - scored_at >= NOW() - 10 minutes : Seulement anomalies récentes (pas historiques)
        # - ORDER BY scored_at : Trier par moment de détection (pas timestamp dataset)
        # - Évite d'afficher les vieilles anomalies du dataset UCI 2006

        cur.execute(query)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        # ↓ AMÉLIORÉ : Utilisation des noms de colonnes
        anomalies = []
        for row in rows:
            anomalies.append({
                'timestamp': row['ts'].isoformat() if row['ts'] else None,
                'power': float(row['global_active_power_kw']) if row['global_active_power_kw'] is not None else None,
                'voltage': float(row['voltage_v']) if row['voltage_v'] is not None else None,
                'score': float(row['anomaly_score']) if row['anomaly_score'] else None,
                'scored_at': row['scored_at'].isoformat() if row['scored_at'] else None
            })

        return jsonify({'success': True, 'anomalies': anomalies})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/current_alert')
def api_current_alert():
    """
    API BONUS : Vérifie s'il y a une alerte ACTIVE en ce moment
    NOUVEAU : Route additionnelle pour alertes temps réel ultra-précises
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Chercher une anomalie détectée dans la dernière minute
        query = """
            SELECT 
                ts,
                global_active_power_kw,
                voltage_v,
                global_intensity_a,
                anomaly_score,
                scored_at,
            FROM power_consumption
            WHERE is_anomaly = TRUE
              AND scored_at >= NOW() - INTERVAL '1 minute'
            ORDER BY scored_at DESC
            LIMIT 1
        """

        cur.execute(query)
        alert = cur.fetchone()

        cur.close()
        conn.close()

        if alert:
            return jsonify({
                'has_alert': True,
                'timestamp': alert['ts'].isoformat(),
                'power': float(alert['global_active_power_kw']) if alert['global_active_power_kw'] else None,
                'voltage': float(alert['voltage_v']) if alert['voltage_v'] else None,
                'intensity': float(alert['global_intensity_a']) if alert['global_intensity_a'] else None,
                'score': float(alert['anomaly_score']) if alert['anomaly_score'] else None,
                'scored_at': alert['scored_at'].isoformat()
            })
        else:
            return jsonify({'has_alert': False})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Dashboard Flask démarré sur http://0.0.0.0:5000")
    print("✨ Version améliorée avec RealDictCursor + logique scored_at")
    app.run(host='0.0.0.0', port=5000, debug=True)