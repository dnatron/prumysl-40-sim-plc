"""
Routes pro správu simulací - start/stop/status
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.config import TEMPLATES_DIR
from app.database import get_session
from app.models import Machine
from app.simulators.manager import simulation_manager
from app.simulators.base import SimulatorStatus

router = APIRouter(prefix="/simulation", tags=["simulation"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.post("/{machine_id}/start", response_class=HTMLResponse)
async def start_simulation(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session),
):
    """Spustí simulaci pro daný stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    # Načíst senzory
    sensors = list(machine.sensors) if machine.sensors else []
    
    # Spustit simulaci
    success = await simulation_manager.start_simulation(machine, sensors)
    
    if not success:
        error = simulation_manager.get_error_message(machine_id)
        return templates.TemplateResponse(
            "partials/status_badge.html",
            {
                "request": request,
                "machine": machine,
                "status": "error",
                "error_message": error,
            }
        )
    
    # Vrátit aktualizovanou kartu
    return templates.TemplateResponse(
        "partials/machine_card.html",
        {
            "request": request,
            "machine": machine,
            "status": simulation_manager.get_status(machine_id),
            "is_running": True,
        }
    )


@router.post("/{machine_id}/stop", response_class=HTMLResponse)
async def stop_simulation(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session),
):
    """Zastaví simulaci pro daný stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    await simulation_manager.stop_simulation(machine_id)
    
    return templates.TemplateResponse(
        "partials/machine_card.html",
        {
            "request": request,
            "machine": machine,
            "status": SimulatorStatus.STOPPED,
            "is_running": False,
        }
    )


@router.get("/{machine_id}/status", response_class=HTMLResponse)
async def get_simulation_status(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session),
):
    """Vrátí aktuální stav simulace"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    status = simulation_manager.get_status(machine_id)
    is_running = simulation_manager.is_running(machine_id)
    error = simulation_manager.get_error_message(machine_id)
    
    return templates.TemplateResponse(
        "partials/status_badge.html",
        {
            "request": request,
            "machine": machine,
            "status": status.value,
            "is_running": is_running,
            "error_message": error,
        }
    )


@router.get("/{machine_id}/values")
async def get_sensor_values(machine_id: int):
    """Vrátí aktuální hodnoty senzorů (JSON)"""
    values = simulation_manager.get_current_values(machine_id)
    
    if values is None:
        return {"running": False, "values": {}}
    
    return {
        "running": True,
        "status": simulation_manager.get_status(machine_id).value,
        "values": values,
    }
