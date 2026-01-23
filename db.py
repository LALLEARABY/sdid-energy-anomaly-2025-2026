import psycopg2

def get_connection():
    try:
        return psycopg2.connect(
            host="127.0.0.1",
            port=5433,
            dbname="sdid_db",
            user="sdid_user",
            password="sdid_password",
            connect_timeout=5
        )
    except psycopg2.OperationalError as e:
        raise RuntimeError(f"❌ Impossible de se connecter à PostgreSQL : {e}")
