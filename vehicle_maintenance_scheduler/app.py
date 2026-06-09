from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_middleware.logger import Logger
from knapsack import solve_knapsack

app = FastAPI(title="Vehicle Maintenance Scheduler")

# API endpoints
DEPOTS_URL = "http://4.224.186.213/evaluation-service/depots"
VEHICLES_URL = "http://4.224.186.213/evaluation-service/vehicles"

# Response models
class TaskResponse(BaseModel):
    task_id: str
    duration: int
    impact: int

class ScheduleResponse(BaseModel):
    depot_id: int
    mechanic_hours: int
    selected_tasks: List[TaskResponse]
    total_impact: int
    total_duration: int
    remaining_hours: int

def fetch_depots(token: str) -> List[Dict]:
    """Fetch depots from external API"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(DEPOTS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("depots", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch depots: {str(e)}")

def fetch_vehicles(token: str) -> List[Dict]:
    """Fetch vehicles from external API"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(VEHICLES_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("vehicles", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vehicles: {str(e)}")

@app.get("/depots")
async def get_depots(authorization: Optional[str] = Header(None)):
    """Proxy endpoint to fetch depots"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    depots = fetch_depots(token)
    return {"depots": depots}

@app.get("/vehicles")
async def get_vehicles(authorization: Optional[str] = Header(None)):
    """Proxy endpoint to fetch vehicles"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    vehicles = fetch_vehicles(token)
    return {"vehicles": vehicles}

@app.post("/schedule", response_model=ScheduleResponse)
async def optimize_schedule(
    depot_id: int,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    Optimize vehicle maintenance schedule for a specific depot.
    Uses 0/1 Knapsack algorithm to maximize impact within mechanic hours.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    logger = Logger(token)
    
    # Log the request
    background_tasks.add_task(
        logger.log, "backend", "info", "controller",
        f"Optimizing schedule for depot {depot_id}"
    )
    
    # Fetch data from external APIs
    depots = fetch_depots(token)
    vehicles = fetch_vehicles(token)
    
    # Find the specific depot
    depot = next((d for d in depots if d.get("ID") == depot_id), None)
    if not depot:
        background_tasks.add_task(
            logger.log, "backend", "error", "handler",
            f"Depot {depot_id} not found"
        )
        raise HTTPException(status_code=404, detail=f"Depot {depot_id} not found")
    
    mechanic_hours = depot.get("MechanicHours", 0)
    
    # Prepare tasks for knapsack: (task_id, duration, impact)
    tasks = []
    for v in vehicles:
        tasks.append((
            v.get("TaskID", ""),
            v.get("Duration", 0),
            v.get("Impact", 0)
        ))
    
    # Solve knapsack problem
    background_tasks.add_task(
        logger.log, "backend", "info", "service",
        f"Running knapsack with {len(tasks)} tasks and {mechanic_hours} hours"
    )
    
    result = solve_knapsack(tasks, mechanic_hours)
    
    # Log completion
    background_tasks.add_task(
        logger.log, "backend", "info", "repository",
        f"Schedule optimized for depot {depot_id}. Total impact: {result['total_impact']}"
    )
    
    return ScheduleResponse(
        depot_id=depot_id,
        mechanic_hours=mechanic_hours,
        selected_tasks=[TaskResponse(**t) for t in result["selected_tasks"]],
        total_impact=result["total_impact"],
        total_duration=result["total_duration"],
        remaining_hours=result["remaining_hours"]
    )

@app.get("/")
async def root():
    return {
        "message": "Vehicle Maintenance Scheduler API",
        "endpoints": {
            "GET /depots": "Fetch all depots",
            "GET /vehicles": "Fetch all vehicles",
            "POST /schedule?depot_id={id}": "Optimize schedule for depot"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)