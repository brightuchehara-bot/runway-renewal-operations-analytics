import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

TABLE_FILES = [
    ("equipment", "data/raw/equipment.csv"),
    ("crew", "data/raw/crew.csv"),
    ("work_zone", "data/raw/work_zone.csv"),
    ("equipment_log", "data/raw/equipment_log.csv"),
    ("crew_log", "data/raw/crew_log.csv"),
    ("production_log", "data/raw/production_log.csv"),
]

def truncate_tables():
    # order matters (facts first) due to FK constraints
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for tbl in ["production_log","crew_log","equipment_log","work_zone","crew","equipment"]:
            conn.execute(text(f"TRUNCATE TABLE {tbl};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

def load_csv(table, path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    # strip strings
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # parse dates
    if "log_date" in df.columns:
        df["log_date"] = pd.to_datetime(df["log_date"]).dt.date

    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"Loaded {len(df):,} rows -> {table}")

def main():
    # makes the load idempotent
    truncate_tables()

    # load dims before facts
    for table, path in TABLE_FILES:
        load_csv(table, path)

    print("Done.")

if __name__ == "__main__":
    main()
