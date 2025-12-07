"""
FastAPI routery
"""

from app.routers.dashboard import router as dashboard_router
from app.routers.machines import router as machines_router
from app.routers.api import router as api_router
from app.routers.simulation import router as simulation_router
from app.routers.sensors import router as sensors_router

__all__ = [
    "dashboard_router",
    "machines_router", 
    "api_router",
    "simulation_router",
    "sensors_router",
]
