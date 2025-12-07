"""
Dashboard routes - hlavní UI stránky
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import TEMPLATES_DIR
from app.database import get_session
from app.models import Machine
from app.simulators.manager import simulation_manager

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    """Hlavní dashboard s přehledem strojů"""
    machines = session.exec(select(Machine).order_by(Machine.created_at.desc())).all()
    
    # Získat seznam běžících simulací
    running_ids = simulation_manager.get_all_running()
    
    # Spočítat statistiky
    running_count = len(running_ids)
    stopped_count = len(machines) - running_count
    total_sensors = sum(len(m.sensors) if m.sensors else 0 for m in machines)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "machines": machines,
            "running_ids": running_ids,
            "running_count": running_count,
            "stopped_count": stopped_count,
            "total_sensors": total_sensors,
            "title": "PLC Simulátor - Dashboard"
        }
    )
