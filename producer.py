import time
import pandas as pd
from db import get_connection

TXT_PATH = "data/household_power_consumption.txt"
SLEEP_SECONDS = 2


def clean_float(value):
    """Convertit ?, NaN ou valeurs invalides en None (NULL SQL)"""
    if value == "?" or pd.isna(value):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main():
    print("📡 Producer G2 démarré (source .txt)")

    # Lecture du fichier TXT (séparateur ;)
    df = pd.read_csv(
        TXT_PATH,
        sep=";",
        low_memory=False
    )

    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        try:
            # Construction du timestamp → ts (MATCH SQL)
            ts = pd.to_datetime(
                row["Date"] + " " + row["Time"],
                format="%d/%m/%Y %H:%M:%S",
                errors="coerce"
            )

            if pd.isna(ts):
                continue

            # INSERT STRICTEMENT ALIGNÉ AVEC LA TABLE SQL
            cur.execute("""
                INSERT INTO power_consumption (
                    ts,
                    global_active_power_kw,
                    global_reactive_power_kw,
                    voltage_v,
                    global_intensity_a,
                    sub_metering_1_wh,
                    sub_metering_2_wh,
                    sub_metering_3_wh
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                ts,
                clean_float(row["Global_active_power"]),
                clean_float(row["Global_reactive_power"]),
                clean_float(row["Voltage"]),
                clean_float(row["Global_intensity"]),
                clean_float(row["Sub_metering_1"]),
                clean_float(row["Sub_metering_2"]),
                clean_float(row["Sub_metering_3"]),
            ))

            conn.commit()
            print(f"✅ Inserted @ {ts}")
            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            conn.rollback()
            print("❌ Erreur insertion :", e)

    cur.close()
    conn.close()
    print("🛑 Producer terminé")


if __name__ == "__main__":
    main()
