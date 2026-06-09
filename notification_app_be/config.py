"""
Configuration file for Notification App Backend
Store all configuration in one place for easy management.
"""

# API Endpoints
NOTIFICATIONS_API = "http://4.224.186.213/evaluation-service/notifications"

# Your Access Token (from registration)
# Get this from: POST /auth endpoint response
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJkaHJ1di4yM2IxNTMxMDEyQGFiZXMuYWMuaW4iLCJleHAiOjE3ODA5OTE2MDcsImlhdCI6MTc4MDk5MDcwNywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6ImU5NDhkNTAwLTkzZjctNDU5NS05ZGNhLTA5NTdkMTU0ODJlMSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImRocnV2IGNoYXVkaGFyeSIsInN1YiI6IjEyMTdhMGU0LTE5ZTktNDhlNi1iNjc0LWFjMTkxMDM4ZmYxZCJ9LCJlbWFpbCI6ImRocnV2LjIzYjE1MzEwMTJAYWJlcy5hYy5pbiIsIm5hbWUiOiJkaHJ1diBjaGF1ZGhhcnkiLCJyb2xsTm8iOiIyMzAwMzIxNTMwMDY5IiwiYWNjZXNzQ29kZSI6ImNYdXFodCIsImNsaWVudElEIjoiMTIxN2EwZTQtMTllOS00OGU2LWI2NzQtYWMxOTEwMzhmZjFkIiwiY2xpZW50U2VjcmV0IjoiUFVBd0FXQ3h4R3JYQ2FxVCJ9.iigrlXps0J6fxTm5_JiwpzMyWRSL7Srf4cU_wwyFJps"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8001

# Priority Inbox Settings
DEFAULT_TOP_N = 10
MAX_TOP_N = 50

# Request Timeout (seconds)
REQUEST_TIMEOUT = 10

# Type weights for priority calculation
TYPE_WEIGHTS = {
    "Placement": 3.0,
    "Result": 2.0,
    "Event": 1.0
}