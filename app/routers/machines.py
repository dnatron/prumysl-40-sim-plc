"""
CRUD operace pro stroje - HTMX endpoints
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional

from app.config import TEMPLATES_DIR, DEFAULT_OPC_UA_PORT, DEFAULT_MODBUS_PORT
from app.database import get_session
from app.models import Machine, MachineCreate, ProtocolType

router = APIRouter(prefix="/machines", tags=["machines"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/list", response_class=HTMLResponse)
async def list_machines(request: Request, session: Session = Depends(get_session)):
    """Vrátí HTML fragment se seznamem strojů (pro HTMX)"""
    machines = session.exec(select(Machine).order_by(Machine.created_at.desc())).all()
    
    return templates.TemplateResponse(
        "partials/machine_list.html",
        {"request": request, "machines": machines}
    )


@router.get("/form", response_class=HTMLResponse)
async def machine_form(request: Request, machine_id: Optional[int] = None, session: Session = Depends(get_session)):
    """Vrátí formulář pro vytvoření/editaci stroje"""
    machine = None
    if machine_id:
        machine = session.get(Machine, machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    return templates.TemplateResponse(
        "partials/machine_form.html",
        {
            "request": request,
            "machine": machine,
            "protocols": ProtocolType,
            "default_opc_port": DEFAULT_OPC_UA_PORT,
            "default_modbus_port": DEFAULT_MODBUS_PORT,
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_machine(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(None),
    protocol: ProtocolType = Form(...),
    host: str = Form("127.0.0.1"),
    port: int = Form(...),
    is_enabled: bool = Form(True),
):
    """Vytvoří nový stroj"""
    machine = Machine(
        name=name,
        description=description,
        protocol=protocol,
        host=host,
        port=port,
        is_enabled=is_enabled,
    )
    session.add(machine)
    session.commit()
    session.refresh(machine)
    
    # Vrátíme kartu nového stroje
    return templates.TemplateResponse(
        "partials/machine_card.html",
        {"request": request, "machine": machine}
    )


@router.get("/{machine_id}", response_class=HTMLResponse)
async def get_machine(request: Request, machine_id: int, session: Session = Depends(get_session)):
    """Vrátí detail stroje"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    return templates.TemplateResponse(
        "partials/machine_card.html",
        {"request": request, "machine": machine}
    )


@router.put("/{machine_id}", response_class=HTMLResponse)
async def update_machine(
    request: Request,
    machine_id: int,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(None),
    protocol: ProtocolType = Form(...),
    host: str = Form("127.0.0.1"),
    port: int = Form(...),
    is_enabled: bool = Form(True),
):
    """Aktualizuje stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    machine.name = name
    machine.description = description
    machine.protocol = protocol
    machine.host = host
    machine.port = port
    machine.is_enabled = is_enabled
    machine.update_timestamp()
    
    session.add(machine)
    session.commit()
    session.refresh(machine)
    
    return templates.TemplateResponse(
        "partials/machine_card.html",
        {"request": request, "machine": machine}
    )


@router.delete("/{machine_id}", response_class=HTMLResponse)
async def delete_machine(machine_id: int, session: Session = Depends(get_session)):
    """Smaže stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    session.delete(machine)
    session.commit()
    
    # Vrátíme prázdný response pro HTMX (element zmizí)
    return HTMLResponse(content="", status_code=200)
