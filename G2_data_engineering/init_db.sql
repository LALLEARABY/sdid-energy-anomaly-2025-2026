DROP TABLE IF EXISTS power_consumption;

CREATE TABLE power_consumption (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMP NOT NULL,

  global_active_power_kw DOUBLE PRECISION NULL,
  global_reactive_power_kw DOUBLE PRECISION NULL,
  voltage_v DOUBLE PRECISION NULL,
  global_intensity_a DOUBLE PRECISION NULL,
  sub_metering_1_wh DOUBLE PRECISION NULL,
  sub_metering_2_wh DOUBLE PRECISION NULL,
  sub_metering_3_wh DOUBLE PRECISION NULL,

  is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
  anomaly_score DOUBLE PRECISION NULL,
  scored_at TIMESTAMP NULL,

  inserted_at TIMESTAMP NOT NULL DEFAULT NOW()
);
