USE runway_ops;

-- 1) Equipment utilization: operating / scheduled
CREATE OR REPLACE VIEW kpi_equipment_utilization_daily AS
SELECT
  log_date,
  zone_id,
  equipment_id,
  scheduled_hours,
  operating_hours,
  downtime_hours,
  downtime_reason,
  CASE 
    WHEN scheduled_hours = 0 THEN NULL
    ELSE ROUND(operating_hours / scheduled_hours, 3)
  END AS utilization_rate
FROM equipment_log;

-- 2) Crew utilization: worked / scheduled
CREATE OR REPLACE VIEW kpi_crew_utilization_daily AS
SELECT
  log_date,
  zone_id,
  crew_id,
  scheduled_hours,
  worked_hours,
  idle_hours,
  notes,
  CASE 
    WHEN scheduled_hours = 0 THEN NULL
    ELSE ROUND(worked_hours / scheduled_hours, 3)
  END AS crew_utilization_rate
FROM crew_log;

-- 3) Production adherence: actual / planned
CREATE OR REPLACE VIEW kpi_production_adherence_daily AS
SELECT
  log_date,
  zone_id,
  task_type,
  planned_qty,
  actual_qty,
  uom,
  CASE
    WHEN planned_qty = 0 THEN NULL
    ELSE ROUND(actual_qty / planned_qty, 3)
  END AS adherence_rate,
  ROUND(actual_qty - planned_qty, 2) AS variance_qty
FROM production_log;

-- 4) Zone-level rollups (daily) for fast reporting
CREATE OR REPLACE VIEW kpi_zone_daily_summary AS
SELECT
  d.log_date,
  d.zone_id,

  -- equipment
  ROUND(AVG(e.utilization_rate), 3) AS avg_equipment_utilization,
  SUM(e.operating_hours) AS total_operating_hours,
  SUM(e.scheduled_hours) AS total_scheduled_hours,

  -- crew
  ROUND(AVG(c.crew_utilization_rate), 3) AS avg_crew_utilization,
  SUM(c.worked_hours) AS total_worked_hours,
  SUM(c.scheduled_hours) AS total_crew_scheduled_hours,

  -- production
  ROUND(AVG(p.adherence_rate), 3) AS avg_production_adherence,
  SUM(p.planned_qty) AS total_planned_qty,
  SUM(p.actual_qty) AS total_actual_qty,
  SUM(p.variance_qty) AS total_variance_qty

FROM (SELECT DISTINCT log_date, zone_id FROM production_log) d
LEFT JOIN kpi_equipment_utilization_daily e
  ON e.log_date = d.log_date AND e.zone_id = d.zone_id
LEFT JOIN kpi_crew_utilization_daily c
  ON c.log_date = d.log_date AND c.zone_id = d.zone_id
LEFT JOIN kpi_production_adherence_daily p
  ON p.log_date = d.log_date AND p.zone_id = d.zone_id
GROUP BY d.log_date, d.zone_id;
