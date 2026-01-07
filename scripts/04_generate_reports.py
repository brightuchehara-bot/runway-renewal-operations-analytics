import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

OUT_DIR = "reports/generated"
os.makedirs(OUT_DIR, exist_ok=True)

def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, engine)

def save_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(OUT_DIR, filename)
    df.to_csv(path, index=False)
    print("Wrote", path)

def line_chart(df: pd.DataFrame, x: str, y: str, title: str, filename: str):
    plt.figure()
    plt.plot(df[x], df[y])
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print("Wrote", path)

def main():
    # Daily trends (overall)
    trend = q("""
        SELECT
          log_date,
          AVG(avg_equipment_utilization) AS equipment_util,
          AVG(avg_crew_utilization) AS crew_util,
          AVG(avg_production_adherence) AS prod_adherence
        FROM kpi_zone_daily_summary
        GROUP BY log_date
        ORDER BY log_date;
    """)
    save_csv(trend, "daily_kpi_trends.csv")

    # Worst-performing zones (by production adherence)
    worst_zones = q("""
        SELECT
          zone_id,
          AVG(avg_production_adherence) AS avg_prod_adherence,
          AVG(avg_equipment_utilization) AS avg_equipment_util,
          AVG(avg_crew_utilization) AS avg_crew_util
        FROM kpi_zone_daily_summary
        GROUP BY zone_id
        ORDER BY avg_prod_adherence ASC
        LIMIT 5;
    """)
    save_csv(worst_zones, "worst_zones.csv")

    # Biggest negative variance days (production)
    worst_days = q("""
        SELECT
          log_date,
          SUM(total_variance_qty) AS total_variance_qty
        FROM kpi_zone_daily_summary
        GROUP BY log_date
        ORDER BY total_variance_qty ASC
        LIMIT 5;
    """)
    save_csv(worst_days, "worst_days_by_variance.csv")

    # Charts
    line_chart(trend, "log_date", "equipment_util",
               "Avg Equipment Utilization (Daily)", "equipment_util_trend.png")
    line_chart(trend, "log_date", "crew_util",
               "Avg Crew Utilization (Daily)", "crew_util_trend.png")
    line_chart(trend, "log_date", "prod_adherence",
               "Avg Production Adherence (Daily)", "production_adherence_trend.png")

    # Executive summary markdown
    eq = float(trend["equipment_util"].mean())
    cr = float(trend["crew_util"].mean())
    pr = float(trend["prod_adherence"].mean())

    md = []
    md.append("# Runway Renewal Operations Analytics – Executive Summary\n")
    md.append("Generated from MySQL KPI views + Python reporting pipeline.\n")
    md.append("## KPI Averages (Overall)\n")
    md.append(f"- Equipment utilization: **{eq:.1%}**\n")
    md.append(f"- Crew utilization: **{cr:.1%}**\n")
    md.append(f"- Production adherence: **{pr:.1%}**\n")

    md.append("\n## Focus Areas\n")
    md.append("### Worst zones (lowest production adherence)\n")
    md.append(worst_zones.to_markdown(index=False))
    md.append("\n\n### Worst days (largest negative production variance)\n")
    md.append(worst_days.to_markdown(index=False))

    out_md = os.path.join(OUT_DIR, "EXEC_SUMMARY.md")
    with open(out_md, "w") as f:
        f.write("\n".join(md))
    print("Wrote", out_md)

if __name__ == "__main__":
    main()
