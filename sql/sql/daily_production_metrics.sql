-- Aggregate daily production metrics by work zone

SELECT
    work_date,
    work_zone,
    COUNT(task_id) AS tasks_completed,
    SUM(output_units) AS total_output,
    AVG(crew_size) AS avg_crew_size
FROM production_logs
GROUP BY work_date, work_zone
ORDER BY work_date;
