"""
Databricks Jobs Client

Provides integration with Databricks Jobs API 2.1 for triggering and monitoring notebook runs.
"""

import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DatabricksJobsClient:
    """Client for Databricks Jobs API using the official SDK."""
    
    # Notebook paths in workspace
    NOTEBOOKS = {
        "01_data_ingestion": {
            "path": "/Shared/ps_delivery_assistant/01_data_ingestion",
            "name": "Data Ingestion",
            "description": "Load data into Delta tables"
        },
        "02_feature_engineering": {
            "path": "/Shared/ps_delivery_assistant/02_feature_engineering",
            "name": "Feature Engineering", 
            "description": "Create aggregated views and metrics"
        },
        "03_ai_insights": {
            "path": "/Shared/ps_delivery_assistant/03_ai_insights",
            "name": "AI Insights",
            "description": "Generate AI insights in Databricks"
        },
        "04_metrics_tracking": {
            "path": "/Shared/ps_delivery_assistant/04_metrics_tracking",
            "name": "Metrics Tracking",
            "description": "Track and persist usage metrics"
        }
    }
    
    def __init__(self):
        """Initialize the Databricks client."""
        self.host = os.getenv("DATABRICKS_HOST")
        self.token = os.getenv("DATABRICKS_TOKEN")
        self.cluster_id = os.getenv("DATABRICKS_CLUSTER_ID")
        
        self._client = None
        self._runs_cache: List[Dict] = []
        
        if self.host and self.token:
            try:
                from databricks.sdk import WorkspaceClient
                self._client = WorkspaceClient(
                    host=self.host,
                    token=self.token
                )
            except Exception as e:
                print(f"Warning: Could not initialize Databricks client: {e}")
    
    @property
    def is_configured(self) -> bool:
        """Check if Databricks credentials are configured."""
        return bool(self.host and self.token)
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Databricks."""
        return self._client is not None
    
    def check_connection(self) -> Dict[str, Any]:
        """Verify connection to Databricks workspace."""
        if not self.is_configured:
            return {
                "connected": False,
                "error": "Databricks credentials not configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN."
            }
        
        if not self._client:
            return {
                "connected": False, 
                "error": "Databricks client not initialized"
            }
        
        try:
            # Test connection by getting current user
            me = self._client.current_user.me()
            return {
                "connected": True,
                "host": self.host,
                "user": me.user_name if me else "Unknown"
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def list_notebooks(self) -> List[Dict[str, str]]:
        """List available notebooks for execution."""
        return [
            {
                "id": key,
                "name": info["name"],
                "path": info["path"],
                "description": info["description"]
            }
            for key, info in self.NOTEBOOKS.items()
        ]
    
    def run_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """Submit a one-time notebook run.
        
        Args:
            notebook_id: Key from NOTEBOOKS dict (e.g., "01_data_ingestion")
            
        Returns:
            Dict with run_id and status
        """
        if not self.is_connected:
            return {"success": False, "error": "Databricks not connected"}
        
        notebook_info = self.NOTEBOOKS.get(notebook_id)
        if not notebook_info:
            return {"success": False, "error": f"Unknown notebook: {notebook_id}"}
        
        try:
            from databricks.sdk.service.jobs import SubmitTask, NotebookTask
            
            # Build the run submission
            run = self._client.jobs.submit(
                run_name=f"PS Assistant - {notebook_info['name']}",
                tasks=[
                    SubmitTask(
                        task_key="main_task",
                        existing_cluster_id=self.cluster_id,
                        notebook_task=NotebookTask(
                            notebook_path=notebook_info["path"]
                        )
                    )
                ]
            )
            
            run_id = run.run_id
            
            # Cache the run info
            run_record = {
                "run_id": run_id,
                "notebook_id": notebook_id,
                "notebook_name": notebook_info["name"],
                "submitted_at": datetime.now().isoformat(),
                "status": "PENDING"
            }
            self._runs_cache.insert(0, run_record)
            
            return {
                "success": True,
                "run_id": run_id,
                "notebook_id": notebook_id,
                "notebook_name": notebook_info["name"],
                "status": "PENDING"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_run_status(self, run_id: int) -> Dict[str, Any]:
        """Get the status of a notebook run.
        
        Args:
            run_id: The Databricks run ID
            
        Returns:
            Dict with run status and details
        """
        if not self.is_connected:
            return {"success": False, "error": "Databricks not connected"}
        
        try:
            run = self._client.jobs.get_run(run_id=run_id)
            
            state = run.state
            life_cycle_state = state.life_cycle_state.value if state.life_cycle_state else "UNKNOWN"
            result_state = state.result_state.value if state.result_state else None
            
            # Determine simple status
            if life_cycle_state in ["PENDING", "QUEUED"]:
                status = "PENDING"
            elif life_cycle_state == "RUNNING":
                status = "RUNNING"
            elif life_cycle_state == "TERMINATED":
                status = result_state or "UNKNOWN"
            else:
                status = life_cycle_state
            
            # Update cache
            for cached in self._runs_cache:
                if cached.get("run_id") == run_id:
                    cached["status"] = status
                    if status in ["SUCCESS", "FAILED", "CANCELLED"]:
                        cached["completed_at"] = datetime.now().isoformat()
                    break
            
            return {
                "success": True,
                "run_id": run_id,
                "status": status,
                "life_cycle_state": life_cycle_state,
                "result_state": result_state,
                "state_message": state.state_message if state else None,
                "run_page_url": run.run_page_url
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notebook runs from cache.
        
        For a full implementation, this would query the Jobs API.
        """
        return self._runs_cache[:limit]
    
    def cancel_run(self, run_id: int) -> Dict[str, Any]:
        """Cancel a running notebook job."""
        if not self.is_connected:
            return {"success": False, "error": "Databricks not connected"}
        
        try:
            self._client.jobs.cancel_run(run_id=run_id)
            
            # Update cache
            for cached in self._runs_cache:
                if cached.get("run_id") == run_id:
                    cached["status"] = "CANCELLED"
                    cached["completed_at"] = datetime.now().isoformat()
                    break
            
            return {"success": True, "run_id": run_id, "status": "CANCELLED"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_to_volume(self, local_path: str, volume_path: str) -> Dict[str, Any]:
        """Upload a file to Unity Catalog Volume.
        
        Args:
            local_path: Path to local file
            volume_path: Path in volume (e.g., /Volumes/main/ps_assistant/data/file.json)
            
        Returns:
            Dict with upload status
        """
        if not self.is_connected:
            return {"success": False, "error": "Databricks not connected"}
        
        try:
            with open(local_path, 'rb') as f:
                content = f.read()
            
            self._client.files.upload(volume_path, content, overwrite=True)
            
            return {
                "success": True,
                "file": volume_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sync_data_to_volumes(self, data_dir: str) -> Dict[str, Any]:
        """Sync local data files to Unity Catalog Volumes.
        
        Args:
            data_dir: Path to local data directory
            
        Returns:
            Dict with sync results
        """
        if not self.is_connected:
            return {"success": False, "error": "Databricks not connected"}
        
        import os as os_module
        
        volume_base = "/Volumes/main/ps_assistant/data"
        files_to_sync = [
            "engagements.json",
            "tasks.json", 
            "delivery_notes.json",
            "notebook_usage.json",
            "ai_metrics.json"
        ]
        
        results = []
        for filename in files_to_sync:
            local_path = os_module.path.join(data_dir, filename)
            if os_module.path.exists(local_path):
                volume_path = f"{volume_base}/{filename}"
                result = self.upload_to_volume(local_path, volume_path)
                results.append({
                    "file": filename,
                    "success": result.get("success", False),
                    "error": result.get("error")
                })
            else:
                results.append({
                    "file": filename,
                    "success": False,
                    "error": "File not found locally"
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": success_count == len(files_to_sync),
            "synced": success_count,
            "total": len(files_to_sync),
            "details": results
        }


# Singleton instance
_client: Optional[DatabricksJobsClient] = None


def get_databricks_client() -> DatabricksJobsClient:
    """Get or create the Databricks jobs client singleton."""
    global _client
    if _client is None:
        _client = DatabricksJobsClient()
    return _client
