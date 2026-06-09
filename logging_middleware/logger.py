import requests
from typing import Literal

StackType = Literal["backend", "frontend"]
LevelType = Literal["debug", "info", "warn", "error", "fatal"]
PackageType = Literal[
    "cache", "controller", "cron_job", "db", "domain", "handler",
    "repository", "route", "service", "auth", "config", "middleware", "utils"
]

class Logger:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.log_endpoint = "http://4.224.186.213/evaluation-service/logs"
    
    def log(self, stack: StackType, level: LevelType, package: PackageType, message: str):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "stack": stack,
            "level": level,
            "package": package,
            "message": message
        }
        try:
            response = requests.post(self.log_endpoint, json=payload, headers=headers, timeout=3)
            if response.status_code == 200:
                print(f" LOG: {level.upper()} - {message}")
                return response.json()
        except Exception as e:
            print(f"LOG FAILED: {e}")
        return None

def Log(access_token: str, stack: str, level: str, package: str, message: str):
    logger = Logger(access_token)
    return logger.log(stack, level, package, message)