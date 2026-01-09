-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 02 - Feature Engineering
-- MAGIC 
-- MAGIC This notebook creates derived features and aggregations for the PS Delivery Assistant.
-- MAGIC 
-- MAGIC **Views Created:**
-- MAGIC - `vw_engagement_health` - Engagement health with risk indicators
-- MAGIC - `vw_task_progress` - Task completion rates by engagement
-- MAGIC - `vw_delivery_sentiment` - Sentiment analysis of delivery notes
-- MAGIC - `vw_team_workload` - Team member workload distribution

-- COMMAND ----------

USE ps_delivery_assistant;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Engagement Health View
-- MAGIC 
-- MAGIC Combines engagement data with calculated health metrics

-- COMMAND ----------

CREATE OR REPLACE VIEW vw_engagement_health AS
SELECT 
    e.engagement_id,
    e.customer_name,
    e.engagement_type,
    e.status,
    e.health_score,
    e.owner_name,
    e.start_date,
    e.end_date,
    e.contract_value,
    
    -- Calculate days remaining
    DATEDIFF(e.end_date, CURRENT_DATE()) as days_remaining,
    
    -- Calculate engagement duration
    DATEDIFF(e.end_date, e.start_date) as total_duration_days,
    
    -- Calculate progress percentage based on time
    ROUND(
        CASE 
            WHEN e.status = 'Completed' THEN 100
            WHEN DATEDIFF(CURRENT_DATE(), e.start_date) < 0 THEN 0
            ELSE LEAST(100, 
                (DATEDIFF(CURRENT_DATE(), e.start_date) * 100.0) / 
                NULLIF(DATEDIFF(e.end_date, e.start_date), 0)
            )
        END, 1
    ) as time_progress_percent,
    
    -- Risk level based on health score
    CASE 
        WHEN e.health_score IS NULL THEN 'Unknown'
        WHEN e.health_score >= 75 THEN 'Low'
        WHEN e.health_score >= 50 THEN 'Medium'
        ELSE 'High'
    END as risk_level,
    
    -- Task statistics (subquery)
    task_stats.total_tasks,
    task_stats.completed_tasks,
    task_stats.in_progress_tasks,
    
    -- Note statistics
    note_stats.total_notes,
    note_stats.risk_notes
    
FROM ps_engagements e
LEFT JOIN (
    SELECT 
        engagement_id,
        COUNT(*) as total_tasks,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
        SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tasks
    FROM ps_tasks
    GROUP BY engagement_id
) task_stats ON e.engagement_id = task_stats.engagement_id
LEFT JOIN (
    SELECT 
        engagement_id,
        COUNT(*) as total_notes,
        SUM(CASE WHEN sentiment = 'risk' THEN 1 ELSE 0 END) as risk_notes
    FROM ps_delivery_notes
    GROUP BY engagement_id
) note_stats ON e.engagement_id = note_stats.engagement_id;

-- COMMAND ----------

-- Preview engagement health
SELECT * FROM vw_engagement_health ORDER BY health_score ASC LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Task Progress View
-- MAGIC 
-- MAGIC Aggregates task status by engagement and phase

-- COMMAND ----------

CREATE OR REPLACE VIEW vw_task_progress AS
SELECT 
    t.engagement_id,
    e.customer_name,
    t.phase,
    COUNT(*) as task_count,
    SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_count,
    SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_count,
    SUM(CASE WHEN t.status = 'Not Started' THEN 1 ELSE 0 END) as not_started_count,
    ROUND(AVG(t.progress_percent), 1) as avg_progress,
    MIN(t.start_date) as phase_start,
    MAX(t.end_date) as phase_end
FROM ps_tasks t
JOIN ps_engagements e ON t.engagement_id = e.engagement_id
GROUP BY t.engagement_id, e.customer_name, t.phase
ORDER BY t.engagement_id, 
    CASE t.phase 
        WHEN 'Discovery' THEN 1
        WHEN 'Setup' THEN 2
        WHEN 'Design' THEN 3
        WHEN 'Build' THEN 4
        WHEN 'Test' THEN 5
        WHEN 'Optimize' THEN 6
        WHEN 'Close' THEN 7
    END;

-- COMMAND ----------

-- Preview task progress
SELECT * FROM vw_task_progress LIMIT 20;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Delivery Sentiment Analysis View
-- MAGIC 
-- MAGIC Aggregates sentiment from delivery notes

-- COMMAND ----------

CREATE OR REPLACE VIEW vw_delivery_sentiment AS
SELECT 
    n.engagement_id,
    e.customer_name,
    DATE(n.created_at) as note_date,
    n.sentiment,
    COUNT(*) as note_count,
    COLLECT_LIST(n.content) as note_contents
FROM ps_delivery_notes n
JOIN ps_engagements e ON n.engagement_id = e.engagement_id
GROUP BY n.engagement_id, e.customer_name, DATE(n.created_at), n.sentiment
ORDER BY n.engagement_id, note_date DESC;

-- COMMAND ----------

-- Sentiment distribution by engagement
SELECT 
    engagement_id,
    customer_name,
    SUM(CASE WHEN sentiment = 'positive' THEN note_count ELSE 0 END) as positive_notes,
    SUM(CASE WHEN sentiment = 'neutral' THEN note_count ELSE 0 END) as neutral_notes,
    SUM(CASE WHEN sentiment = 'risk' THEN note_count ELSE 0 END) as risk_notes,
    ROUND(
        SUM(CASE WHEN sentiment = 'positive' THEN note_count ELSE 0 END) * 100.0 / 
        SUM(note_count), 1
    ) as positive_pct
FROM vw_delivery_sentiment
GROUP BY engagement_id, customer_name
ORDER BY positive_pct ASC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Team Workload View
-- MAGIC 
-- MAGIC Analyzes workload distribution across team members

-- COMMAND ----------

CREATE OR REPLACE VIEW vw_team_workload AS
SELECT 
    t.owner_id,
    tm.name as owner_name,
    tm.role,
    COUNT(DISTINCT t.engagement_id) as active_engagements,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) as active_tasks,
    SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
    ROUND(AVG(t.progress_percent), 1) as avg_task_progress
FROM ps_tasks t
LEFT JOIN (
    SELECT DISTINCT 
        team.id,
        team.name,
        team.role
    FROM ps_engagements
    LATERAL VIEW EXPLODE(team_members) AS team
) tm ON t.owner_id = tm.id
WHERE t.status != 'Not Started'
GROUP BY t.owner_id, tm.name, tm.role
ORDER BY active_tasks DESC;

-- COMMAND ----------

-- Preview team workload
SELECT * FROM vw_team_workload;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Dashboard Summary Statistics

-- COMMAND ----------

-- Overall dashboard metrics
SELECT 
    COUNT(*) as total_engagements,
    SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_engagements,
    SUM(CASE WHEN status = 'At Risk' THEN 1 ELSE 0 END) as at_risk_engagements,
    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_engagements,
    ROUND(AVG(health_score), 1) as avg_health_score,
    SUM(contract_value) as total_contract_value
FROM ps_engagements;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Verify All Views Created

-- COMMAND ----------

SHOW VIEWS IN ps_delivery_assistant;
