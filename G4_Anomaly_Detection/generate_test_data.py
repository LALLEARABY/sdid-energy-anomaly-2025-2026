import psycopg2
import numpy as np
from datetime import datetime, timedelta

# Connexion
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="power_consumption_db",
    user="postgres",
    password="1234"
)
cur = conn.cursor()

# Génère 1000 enregistrements
start_time = datetime.now() - timedelta(days=30)
for i in range(1000):
    ts = start_time + timedelta(minutes=i)
    cur.execute("""
        INSERT INTO power_consumption 
        (ts, global_active_power_kw, voltage_v, global_intensity_a) 
        VALUES (%s, %s, %s, %s)
    """, (ts, np.random.uniform(1, 5), np.random.uniform(220, 240), np.random.uniform(4, 20)))

conn.commit()
cur.close()
conn.close()
print("✓ 1000 enregistrements insérés!")
