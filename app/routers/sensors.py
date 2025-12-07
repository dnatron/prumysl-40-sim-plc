"""
CRUD operace pro senzory - HTMX endpoints
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional

from app.config import TEMPLATES_DIR
from app.database import get_session
from app.models import Machine, Sensor, SensorCreate, DataType, SimulationType

router = APIRouter(prefix="/sensors", tags=["sensors"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/form/{machine_id}", response_class=HTMLResponse)
async def sensor_form(
    request: Request,
    machine_id: int,
    sensor_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Vrátí formulář pro přidání/editaci senzoru"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    sensor = None
    if sensor_id:
        sensor = session.get(Sensor, sensor_id)
    
    return templates.TemplateResponse(
        "partials/sensor_form.html",
        {
            "request": request,
            "machine": machine,
            "sensor": sensor,
            "data_types": DataType,
            "simulation_types": SimulationType,
        }
    )


@router.post("/create/{machine_id}", response_class=HTMLResponse)
async def create_sensor(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session),
    name: str = Form(...),
    unit: str = Form(None),
    data_type: DataType = Form(DataType.FLOAT),
    simulation_type: SimulationType = Form(SimulationType.RANDOM),
    initial_value: float = Form(0.0),
    min_value: float = Form(0.0),
    max_value: float = Form(100.0),
):
    """Vytvoří nový senzor"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    sensor = Sensor(
        machine_id=machine_id,
        name=name,
        unit=unit if unit else None,
        data_type=data_type,
        simulation_type=simulation_type,
        initial_value=initial_value,
        min_value=min_value,
        max_value=max_value,
    )
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    
    # Vrátíme řádek nového senzoru
    return templates.TemplateResponse(
        "partials/sensor_row.html",
        {"request": request, "sensor": sensor, "machine": machine}
    )


@router.delete("/{sensor_id}", response_class=HTMLResponse)
async def delete_sensor(sensor_id: int, session: Session = Depends(get_session)):
    """Smaže senzor"""
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Senzor nenalezen")
    
    session.delete(sensor)
    session.commit()
    
    return HTMLResponse(content="", status_code=200)


@router.get("/list/{machine_id}", response_class=HTMLResponse)
async def list_sensors(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session)
):
    """Vrátí seznam senzorů pro stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    sensors = session.exec(
        select(Sensor).where(Sensor.machine_id == machine_id)
    ).all()
    
    return templates.TemplateResponse(
        "partials/sensor_list.html",
        {"request": request, "sensors": sensors, "machine": machine}
    )
