# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - AI Insights Generation
# MAGIC 
# MAGIC This notebook generates AI-powered insights using Hugging Face's Inference API.
# MAGIC 
# MAGIC **Capabilities:**
# MAGIC - Summarize engagement health
# MAGIC - Identify delivery risk signals
# MAGIC - Extract recurring themes from notes
# MAGIC - Recommend next actions

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC 
# MAGIC ⚠️ **Required:** Set your Hugging Face API token as a Databricks secret or widget.

# COMMAND ----------

import requests
import json
from datetime import datetime
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Get API token from Databricks secrets
# To set up: databricks secrets create-scope --scope ps-assistant
#            databricks secrets put --scope ps-assistant --key hf-token
try:
    HF_API_TOKEN = dbutils.secrets.get(scope="ps-assistant", key="hf-token")
except:
    # Fallback to widget for development
    dbutils.widgets.text("hf_token", "", "Hugging Face API Token")
    HF_API_TOKEN = dbutils.widgets.get("hf_token")

if not HF_API_TOKEN:
    raise ValueError("⚠️ Please provide a Hugging Face API token")

# Model configuration
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

DATABASE_NAME = "ps_delivery_assistant"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prompt Templates

# COMMAND ----------

PROMPT_TEMPLATES = {
    "health_summary": """<s>[INST] You are a Professional Services delivery analyst. Analyze this engagement data and provide a concise health summary.

Engagement: {customer_name}
Type: {engagement_type}
Status: {status}
Health Score: {health_score}/100
Days Remaining: {days_remaining}
Tasks: {completed_tasks}/{total_tasks} completed
Recent Notes: {recent_notes}

Provide a 2-3 sentence health summary focusing on delivery status and any concerns. Be specific and actionable. [/INST]""",

    "risk_detection": """<s>[INST] You are a Professional Services risk analyst. Review these delivery notes and identify any risk signals.

Customer: {customer_name}
Engagement Type: {engagement_type}
Current Status: {status}

Recent Delivery Notes:
{delivery_notes}

List any risk signals found (scope creep, resource issues, timeline concerns, technical blockers). If no risks, state "No significant risks identified." Be concise. [/INST]""",

    "theme_extraction": """<s>[INST] You are a Professional Services analyst. Extract the main themes from these delivery notes.

Customer: {customer_name}
Notes:
{all_notes}

Identify 3-5 recurring themes or patterns. Format as a bullet list. Focus on actionable insights. [/INST]""",

    "action_recommendation": """<s>[INST] You are a Professional Services delivery manager. Based on this engagement status, recommend next actions.

Customer: {customer_name}
Status: {status}
Health Score: {health_score}/100
Current Phase: {current_phase}
Key Concerns: {concerns}

Recommend 2-3 specific next actions the PS team should take. Be practical and prioritize impact. [/INST]"""
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## AI Client Functions

# COMMAND ----------

def query_llm(prompt: str, max_tokens: int = 256) -> str:
    """Send a prompt to the Hugging Face Inference API."""
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        return str(result)
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def generate_insight(insight_type: str, engagement_data: dict) -> dict:
    """Generate a specific type of insight for an engagement."""
    template = PROMPT_TEMPLATES.get(insight_type)
    if not template:
        return {"error": f"Unknown insight type: {insight_type}"}
    
    # Format the prompt with engagement data
    prompt = template.format(**engagement_data)
    
    # Query the LLM
    response = query_llm(prompt)
    
    return {
        "insight_type": insight_type,
        "engagement_id": engagement_data.get("engagement_id"),
        "customer_name": engagement_data.get("customer_name"),
        "generated_at": datetime.now().isoformat(),
        "content": response
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Engagement Data

# COMMAND ----------

spark.sql(f"USE {DATABASE_NAME}")

# Get engagement health data
engagement_health_df = spark.sql("""
    SELECT * FROM vw_engagement_health 
    WHERE status IN ('Active', 'At Risk')
    ORDER BY health_score ASC
""")

display(engagement_health_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Insights for At-Risk Engagements

# COMMAND ----------

# Get at-risk engagements
at_risk = spark.sql("""
    SELECT 
        e.*,
        COLLECT_LIST(n.content) as recent_notes
    FROM vw_engagement_health e
    LEFT JOIN ps_delivery_notes n ON e.engagement_id = n.engagement_id
    WHERE e.status = 'At Risk' OR e.health_score < 60
    GROUP BY e.engagement_id, e.customer_name, e.engagement_type, e.status,
             e.health_score, e.owner_name, e.start_date, e.end_date, 
             e.contract_value, e.days_remaining, e.total_duration_days,
             e.time_progress_percent, e.risk_level, e.total_tasks,
             e.completed_tasks, e.in_progress_tasks, e.total_notes, e.risk_notes
    LIMIT 5
""").collect()

print(f"Found {len(at_risk)} at-risk engagements")

# COMMAND ----------

# Generate health summaries for at-risk engagements
insights = []

for row in at_risk:
    engagement_data = {
        "engagement_id": row.engagement_id,
        "customer_name": row.customer_name,
        "engagement_type": row.engagement_type,
        "status": row.status,
        "health_score": row.health_score or 0,
        "days_remaining": row.days_remaining or 0,
        "completed_tasks": row.completed_tasks or 0,
        "total_tasks": row.total_tasks or 0,
        "recent_notes": "; ".join(row.recent_notes[:3]) if row.recent_notes else "No recent notes"
    }
    
    # Generate health summary
    insight = generate_insight("health_summary", engagement_data)
    insights.append(insight)
    print(f"\n📊 {row.customer_name}:")
    print(f"   {insight['content'][:200]}...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Store Insights in Delta Table

# COMMAND ----------

# Define insights schema
insights_schema = StructType([
    StructField("insight_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("customer_name", StringType(), True),
    StructField("insight_type", StringType(), True),
    StructField("content", StringType(), True),
    StructField("generated_at", StringType(), True)
])

# Create DataFrame from insights
import uuid
insights_with_id = [
    {
        "insight_id": str(uuid.uuid4())[:8],
        **insight
    }
    for insight in insights
]

if insights_with_id:
    insights_df = spark.createDataFrame(insights_with_id, insights_schema)
    
    # Append to Delta table
    insights_df.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable(f"{DATABASE_NAME}.ps_ai_insights")
    
    print(f"✅ Saved {len(insights_with_id)} insights to ps_ai_insights table")
else:
    print("No insights to save")

# COMMAND ----------

# MAGIC %md
# MAGIC ## View Generated Insights

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ps_delivery_assistant.ps_ai_insights 
# MAGIC ORDER BY generated_at DESC 
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Batch Insight Generation
# MAGIC 
# MAGIC Generate multiple insight types for an engagement

# COMMAND ----------

def generate_full_analysis(engagement_id: str) -> list:
    """Generate all insight types for a single engagement."""
    
    # Get engagement data with notes
    eng_data = spark.sql(f"""
        SELECT 
            e.*,
            COLLECT_LIST(n.content) as all_notes,
            COLLECT_LIST(CASE WHEN n.sentiment = 'risk' THEN n.content END) as risk_notes
        FROM vw_engagement_health e
        LEFT JOIN ps_delivery_notes n ON e.engagement_id = n.engagement_id
        WHERE e.engagement_id = '{engagement_id}'
        GROUP BY e.engagement_id, e.customer_name, e.engagement_type, e.status,
                 e.health_score, e.owner_name, e.start_date, e.end_date, 
                 e.contract_value, e.days_remaining, e.total_duration_days,
                 e.time_progress_percent, e.risk_level, e.total_tasks,
                 e.completed_tasks, e.in_progress_tasks, e.total_notes, e.risk_notes
    """).first()
    
    if not eng_data:
        return []
    
    # Get current phase
    current_phase = spark.sql(f"""
        SELECT phase FROM ps_tasks 
        WHERE engagement_id = '{engagement_id}' AND status = 'In Progress'
        LIMIT 1
    """).first()
    
    base_data = {
        "engagement_id": eng_data.engagement_id,
        "customer_name": eng_data.customer_name,
        "engagement_type": eng_data.engagement_type,
        "status": eng_data.status,
        "health_score": eng_data.health_score or 0,
        "days_remaining": eng_data.days_remaining or 0,
        "completed_tasks": eng_data.completed_tasks or 0,
        "total_tasks": eng_data.total_tasks or 0,
        "recent_notes": "; ".join(eng_data.all_notes[:5]) if eng_data.all_notes else "",
        "delivery_notes": "\n".join(eng_data.all_notes[:10]) if eng_data.all_notes else "",
        "all_notes": "\n".join(eng_data.all_notes) if eng_data.all_notes else "",
        "current_phase": current_phase.phase if current_phase else "Unknown",
        "concerns": "; ".join([n for n in (eng_data.risk_notes or []) if n][:3])
    }
    
    all_insights = []
    for insight_type in PROMPT_TEMPLATES.keys():
        insight = generate_insight(insight_type, base_data)
        all_insights.append(insight)
        print(f"✅ Generated {insight_type} for {eng_data.customer_name}")
    
    return all_insights

# COMMAND ----------

# Example: Generate full analysis for one engagement
# Uncomment and run with a valid engagement_id
# full_insights = generate_full_analysis("ENG-2024-1234")
# for insight in full_insights:
#     print(f"\n{'='*50}")
#     print(f"Type: {insight['insight_type']}")
#     print(f"Content: {insight['content']}")
