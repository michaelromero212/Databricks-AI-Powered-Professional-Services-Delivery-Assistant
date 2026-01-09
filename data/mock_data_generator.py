"""
Mock Data Generator for Databricks Professional Services Delivery Assistant

Generates realistic PS operational data for development and demonstration:
- Engagements (customer projects)
- Tasks and milestones
- Delivery notes (free-text)
- Notebook usage metadata
- AI tool usage metrics
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Realistic customer names (fictional companies)
CUSTOMERS = [
    "Acme Financial Services",
    "TechVentures Inc",
    "Global Retail Partners",
    "HealthFirst Analytics",
    "Energy Solutions Corp",
    "Metropolitan Bank",
    "DataDriven Insurance",
    "CloudScale Logistics",
    "SmartManufacturing Co",
    "NextGen Pharma",
    "Velocity Trading",
    "Insight Media Group",
    "Pioneer Healthcare",
    "Quantum Telecom",
    "Atlas Supply Chain"
]

# Engagement types
ENGAGEMENT_TYPES = [
    "Platform Migration",
    "Data Lake Implementation",
    "ML Platform Setup",
    "Delta Lake Implementation",
    "Unity Catalog Deployment",
    "Real-time Analytics",
    "Data Governance",
    "Lakehouse Architecture"
]

# PS team members (fictional)
PS_TEAM = [
    {"id": "ps001", "name": "Sarah Chen", "role": "Senior Solutions Architect"},
    {"id": "ps002", "name": "Marcus Johnson", "role": "Lead Data Engineer"},
    {"id": "ps003", "name": "Emily Rodriguez", "role": "ML Engineer"},
    {"id": "ps004", "name": "David Kim", "role": "Solutions Architect"},
    {"id": "ps005", "name": "Rachel Thompson", "role": "Delivery Manager"},
    {"id": "ps006", "name": "James Wilson", "role": "Data Engineer"},
    {"id": "ps007", "name": "Priya Patel", "role": "Senior Data Engineer"},
    {"id": "ps008", "name": "Michael Brown", "role": "Solutions Architect"}
]

# Task templates
TASK_TEMPLATES = [
    {"name": "Environment Setup", "duration_days": 5, "phase": "Setup"},
    {"name": "Requirements Gathering", "duration_days": 7, "phase": "Discovery"},
    {"name": "Architecture Design", "duration_days": 10, "phase": "Design"},
    {"name": "Data Assessment", "duration_days": 5, "phase": "Discovery"},
    {"name": "Cluster Configuration", "duration_days": 3, "phase": "Setup"},
    {"name": "ETL Pipeline Development", "duration_days": 14, "phase": "Build"},
    {"name": "Data Modeling", "duration_days": 7, "phase": "Build"},
    {"name": "Security Implementation", "duration_days": 5, "phase": "Build"},
    {"name": "Testing & Validation", "duration_days": 7, "phase": "Test"},
    {"name": "Performance Tuning", "duration_days": 5, "phase": "Optimize"},
    {"name": "Documentation", "duration_days": 3, "phase": "Close"},
    {"name": "Knowledge Transfer", "duration_days": 5, "phase": "Close"},
    {"name": "Go-Live Support", "duration_days": 3, "phase": "Close"}
]

# Delivery note templates (realistic PS observations)
DELIVERY_NOTES_POSITIVE = [
    "Customer team is highly engaged and technical. Good progress on {task}.",
    "Completed {task} ahead of schedule. Customer expressed satisfaction with the approach.",
    "Successful workshop with stakeholders. Clear alignment on next steps.",
    "Data quality better than expected. Migration estimates can be reduced.",
    "Customer's existing infrastructure integrates well with Databricks.",
    "Team ramping up quickly on platform features. Minimal hand-holding needed.",
    "Executive sponsor actively involved. Strong organizational support.",
    "Production cluster performing well under load testing.",
]

DELIVERY_NOTES_NEUTRAL = [
    "Working through {task}. On track for milestone deadline.",
    "Regular sync with customer team. No blockers currently.",
    "Documentation in progress for completed modules.",
    "Waiting on customer IT for network configuration.",
    "Data validation scripts running. Results expected tomorrow.",
    "Mid-project review scheduled for next week.",
]

DELIVERY_NOTES_RISK = [
    "Scope creep detected. Customer requesting additional features not in SOW.",
    "Key stakeholder unavailable this week. May impact timeline.",
    "Data quality issues found in source systems. Additional cleansing required.",
    "Customer team resource constraints. Training velocity slower than planned.",
    "Integration complexity higher than estimated. Recommend timeline extension.",
    "Security review pending. May delay production deployment.",
    "Technical debt in legacy systems causing migration challenges.",
    "Customer requesting timeline acceleration. Discussing trade-offs.",
    "Dependency on third-party vendor causing delays.",
]

# Engagement statuses
STATUSES = ["Active", "At Risk", "On Hold", "Completed"]
STATUS_WEIGHTS = [0.5, 0.2, 0.1, 0.2]


def generate_engagement_id():
    """Generate a realistic engagement ID."""
    return f"ENG-{random.randint(2024, 2025)}-{random.randint(1000, 9999)}"


def generate_date_range(start_date: datetime, duration_weeks: int):
    """Generate start and end dates for an engagement."""
    end_date = start_date + timedelta(weeks=duration_weeks)
    return start_date, end_date


def generate_tasks(engagement_id: str, start_date: datetime, owner_id: str):
    """Generate tasks for an engagement."""
    tasks = []
    current_date = start_date
    
    # Select 6-10 tasks from templates
    selected_tasks = random.sample(TASK_TEMPLATES, random.randint(6, 10))
    selected_tasks.sort(key=lambda x: ["Discovery", "Setup", "Design", "Build", "Test", "Optimize", "Close"].index(x["phase"]))
    
    for i, template in enumerate(selected_tasks):
        task_start = current_date
        task_end = task_start + timedelta(days=template["duration_days"])
        
        # Determine task status based on current date simulation
        days_since_start = (datetime.now() - task_start).days
        if days_since_start < 0:
            status = "Not Started"
            progress = 0
        elif days_since_start > template["duration_days"]:
            status = "Completed"
            progress = 100
        else:
            status = "In Progress"
            progress = min(95, int((days_since_start / template["duration_days"]) * 100))
        
        tasks.append({
            "task_id": f"{engagement_id}-T{i+1:02d}",
            "engagement_id": engagement_id,
            "name": template["name"],
            "phase": template["phase"],
            "owner_id": owner_id,
            "start_date": task_start.strftime("%Y-%m-%d"),
            "end_date": task_end.strftime("%Y-%m-%d"),
            "status": status,
            "progress_percent": progress
        })
        
        current_date = task_end
    
    return tasks


def generate_delivery_notes(engagement_id: str, tasks: list, owner_id: str):
    """Generate delivery notes for an engagement."""
    notes = []
    
    # Generate 5-15 notes per engagement
    num_notes = random.randint(5, 15)
    
    for i in range(num_notes):
        # Weighted selection: 50% positive, 30% neutral, 20% risk
        note_type = random.choices(
            ["positive", "neutral", "risk"],
            weights=[0.5, 0.3, 0.2]
        )[0]
        
        if note_type == "positive":
            template = random.choice(DELIVERY_NOTES_POSITIVE)
        elif note_type == "neutral":
            template = random.choice(DELIVERY_NOTES_NEUTRAL)
        else:
            template = random.choice(DELIVERY_NOTES_RISK)
        
        # Replace placeholders
        task_name = random.choice(tasks)["name"] if tasks else "current phase"
        note_text = template.replace("{task}", task_name)
        
        # Random date within engagement timeline
        task_dates = [datetime.strptime(t["start_date"], "%Y-%m-%d") for t in tasks]
        if task_dates:
            note_date = random.choice(task_dates) + timedelta(days=random.randint(0, 5))
        else:
            note_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        notes.append({
            "note_id": f"{engagement_id}-N{i+1:02d}",
            "engagement_id": engagement_id,
            "author_id": owner_id,
            "created_at": note_date.strftime("%Y-%m-%d %H:%M:%S"),
            "content": note_text,
            "sentiment": note_type
        })
    
    return notes


def generate_notebook_usage(engagement_id: str, owner_id: str, num_days: int = 30):
    """Generate notebook usage metadata."""
    usage = []
    
    notebook_names = [
        "01_data_exploration",
        "02_schema_analysis",
        "03_etl_pipeline",
        "04_data_quality_checks",
        "05_performance_testing",
        "06_ml_feature_engineering"
    ]
    
    for day in range(num_days):
        date = datetime.now() - timedelta(days=num_days - day)
        
        # 70% chance of notebook activity on a given day
        if random.random() < 0.7:
            num_notebooks = random.randint(1, 4)
            selected_notebooks = random.sample(notebook_names, min(num_notebooks, len(notebook_names)))
            
            for notebook in selected_notebooks:
                usage.append({
                    "usage_id": str(uuid.uuid4())[:8],
                    "engagement_id": engagement_id,
                    "user_id": owner_id,
                    "notebook_name": notebook,
                    "execution_date": date.strftime("%Y-%m-%d"),
                    "execution_count": random.randint(1, 10),
                    "compute_hours": round(random.uniform(0.1, 2.5), 2)
                })
    
    return usage


def generate_ai_metrics(num_days: int = 30):
    """Generate AI tool usage metrics."""
    metrics = []
    
    roles = ["Solutions Architect", "Data Engineer", "ML Engineer", "Delivery Manager"]
    insight_types = ["health_summary", "risk_detection", "theme_extraction", "action_recommendation"]
    
    for day in range(num_days):
        date = datetime.now() - timedelta(days=num_days - day)
        
        for role in roles:
            # Simulate varying adoption by role
            base_usage = {
                "Solutions Architect": 8,
                "Data Engineer": 5,
                "ML Engineer": 6,
                "Delivery Manager": 10
            }[role]
            
            daily_insights = max(0, base_usage + random.randint(-3, 5))
            
            if daily_insights > 0:
                metrics.append({
                    "metric_id": str(uuid.uuid4())[:8],
                    "date": date.strftime("%Y-%m-%d"),
                    "role": role,
                    "insight_type": random.choice(insight_types),
                    "insights_generated": daily_insights,
                    "estimated_time_saved_minutes": daily_insights * random.randint(5, 15),
                    "user_rating": random.choice([None, 4, 5, 5, 5])  # Mostly positive when rated
                })
    
    return metrics


def generate_all_data(output_dir: str = "data/generated"):
    """Generate all mock data and save to JSON files."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    all_engagements = []
    all_tasks = []
    all_notes = []
    all_notebook_usage = []
    
    # Generate 15 engagements
    for i, customer in enumerate(CUSTOMERS):
        engagement_id = generate_engagement_id()
        
        # Random engagement parameters
        duration_weeks = random.randint(8, 24)
        start_offset = random.randint(-60, 30)  # Some in past, some recent
        start_date = datetime.now() + timedelta(days=start_offset)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Assign team members
        owner = random.choice(PS_TEAM)
        team = random.sample(PS_TEAM, random.randint(2, 4))
        
        # Determine status based on dates
        if end_date < datetime.now():
            status = "Completed"
            health_score = random.randint(75, 100)
        elif start_date > datetime.now():
            status = "Not Started"
            health_score = None
        else:
            status = random.choices(["Active", "At Risk"], weights=[0.7, 0.3])[0]
            health_score = random.randint(40, 95) if status == "Active" else random.randint(25, 60)
        
        engagement = {
            "engagement_id": engagement_id,
            "customer_name": customer,
            "engagement_type": random.choice(ENGAGEMENT_TYPES),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "status": status,
            "health_score": health_score,
            "owner_id": owner["id"],
            "owner_name": owner["name"],
            "team_members": [{"id": m["id"], "name": m["name"], "role": m["role"]} for m in team],
            "contract_value": random.randint(50, 500) * 1000,
            "created_at": (start_date - timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        all_engagements.append(engagement)
        
        # Generate related data
        tasks = generate_tasks(engagement_id, start_date, owner["id"])
        notes = generate_delivery_notes(engagement_id, tasks, owner["id"])
        usage = generate_notebook_usage(engagement_id, owner["id"])
        
        all_tasks.extend(tasks)
        all_notes.extend(notes)
        all_notebook_usage.extend(usage)
    
    # Generate AI metrics
    ai_metrics = generate_ai_metrics()
    
    # Save to JSON files
    data_files = {
        "engagements.json": all_engagements,
        "tasks.json": all_tasks,
        "delivery_notes.json": all_notes,
        "notebook_usage.json": all_notebook_usage,
        "ai_metrics.json": ai_metrics,
        "team_members.json": PS_TEAM
    }
    
    for filename, data in data_files.items():
        filepath = output_path / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath}: {len(data)} records")
    
    print(f"\n✅ All mock data generated in {output_path}/")
    return data_files


if __name__ == "__main__":
    generate_all_data()
