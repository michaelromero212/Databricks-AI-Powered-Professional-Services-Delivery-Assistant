"""
FastAPI Backend for PS Delivery Assistant

Provides REST API endpoints for the dashboard application.
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from databricks_connector import get_connector, DatabricksConnector
from ai_client import AIClient

load_dotenv()

# ----- Pydantic Models -----

class InsightRequest(BaseModel):
    """Request model for generating insights."""
    engagement_id: str
    insight_type: str = "health_summary"


class InsightResponse(BaseModel):
    """Response model for generated insights."""
    success: bool
    insight_id: Optional[str] = None
    insight_type: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None
    generated_at: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    ai_connected: bool
    data_mode: str


# ----- Application Setup -----

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 PS Delivery Assistant API starting...")
    yield
    # Shutdown
    print("👋 PS Delivery Assistant API shutting down...")


app = FastAPI(
    title="PS Delivery Assistant API",
    description="AI-powered Professional Services delivery intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Dependencies -----

def get_db() -> DatabricksConnector:
    """Get the database connector."""
    return get_connector()


def get_ai() -> Optional[AIClient]:
    """Get the AI client if token is configured."""
    try:
        return AIClient()
    except ValueError:
        return None


# ----- Health Check -----

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    ai_client = get_ai()
    ai_connected = False
    
    if ai_client:
        status = ai_client.check_connection()
        ai_connected = status.get("connected", False)
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        ai_connected=ai_connected,
        data_mode=os.getenv("DATA_MODE", "local")
    )


# ----- Dashboard -----

@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard overview data."""
    db = get_db()
    return db.get_dashboard_data()


# ----- Engagements -----

@app.get("/api/engagements")
async def list_engagements(
    status: Optional[str] = Query(None, description="Filter by status")
):
    """List all engagements."""
    db = get_db()
    return db.get_engagements(status=status)


@app.get("/api/engagements/{engagement_id}")
async def get_engagement(engagement_id: str):
    """Get a single engagement with details."""
    db = get_db()
    engagement = db.get_engagement_with_details(engagement_id)
    
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    return engagement


@app.get("/api/engagements/{engagement_id}/tasks")
async def get_engagement_tasks(engagement_id: str):
    """Get tasks for an engagement."""
    db = get_db()
    tasks = db.get_tasks(engagement_id=engagement_id)
    return tasks


@app.get("/api/engagements/{engagement_id}/notes")
async def get_engagement_notes(
    engagement_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get delivery notes for an engagement."""
    db = get_db()
    notes = db.get_delivery_notes(engagement_id=engagement_id, limit=limit)
    return notes


# ----- AI Insights -----

@app.get("/api/insights")
async def list_insights(
    engagement_id: Optional[str] = Query(None),
    insight_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """List stored AI insights."""
    db = get_db()
    return db.get_insights(
        engagement_id=engagement_id,
        insight_type=insight_type,
        limit=limit
    )


@app.post("/api/insights/generate", response_model=InsightResponse)
async def generate_insight(request: InsightRequest):
    """Generate a new AI insight for an engagement.
    
    ⚠️ Requires HUGGINGFACE_API_TOKEN environment variable.
    """
    # Get AI client
    ai_client = get_ai()
    if not ai_client:
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable. Please configure HUGGINGFACE_API_TOKEN."
        )
    
    # Get engagement data
    db = get_db()
    engagement = db.get_engagement_with_details(request.engagement_id)
    
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    
    # Prepare data for AI
    notes_text = "\n".join([n.get("content", "") for n in engagement.get("notes", [])[:10]])
    risk_notes = [n.get("content", "") for n in engagement.get("notes", []) if n.get("sentiment") == "risk"]
    
    # Get current phase from tasks
    in_progress = [t for t in engagement.get("tasks", []) if t.get("status") == "In Progress"]
    current_phase = in_progress[0].get("phase") if in_progress else "Unknown"
    
    engagement_data = {
        "engagement_id": engagement.get("engagement_id"),
        "customer_name": engagement.get("customer_name"),
        "engagement_type": engagement.get("engagement_type"),
        "status": engagement.get("status"),
        "health_score": engagement.get("health_score") or 0,
        "days_remaining": 0,  # Calculate if needed
        "completed_tasks": len([t for t in engagement.get("tasks", []) if t.get("status") == "Completed"]),
        "total_tasks": len(engagement.get("tasks", [])),
        "recent_notes": notes_text[:500],
        "delivery_notes": notes_text,
        "all_notes": notes_text,
        "current_phase": current_phase,
        "concerns": "; ".join(risk_notes[:3]) if risk_notes else "None identified"
    }
    
    # Generate insight
    result = ai_client.generate_insight(request.insight_type, engagement_data)
    
    if result.get("success"):
        # Save insight
        insight_id = str(uuid.uuid4())[:8]
        insight_record = {
            "insight_id": insight_id,
            "engagement_id": request.engagement_id,
            "customer_name": engagement.get("customer_name"),
            "insight_type": request.insight_type,
            "content": result.get("content"),
            "generated_at": datetime.now().isoformat()
        }
        db.save_insight(insight_record)
        
        return InsightResponse(
            success=True,
            insight_id=insight_id,
            insight_type=request.insight_type,
            content=result.get("content"),
            generated_at=insight_record["generated_at"]
        )
    else:
        return InsightResponse(
            success=False,
            error=result.get("error", "Unknown error")
        )


@app.post("/api/insights/generate-all/{engagement_id}")
async def generate_all_insights(engagement_id: str):
    """Generate all insight types for an engagement."""
    insight_types = ["health_summary", "risk_detection", "theme_extraction", "action_recommendation"]
    results = []
    
    for insight_type in insight_types:
        request = InsightRequest(engagement_id=engagement_id, insight_type=insight_type)
        try:
            result = await generate_insight(request)
            results.append(result.dict())
        except HTTPException as e:
            results.append({"success": False, "insight_type": insight_type, "error": str(e.detail)})
    
    return {"engagement_id": engagement_id, "insights": results}


# ----- Metrics -----

@app.get("/api/metrics")
async def get_metrics():
    """Get AI tool usage metrics."""
    db = get_db()
    return db.get_metrics_summary()


@app.get("/api/metrics/daily")
async def get_daily_metrics(days: int = Query(30, ge=1, le=90)):
    """Get daily metrics trend."""
    db = get_db()
    metrics = db.get_ai_metrics(days=days)
    return metrics


# ----- Team -----

@app.get("/api/team")
async def get_team():
    """Get team members."""
    db = get_db()
    return db.get_team_members()


# ----- Data Management -----

@app.post("/api/data/regenerate")
async def regenerate_data():
    """Regenerate sample data."""
    import sys
    from pathlib import Path
    
    # Add data directory to path
    data_dir = Path(__file__).parent.parent.parent / "data"
    sys.path.insert(0, str(data_dir))
    
    try:
        from mock_data_generator import generate_all_data
        generate_all_data(str(data_dir / "generated"))
        
        # Clear connector cache
        db = get_db()
        db._cache = {}
        
        return {"success": True, "message": "Sample data regenerated"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/data/upload")
async def upload_data(file: bytes = None, data_type: str = "engagements"):
    """Upload JSON data file.
    
    Note: For POC, this is a simplified implementation.
    In production, use proper file upload handling.
    """
    from fastapi import File, UploadFile, Form
    return {"success": False, "error": "File upload requires multipart form. Use /api/data/regenerate instead."}


# For proper file upload, add this endpoint
from fastapi import File, UploadFile, Form
import json

@app.post("/api/data/upload-file")
async def upload_data_file(
    file: UploadFile = File(...),
    data_type: str = Form("engagements")
):
    """Upload a JSON data file."""
    from pathlib import Path
    
    valid_types = ["engagements", "tasks", "delivery_notes", "ai_metrics"]
    if data_type not in valid_types:
        return {"success": False, "error": f"Invalid data type. Must be one of: {valid_types}"}
    
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        
        if not isinstance(data, list):
            return {"success": False, "error": "JSON must be an array of records"}
        
        # Save to data directory
        data_path = Path(__file__).parent.parent.parent / "data" / "generated" / f"{data_type}.json"
        with open(data_path, "w") as f:
            json.dump(data, f, indent=2)
        
        # Clear connector cache
        db = get_db()
        db._cache = {}
        
        return {"success": True, "records": len(data), "data_type": data_type}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON format"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ----- Databricks Notebook Jobs -----

from databricks_jobs import get_databricks_client

@app.get("/api/notebooks")
async def list_notebooks():
    """List available Databricks notebooks."""
    client = get_databricks_client()
    return {
        "notebooks": client.list_notebooks(),
        "connected": client.is_connected,
        "configured": client.is_configured
    }


@app.get("/api/notebooks/status")
async def get_databricks_status():
    """Check Databricks connection status."""
    client = get_databricks_client()
    return client.check_connection()


class NotebookRunRequest(BaseModel):
    """Request model for running a notebook."""
    notebook_id: str


@app.post("/api/notebooks/run")
async def run_notebook(request: NotebookRunRequest):
    """Trigger a Databricks notebook run."""
    client = get_databricks_client()
    
    if not client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Databricks not connected. Check credentials."
        )
    
    result = client.run_notebook(request.notebook_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@app.get("/api/notebooks/runs")
async def list_notebook_runs(limit: int = Query(10, ge=1, le=50)):
    """Get recent notebook runs."""
    client = get_databricks_client()
    return {"runs": client.get_recent_runs(limit=limit)}


@app.get("/api/notebooks/runs/{run_id}")
async def get_notebook_run_status(run_id: int):
    """Get status of a specific notebook run."""
    client = get_databricks_client()
    
    if not client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Databricks not connected"
        )
    
    result = client.get_run_status(run_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@app.post("/api/notebooks/runs/{run_id}/cancel")
async def cancel_notebook_run(run_id: int):
    """Cancel a running notebook job."""
    client = get_databricks_client()
    
    if not client.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Databricks not connected"
        )
    
    result = client.cancel_run(run_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


# ----- Main -----

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
