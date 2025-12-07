"""
REST API endpoints pro programatický přístup
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Machine, MachineCreate, MachineUpdate
from app.models.machine import MachineRead

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/machines", response_model=List[MachineRead])
async def api_list_machines(session: Session = Depends(get_session)):
    """Vrátí seznam všech strojů"""
    machines = session.exec(select(Machine)).all()
    return machines


@router.get("/machines/{machine_id}", response_model=MachineRead)
async def api_get_machine(machine_id: int, session: Session = Depends(get_session)):
    """Vrátí detail stroje"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    return machine


@router.post("/machines", response_model=MachineRead)
async def api_create_machine(machine_data: MachineCreate, session: Session = Depends(get_session)):
    """Vytvoří nový stroj"""
    machine = Machine.model_validate(machine_data)
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine


@router.patch("/machines/{machine_id}", response_model=MachineRead)
async def api_update_machine(
    machine_id: int, 
    machine_data: MachineUpdate, 
    session: Session = Depends(get_session)
):
    """Aktualizuje stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    update_data = machine_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(machine, key, value)
    
    machine.update_timestamp()
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine


@router.delete("/machines/{machine_id}")
async def api_delete_machine(machine_id: int, session: Session = Depends(get_session)):
    """Smaže stroj"""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Stroj nenalezen")
    
    session.delete(machine)
    session.commit()
    return {"message": "Stroj smazán", "id": machine_id}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "PLC Simulator"}
