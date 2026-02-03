import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="sdid_postgres",
    port=5432,
    database="sdid_db",
    user="sdid_user",
    password="sdid_password"
)

query_baseline = """
SELECT *
FROM power_consumption
WHERE ts BETWEEN '2006-12-01' AND '2006-12-31'
"""

query_current = """
SELECT *
FROM power_consumption
WHERE ts BETWEEN '2007-05-01' AND '2007-05-31'
"""

baseline = pd.read_sql(query_baseline, conn)
current = pd.read_sql(query_current, conn)

baseline.to_csv("data/baseline_dec_2006.csv", index=False)
current.to_csv("data/current_data.csv", index=False)

print("Extraction terminée avec succès")
