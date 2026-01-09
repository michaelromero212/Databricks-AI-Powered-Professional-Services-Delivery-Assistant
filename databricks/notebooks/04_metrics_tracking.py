# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Metrics Tracking
# MAGIC 
# MAGIC This notebook tracks and stores AI tooling usage metrics for the PS Delivery Assistant.
# MAGIC 
# MAGIC **Metrics Tracked:**
# MAGIC - Tool usage frequency
# MAGIC - AI insights generated
# MAGIC - Estimated time saved
# MAGIC - Adoption by role

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import uuid

DATABASE_NAME = "ps_delivery_assistant"
spark.sql(f"USE {DATABASE_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Metrics Tables

# COMMAND ----------

# Tool usage events table
spark.sql("""
CREATE TABLE IF NOT EXISTS ps_tool_usage (
    event_id STRING,
    user_id STRING,
    user_role STRING,
    tool_name STRING,
    action STRING,
    engagement_id STRING,
    timestamp TIMESTAMP,
    duration_seconds INT,
    success BOOLEAN
)
USING DELTA
""")

# AI insights metrics table (aggregated)
spark.sql("""
CREATE TABLE IF NOT EXISTS ps_insights_metrics (
    date DATE,
    insight_type STRING,
    role STRING,
    insights_count INT,
    avg_generation_time_seconds DOUBLE,
    estimated_time_saved_minutes INT,
    positive_ratings INT,
    total_ratings INT
)
USING DELTA
""")

# Adoption metrics table
spark.sql("""
CREATE TABLE IF NOT EXISTS ps_adoption_metrics (
    date DATE,
    role STRING,
    unique_users INT,
    total_sessions INT,
    total_insights_viewed INT,
    total_actions_taken INT,
    avg_session_duration_minutes DOUBLE
)
USING DELTA
""")

print("✅ Metrics tables created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log Tool Usage Event

# COMMAND ----------

def log_tool_usage(user_id: str, user_role: str, tool_name: str, 
                   action: str, engagement_id: str = None,
                   duration_seconds: int = 0, success: bool = True):
    """Log a tool usage event."""
    event = {
        "event_id": str(uuid.uuid4())[:8],
        "user_id": user_id,
        "user_role": user_role,
        "tool_name": tool_name,
        "action": action,
        "engagement_id": engagement_id,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration_seconds,
        "success": success
    }
    
    event_df = spark.createDataFrame([event])
    event_df.write.format("delta").mode("append").saveAsTable("ps_tool_usage")
    return event

# Example usage
# log_tool_usage("ps001", "Solutions Architect", "ai_insights", "generate_health_summary", "ENG-2024-1234", 5, True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calculate Daily Metrics

# COMMAND ----------

def calculate_daily_metrics(target_date: str = None):
    """Calculate aggregated metrics for a given date."""
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate insights metrics
    insights_metrics = spark.sql(f"""
        SELECT 
            DATE(generated_at) as date,
            insight_type,
            'All Roles' as role,
            COUNT(*) as insights_count,
            0.0 as avg_generation_time_seconds,
            COUNT(*) * 10 as estimated_time_saved_minutes,
            0 as positive_ratings,
            0 as total_ratings
        FROM ps_ai_insights
        WHERE DATE(generated_at) = '{target_date}'
        GROUP BY DATE(generated_at), insight_type
    """)
    
    if insights_metrics.count() > 0:
        insights_metrics.write.format("delta").mode("append").saveAsTable("ps_insights_metrics")
        print(f"✅ Calculated insights metrics for {target_date}")
    
    # Calculate adoption metrics from tool usage
    adoption_metrics = spark.sql(f"""
        SELECT 
            DATE(timestamp) as date,
            user_role as role,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT CONCAT(user_id, DATE(timestamp))) as total_sessions,
            SUM(CASE WHEN tool_name = 'ai_insights' THEN 1 ELSE 0 END) as total_insights_viewed,
            SUM(CASE WHEN action LIKE 'action_%' THEN 1 ELSE 0 END) as total_actions_taken,
            AVG(duration_seconds) / 60.0 as avg_session_duration_minutes
        FROM ps_tool_usage
        WHERE DATE(timestamp) = '{target_date}'
        GROUP BY DATE(timestamp), user_role
    """)
    
    if adoption_metrics.count() > 0:
        adoption_metrics.write.format("delta").mode("append").saveAsTable("ps_adoption_metrics")
        print(f"✅ Calculated adoption metrics for {target_date}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Metrics Dashboard Queries

# COMMAND ----------

# MAGIC %md
# MAGIC ### Weekly Tool Usage Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     DATE_TRUNC('week', date) as week,
# MAGIC     SUM(unique_users) as weekly_active_users,
# MAGIC     SUM(total_sessions) as total_sessions,
# MAGIC     SUM(total_insights_viewed) as insights_viewed,
# MAGIC     ROUND(AVG(avg_session_duration_minutes), 1) as avg_session_minutes
# MAGIC FROM ps_adoption_metrics
# MAGIC GROUP BY DATE_TRUNC('week', date)
# MAGIC ORDER BY week DESC
# MAGIC LIMIT 12

# COMMAND ----------

# MAGIC %md
# MAGIC ### Adoption by Role

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     role,
# MAGIC     SUM(unique_users) as total_users,
# MAGIC     SUM(total_insights_viewed) as insights_viewed,
# MAGIC     ROUND(SUM(total_insights_viewed) * 10.0, 0) as estimated_minutes_saved
# MAGIC FROM ps_adoption_metrics
# MAGIC GROUP BY role
# MAGIC ORDER BY insights_viewed DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### AI Insights Volume Over Time

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     date,
# MAGIC     insight_type,
# MAGIC     insights_count,
# MAGIC     estimated_time_saved_minutes
# MAGIC FROM ps_insights_metrics
# MAGIC ORDER BY date DESC, insights_count DESC
# MAGIC LIMIT 50

# COMMAND ----------

# MAGIC %md
# MAGIC ### Time Saved Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     SUM(estimated_time_saved_minutes) as total_minutes_saved,
# MAGIC     ROUND(SUM(estimated_time_saved_minutes) / 60.0, 1) as total_hours_saved,
# MAGIC     SUM(insights_count) as total_insights_generated
# MAGIC FROM ps_insights_metrics

# COMMAND ----------

# MAGIC %md
# MAGIC ## Export Metrics for Dashboard

# COMMAND ----------

def get_dashboard_metrics():
    """Get current metrics for the web dashboard."""
    
    # Summary metrics
    summary = spark.sql("""
        SELECT 
            COUNT(DISTINCT engagement_id) as engagements_analyzed,
            COUNT(*) as total_insights,
            ROUND(COUNT(*) * 10 / 60.0, 1) as hours_saved_estimate
        FROM ps_ai_insights
    """).first()
    
    # Insights by type
    by_type = spark.sql("""
        SELECT 
            insight_type,
            COUNT(*) as count
        FROM ps_ai_insights
        GROUP BY insight_type
    """).collect()
    
    # Recent activity
    recent = spark.sql("""
        SELECT 
            DATE(generated_at) as date,
            COUNT(*) as daily_insights
        FROM ps_ai_insights
        WHERE generated_at >= DATE_SUB(CURRENT_DATE(), 30)
        GROUP BY DATE(generated_at)
        ORDER BY date
    """).collect()
    
    return {
        "summary": {
            "engagements_analyzed": summary.engagements_analyzed or 0,
            "total_insights": summary.total_insights or 0,
            "hours_saved": summary.hours_saved_estimate or 0
        },
        "by_type": [{"type": r.insight_type, "count": r.count} for r in by_type],
        "daily_trend": [{"date": str(r.date), "count": r.daily_insights} for r in recent]
    }

# Display current metrics
metrics = get_dashboard_metrics()
print(json.dumps(metrics, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Simulate Historical Metrics (for Demo)

# COMMAND ----------

def simulate_historical_metrics(days: int = 30):
    """Generate simulated historical metrics for demonstration."""
    import random
    
    roles = ["Solutions Architect", "Data Engineer", "ML Engineer", "Delivery Manager"]
    insight_types = ["health_summary", "risk_detection", "theme_extraction", "action_recommendation"]
    
    adoption_records = []
    insights_records = []
    
    for day in range(days):
        date = (datetime.now() - timedelta(days=days - day)).strftime("%Y-%m-%d")
        
        # Adoption metrics - simulate growth over time
        growth_factor = 1 + (day / days) * 0.5  # 50% growth over period
        
        for role in roles:
            base_users = {"Solutions Architect": 5, "Data Engineer": 8, 
                         "ML Engineer": 4, "Delivery Manager": 6}[role]
            
            adoption_records.append({
                "date": date,
                "role": role,
                "unique_users": int(base_users * growth_factor * random.uniform(0.8, 1.2)),
                "total_sessions": int(base_users * 2 * growth_factor * random.uniform(0.7, 1.3)),
                "total_insights_viewed": int(base_users * 3 * growth_factor * random.uniform(0.6, 1.4)),
                "total_actions_taken": int(base_users * growth_factor * random.uniform(0.5, 1.5)),
                "avg_session_duration_minutes": round(random.uniform(5, 25), 1)
            })
        
        # Insights metrics
        for insight_type in insight_types:
            base_count = random.randint(5, 15)
            insights_records.append({
                "date": date,
                "insight_type": insight_type,
                "role": "All Roles",
                "insights_count": int(base_count * growth_factor),
                "avg_generation_time_seconds": round(random.uniform(2, 8), 2),
                "estimated_time_saved_minutes": int(base_count * growth_factor * random.randint(8, 15)),
                "positive_ratings": int(base_count * growth_factor * 0.8),
                "total_ratings": int(base_count * growth_factor * 0.9)
            })
    
    # Write to tables
    adoption_df = spark.createDataFrame(adoption_records)
    adoption_df.write.format("delta").mode("overwrite").saveAsTable("ps_adoption_metrics")
    
    insights_df = spark.createDataFrame(insights_records)
    insights_df.write.format("delta").mode("overwrite").saveAsTable("ps_insights_metrics")
    
    print(f"✅ Simulated {days} days of historical metrics")
    print(f"   - {len(adoption_records)} adoption records")
    print(f"   - {len(insights_records)} insights records")

# Uncomment to generate demo data
# simulate_historical_metrics(30)
