import psycopg2

print("🔍 Test de connexion PostgreSQL depuis Python...")

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        dbname="sdid_db",
        user="sdid_user",
        password="sdid_password",
        connect_timeout=5
    )
    print("✅ Connexion PostgreSQL OK depuis Python")
    conn.close()
except Exception as e:
    print("❌ Connexion échouée :", e)
