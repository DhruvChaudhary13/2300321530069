"""
Notification App Backend - Stage 6 Priority Inbox
FastAPI application that fetches notifications from test server
and returns top 10 priority notifications.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests

# Import from config file
from config import (
    NOTIFICATIONS_API,
    ACCESS_TOKEN,
    HOST,
    PORT,
    DEFAULT_TOP_N,
    MAX_TOP_N,
    REQUEST_TIMEOUT,
    TYPE_WEIGHTS
)
from priority_inbox import PriorityInbox, get_top_priority_notifications

app = FastAPI(title="Notification App - Priority Inbox")


class NotificationResponse(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str
    priority_score: float
    rank: int


class TopNResponse(BaseModel):
    total_fetched: int
    top_n: List[NotificationResponse]
    stats: Dict[str, Any]


def fetch_notifications() -> List[Dict[str, Any]]:
    """
    Fetch notifications from the test server API using token from config.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            NOTIFICATIONS_API, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("notifications", [])
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Notification App - Priority Inbox API",
        "endpoints": {
            "GET /notifications": "Fetch all notifications from test server",
            "GET /priority-inbox": f"Get top {DEFAULT_TOP_N} priority notifications",
            "GET /priority-inbox?n=15": "Get top 15 priority notifications",
            "GET /priority-inbox/explain": "Explanation of priority calculation"
        },
        "config": {
            "default_top_n": DEFAULT_TOP_N,
            "max_top_n": MAX_TOP_N,
            "type_weights": TYPE_WEIGHTS
        }
    }


@app.get("/notifications")
async def get_notifications():
    """
    Proxy endpoint to fetch all notifications from test server.
    """
    notifications = fetch_notifications()
    return {
        "total": len(notifications),
        "notifications": notifications
    }


@app.get("/priority-inbox", response_model=TopNResponse)
async def get_priority_inbox(
    n: Optional[int] = Query(DEFAULT_TOP_N, description="Number of top notifications to return", ge=1, le=MAX_TOP_N)
):
    """
    Get top N priority notifications based on:
    - Type weight (Placement > Result > Event)
    - Recency (newer notifications have higher priority)
    """
    notifications = fetch_notifications()
    
    if not notifications:
        return TopNResponse(
            total_fetched=0,
            top_n=[],
            stats={"message": "No notifications found"}
        )
    
    inbox = PriorityInbox(n)
    inbox.add_notifications(notifications)
    top_notifications = inbox.get_top_n()
    stats = inbox.get_stats()
    
    return TopNResponse(
        total_fetched=len(notifications),
        top_n=top_notifications,
        stats={
            "total_in_inbox": stats["total_in_inbox"],
            "highest_score": stats["highest_score"],
            "lowest_score": stats["lowest_score"],
            "n_requested": n
        }
    )


@app.get("/priority-inbox/explain")
async def explain_priority():
    """
    Explanation of how priority scores are calculated.
    """
    return {
        "formula": "Priority Score = Type_Weight × Recency_Score",
        "type_weights": TYPE_WEIGHTS,
        "recency_score": "1 / (Days_Ago + 1)",
        "example": {
            "notification": {
                "Type": "Placement",
                "Timestamp": "today"
            },
            "calculation": f"{TYPE_WEIGHTS['Placement']} × 1.0 = {TYPE_WEIGHTS['Placement']} (Highest possible)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)