-- Calculate daily equipment utilization rates

SELECT
    equipment_id,
    work_date,
    SUM(hours_used) AS total_hours_used,
    SUM(hours_available) AS total_hours_available,
    ROUND(
        SUM(hours_used) / NULLIF(SUM(hours_available), 0),
        2
    ) AS utilization_rate
FROM equipment_logs
GROUP BY equipment_id, work_date
ORDER BY work_date, utilization_rate DESC;
