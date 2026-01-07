import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(7)

OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

# ---- dimensions ----
equipment = pd.DataFrame([
    {"equipment_id": f"EQ-{i:03d}",
     "equipment_type": random.choice(["MILLER", "PAVER", "ROLLER", "SWEEPER", "DUMP_TRUCK"]),
     "manufacturer": random.choice(["CAT", "WIRTGEN", "VOLVO", "DEERE"]),
     "model": random.choice(["A1", "B2", "C3", "D4"]),
     "active_flag": 1}
    for i in range(1, 16)
])

crew = pd.DataFrame([
    {"crew_id": f"CR-{i:03d}",
     "crew_name": random.choice(["Alpha", "Bravo", "Charlie", "Delta", "Echo"]) + f" Crew {i}",
     "trade": random.choice(["MILLING", "PAVING", "STRIPING", "QC", "LOGISTICS"]),
     "contractor": random.choice(["PrimeCo", "BuildRight", "RunwayWorks"]),
     "active_flag": 1}
    for i in range(1, 11)
])

zones = pd.DataFrame([
    {"zone_id": f"Z-{i:02d}",
     "zone_name": f"Work Zone {i}",
     "runway_phase": random.choice(["PHASE_1", "PHASE_2", "PHASE_3"])}
    for i in range(1, 6)
])

# ---- facts ----
start = date(2026, 1, 1)
days = 21
dates = [start + timedelta(days=i) for i in range(days)]

def clamp(x, lo=0.0):
    return max(lo, x)

equipment_rows = []
for d in dates:
    for _, e in equipment.sample(10, random_state=random.randint(1, 9999)).iterrows():
        sched = random.choice([8, 10, 12])
        op = clamp(random.gauss(mu=sched * 0.78, sigma=1.2))
        down = clamp(sched - op)
        equipment_rows.append({
            "log_date": d.isoformat(),
            "equipment_id": e["equipment_id"],
            "zone_id": random.choice(zones["zone_id"].tolist()),
            "scheduled_hours": round(sched, 2),
            "operating_hours": round(op, 2),
            "downtime_hours": round(down, 2),
            "downtime_reason": random.choice(["MECH", "WEATHER", "WAITING_ON_MATERIAL", "SHIFT_CHANGE", "NONE"])
        })

crew_rows = []
for d in dates:
    for _, c in crew.sample(7, random_state=random.randint(1, 9999)).iterrows():
        sched = random.choice([8, 10, 12])
        worked = clamp(random.gauss(mu=sched * 0.83, sigma=1.1))
        idle = clamp(sched - worked)
        crew_rows.append({
            "log_date": d.isoformat(),
            "crew_id": c["crew_id"],
            "zone_id": random.choice(zones["zone_id"].tolist()),
            "scheduled_hours": round(sched, 2),
            "worked_hours": round(worked, 2),
            "idle_hours": round(idle, 2),
            "notes": random.choice(["", "handoff_delay", "material_wait", "rework", "normal"])
        })

tasks = ["MILLING", "PAVING", "STRIPING"]
uoms = {"MILLING": "sqft", "PAVING": "tons", "STRIPING": "linear_ft"}

prod_rows = []
for d in dates:
    for z in zones["zone_id"]:
        for t in tasks:
            planned = random.choice([1000, 1200, 1500, 1800])
            actual = clamp(random.gauss(mu=planned * 0.92, sigma=120))
            prod_rows.append({
                "log_date": d.isoformat(),
                "zone_id": z,
                "task_type": t,
                "planned_qty": round(planned, 2),
                "actual_qty": round(actual, 2),
                "uom": uoms[t]
            })

# write CSVs
equipment.to_csv(os.path.join(OUT_DIR, "equipment.csv"), index=False)
crew.to_csv(os.path.join(OUT_DIR, "crew.csv"), index=False)
zones.to_csv(os.path.join(OUT_DIR, "work_zone.csv"), index=False)
pd.DataFrame(equipment_rows).to_csv(os.path.join(OUT_DIR, "equipment_log.csv"), index=False)
pd.DataFrame(crew_rows).to_csv(os.path.join(OUT_DIR, "crew_log.csv"), index=False)
pd.DataFrame(prod_rows).to_csv(os.path.join(OUT_DIR, "production_log.csv"), index=False)

print("Wrote sample CSVs to data/raw/")
