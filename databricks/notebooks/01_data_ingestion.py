# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Data Ingestion
# MAGIC 
# MAGIC This notebook ingests mock Professional Services engagement data into Delta tables.
# MAGIC 
# MAGIC **Tables Created:**
# MAGIC - `ps_engagements` - Customer engagement records
# MAGIC - `ps_tasks` - Tasks and milestones per engagement
# MAGIC - `ps_delivery_notes` - Free-text delivery observations
# MAGIC - `ps_notebook_usage` - Notebook execution metadata
# MAGIC - `ps_ai_metrics` - AI tool usage tracking

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from datetime import datetime

# Database configuration
DATABASE_NAME = "ps_delivery_assistant"
DATA_PATH = "/FileStore/ps_assistant/data"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Database

# COMMAND ----------

spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
spark.sql(f"USE {DATABASE_NAME}")
print(f"Using database: {DATABASE_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Schemas

# COMMAND ----------

# Engagements schema
engagements_schema = StructType([
    StructField("engagement_id", StringType(), False),
    StructField("customer_name", StringType(), False),
    StructField("engagement_type", StringType(), True),
    StructField("start_date", StringType(), True),
    StructField("end_date", StringType(), True),
    StructField("status", StringType(), True),
    StructField("health_score", IntegerType(), True),
    StructField("owner_id", StringType(), True),
    StructField("owner_name", StringType(), True),
    StructField("team_members", ArrayType(
        StructType([
            StructField("id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("role", StringType(), True)
        ])
    ), True),
    StructField("contract_value", IntegerType(), True),
    StructField("created_at", StringType(), True)
])

# Tasks schema
tasks_schema = StructType([
    StructField("task_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("name", StringType(), True),
    StructField("phase", StringType(), True),
    StructField("owner_id", StringType(), True),
    StructField("start_date", StringType(), True),
    StructField("end_date", StringType(), True),
    StructField("status", StringType(), True),
    StructField("progress_percent", IntegerType(), True)
])

# Delivery notes schema
notes_schema = StructType([
    StructField("note_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("author_id", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("content", StringType(), True),
    StructField("sentiment", StringType(), True)
])

# Notebook usage schema
usage_schema = StructType([
    StructField("usage_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("user_id", StringType(), True),
    StructField("notebook_name", StringType(), True),
    StructField("execution_date", StringType(), True),
    StructField("execution_count", IntegerType(), True),
    StructField("compute_hours", DoubleType(), True)
])

# AI metrics schema
metrics_schema = StructType([
    StructField("metric_id", StringType(), False),
    StructField("date", StringType(), True),
    StructField("role", StringType(), True),
    StructField("insight_type", StringType(), True),
    StructField("insights_generated", IntegerType(), True),
    StructField("estimated_time_saved_minutes", IntegerType(), True),
    StructField("user_rating", IntegerType(), True)
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load and Write Data
# MAGIC 
# MAGIC **Note:** Upload the generated JSON files from `data/generated/` to DBFS at `/FileStore/ps_assistant/data/`

# COMMAND ----------

def load_and_write_delta(json_path: str, table_name: str, schema: StructType):
    """Load JSON data and write to Delta table."""
    try:
        df = spark.read.schema(schema).json(f"{DATA_PATH}/{json_path}")
        
        # Write to Delta table
        df.write \
            .format("delta") \
            .mode("overwrite") \
            .saveAsTable(f"{DATABASE_NAME}.{table_name}")
        
        record_count = df.count()
        print(f"✅ {table_name}: {record_count} records written to Delta")
        return df
    except Exception as e:
        print(f"❌ Error loading {table_name}: {str(e)}")
        return None

# COMMAND ----------

# Load all data
engagements_df = load_and_write_delta("engagements.json", "ps_engagements", engagements_schema)
tasks_df = load_and_write_delta("tasks.json", "ps_tasks", tasks_schema)
notes_df = load_and_write_delta("delivery_notes.json", "ps_delivery_notes", notes_schema)
usage_df = load_and_write_delta("notebook_usage.json", "ps_notebook_usage", usage_schema)
metrics_df = load_and_write_delta("ai_metrics.json", "ps_ai_metrics", metrics_schema)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Tables

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN ps_delivery_assistant

# COMMAND ----------

# Preview data
if engagements_df:
    display(engagements_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC   'Engagements' as table_name, COUNT(*) as record_count FROM ps_delivery_assistant.ps_engagements
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Tasks' as table_name, COUNT(*) as record_count FROM ps_delivery_assistant.ps_tasks
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Delivery Notes' as table_name, COUNT(*) as record_count FROM ps_delivery_assistant.ps_delivery_notes
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Notebook Usage' as table_name, COUNT(*) as record_count FROM ps_delivery_assistant.ps_notebook_usage
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'AI Metrics' as table_name, COUNT(*) as record_count FROM ps_delivery_assistant.ps_ai_metrics
