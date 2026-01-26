import os

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
    "port": os.getenv("POSTGRES_PORT", 5433),
    "dbname": os.getenv("POSTGRES_DB", "sdid_db"),
    "user": os.getenv("POSTGRES_USER", "sdid_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "sdid_password"),
}
