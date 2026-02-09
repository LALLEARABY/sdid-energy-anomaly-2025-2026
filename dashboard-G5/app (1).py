import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, session, request, redirect, url_for, render_template_string
from functools import wraps
from datetime import datetime

# استيراد وظيفة الاتصال (تأكد أن ملف db_connection.py موجود في نفس المجلد)
try:
    from db_connection import get_connection
except ImportError:
    # وظيفة احتياطية في حال لم يتم العثور sur le fichier
    def get_connection():
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            dbname=os.getenv('DB_NAME', 'sdid_db'),
            user=os.getenv('DB_USER', 'sdid_user'),
            password=os.getenv('DB_PASSWORD', 'sdid_password')
        )

app = Flask(__name__)

# ==========================================
# 🔐 1. CONFIGURATION SÉCURITÉ & SECRETS
# ==========================================
# قراءة المفاتيح من ملف .env (Docker Environment)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_123')
ADMIN_USER = os.getenv('DASHBOARD_USER', 'admin')
ADMIN_PASS = os.getenv('DASHBOARD_PASS', 'admin')

# القالب البسيط لصفحة تسجيل الدخول (HTML intégré)
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - SDID Energy Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #0e1117; color: white; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #1e2130; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; width: 320px; border: 1px solid #2d3342; }
        h2 { color: #00d4ff; margin-bottom: 20px; letter-spacing: 1px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #3d4457; background: #262b3d; color: white; box-sizing: border-box; }
        input:focus { outline: none; border-color: #00d4ff; }
        button { width: 100%; padding: 12px; background-color: #00d4ff; color: #0e1117; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin-top: 15px; transition: 0.3s; }
        button:hover { background-color: #00a0c0; transform: translateY(-2px); }
        .error { color: #ff4b4b; font-size: 0.9em; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>⚡ SDID SECURE</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Identifiant" required autocomplete="off">
            <input type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit">CONNEXION</button>
        </form>
        {% if error %}
            <div class="error">⚠️ {{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

# Décorateur pour protéger les routes (Middleware)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 🚪 2. ROUTES D'AUTHENTIFICATION
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_input = request.form['username']
        pass_input = request.form['password']
        
        # Vérification des identifiants (variables d'environnement)
        if user_input == ADMIN_USER and pass_input == ADMIN_PASS:
            session['logged_in'] = True
            session['user'] = user_input
            return redirect(url_for('index'))
        else:
            error = 'Identifiants invalides. Accès refusé.'
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# 📊 3. ROUTES PRINCIPALES (PROTÉGÉES)
# ==========================================

@app.route('/')
@login_required  # 🔒 Protection active
def index():
    """ Page principale du dashboard """
    return render_template('index.html')

# ==========================================
# 🔌 4. APIS DE DONNÉES (PROTÉGÉES)
# ==========================================

@app.route('/api/data')
@login_required  # 🔒 Protection active
def api_data():
    """ API : Renvoie les 100 dernières mesures """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT ts, global_active_power_kw, global_reactive_power_kw, voltage_v, 
                   global_intensity_a, sub_metering_1_wh, sub_metering_2_wh, sub_metering_3_wh, 
                   is_anomaly, anomaly_score
            FROM power_consumption
            ORDER BY ts DESC LIMIT 100
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
@login_required  # 🔒 Protection active
def api_stats():
    """ API : Statistiques globales """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT COUNT(*) as total_records,
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
@login_required  # 🔒 Protection active
def api_anomalies():
    """ API : Anomalies récentes (basées sur scored_at) """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Filtre sur les anomalies détectées dans les 10 dernières minutes
        query = """
            SELECT ts, global_active_power_kw, voltage_v, anomaly_score, scored_at
            FROM power_consumption
            WHERE is_anomaly = TRUE 
              AND scored_at IS NOT NULL
            ORDER BY scored_at DESC LIMIT 20
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

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
@login_required  # 🔒 Protection active
def api_current_alert():
    """ API : Alerte Temps Réel (Dernière minute) """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT ts, global_active_power_kw, voltage_v, global_intensity_a, anomaly_score, scored_at
            FROM power_consumption
            WHERE is_anomaly = TRUE 
              AND scored_at >= NOW() - INTERVAL '1 minute'
            ORDER BY scored_at DESC LIMIT 1
        """
        cur.execute(query)
        alert = cur.fetchone()
        cur.close()
        conn.close()

        if alert:
            return jsonify({
                'has_alert': True,
                'timestamp': alert['ts'].isoformat(),
                'power': float(alert['global_active_power_kw']),
                'voltage': float(alert['voltage_v']),
                'intensity': float(alert['global_intensity_a']),
                'score': float(alert['anomaly_score']),
                'scored_at': alert['scored_at'].isoformat()
            })
        else:
            return jsonify({'has_alert': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print(f"🚀 Dashboard Sécurisé démarré sur http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)