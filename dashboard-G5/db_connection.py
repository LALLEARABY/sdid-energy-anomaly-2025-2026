import psycopg2
from psycopg2.extras import RealDictCursor  # ← NOUVEAU : Import pour curseur dictionnaire
import os


def get_connection():
    """
    Connexion à PostgreSQL - Compatible avec Docker et local
    Les variables d'environnement sont définies dans docker-compose.yaml ou .env

    AMÉLIORATIONS :
    - Import RealDictCursor pour utilisation dans app.py
    - Paramètres flexibles via variables d'environnement
    - Gestion robuste des erreurs
    """
    try:
        # Paramètres de connexion (identiques à ceux de G2)
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),  # "db" pour Docker, "127.0.0.1" pour local
            port=os.getenv("DB_PORT", "5432"),  # Ton port PostgreSQL
            dbname=os.getenv("DB_NAME", "sdid_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "23654"),
            connect_timeout=5
        )
    except psycopg2.OperationalError as e:
        raise RuntimeError(f"❌ Impossible de se connecter à PostgreSQL : {e}")


# Test de connexion (exécutable directement)
if __name__ == "__main__":
    print("🔗 Test de connexion à PostgreSQL...")
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)  # ← NOUVEAU : Test avec RealDictCursor

        # Test simple : compter les enregistrements
        cur.execute("SELECT COUNT(*) as total FROM power_consumption;")
        result = cur.fetchone()
        count = result['total']  # ← Utilisation du nom de colonne

        print(f"✅ Connexion réussie !")
        print(f"📊 Nombre d'enregistrements dans la base : {count}")

        # Test bonus : Vérifier les anomalies récentes
        cur.execute("""
            SELECT COUNT(*) as recent_anomalies 
            FROM power_consumption 
            WHERE is_anomaly = TRUE 
              AND scored_at >= NOW() - INTERVAL '10 minutes'
        """)
        anomalies = cur.fetchone()
        print(f"⚠️  Anomalies récentes (10 dernières minutes) : {anomalies['recent_anomalies']}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erreur : {e}")