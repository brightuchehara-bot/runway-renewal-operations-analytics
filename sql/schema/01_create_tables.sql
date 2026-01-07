USE runway_ops;

CREATE TABLE IF NOT EXISTS equipment (
  equipment_id VARCHAR(50) PRIMARY KEY,
  equipment_type VARCHAR(50) NOT NULL,
  manufacturer VARCHAR(50),
  model VARCHAR(50),
  active_flag TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS crew (
  crew_id VARCHAR(50) PRIMARY KEY,
  crew_name VARCHAR(100),
  trade VARCHAR(50),
  contractor VARCHAR(100),
  active_flag TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS work_zone (
  zone_id VARCHAR(50) PRIMARY KEY,
  zone_name VARCHAR(100),
  runway_phase VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS equipment_log (
  log_date DATE NOT NULL,
  equipment_id VARCHAR(50) NOT NULL,
  zone_id VARCHAR(50),
  scheduled_hours DECIMAL(6,2) NOT NULL,
  operating_hours DECIMAL(6,2) NOT NULL,
  downtime_hours DECIMAL(6,2) NOT NULL,
  downtime_reason VARCHAR(200),
  PRIMARY KEY (log_date, equipment_id),
  FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
  FOREIGN KEY (zone_id) REFERENCES work_zone(zone_id)
);

CREATE TABLE IF NOT EXISTS crew_log (
  log_date DATE NOT NULL,
  crew_id VARCHAR(50) NOT NULL,
  zone_id VARCHAR(50),
  scheduled_hours DECIMAL(6,2) NOT NULL,
  worked_hours DECIMAL(6,2) NOT NULL,
  idle_hours DECIMAL(6,2) NOT NULL,
  notes VARCHAR(200),
  PRIMARY KEY (log_date, crew_id),
  FOREIGN KEY (crew_id) REFERENCES crew(crew_id),
  FOREIGN KEY (zone_id) REFERENCES work_zone(zone_id)
);

CREATE TABLE IF NOT EXISTS production_log (
  log_date DATE NOT NULL,
  zone_id VARCHAR(50) NOT NULL,
  task_type VARCHAR(50) NOT NULL,
  planned_qty DECIMAL(10,2) NOT NULL,
  actual_qty DECIMAL(10,2) NOT NULL,
  uom VARCHAR(20) NOT NULL,
  PRIMARY KEY (log_date, zone_id, task_type),
  FOREIGN KEY (zone_id) REFERENCES work_zone(zone_id)
);
