import pandas as pd
from common.db import get_connection

QUERY = """
SELECT
    global_active_power_kw,
    voltage_v,
    global_intensity_a
FROM power_consumption
WHERE global_active_power_kw IS NOT NULL
  AND voltage_v IS NOT NULL
  AND global_intensity_a IS NOT NULL
LIMIT 100000;
"""

def fetch_historical_data():
    print("Chargement des données historiques depuis PostgreSQL")

    conn = get_connection()
    df = pd.read_sql(QUERY, conn)
    conn.close()

    return df
