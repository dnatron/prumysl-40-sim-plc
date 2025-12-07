"""
Model pro stroj (Machine) - PLC simulátor
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.sensor import Sensor


class ProtocolType(str, Enum):
    """Typ komunikačního protokolu"""
    OPC_UA = "opc_ua"
    MODBUS = "modbus"


class MachineBase(SQLModel):
    """Základní atributy stroje"""
    name: str = Field(index=True, description="Název stroje (např. 'Lis-01')")
    description: Optional[str] = Field(default=None, description="Popis stroje")
    protocol: ProtocolType = Field(default=ProtocolType.OPC_UA, description="Komunikační protokol")
    host: str = Field(default="127.0.0.1", description="IP adresa serveru")
    port: int = Field(default=4840, description="Port serveru")
    is_enabled: bool = Field(default=True, description="Zda je stroj aktivní pro simulaci")


class Machine(MachineBase, table=True):
    """Databázový model stroje"""
    __tablename__ = "machines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Čas vytvoření")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Čas poslední úpravy")
    
    # Relace na senzory
    sensors: List["Sensor"] = Relationship(
        back_populates="machine",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    def update_timestamp(self):
        """Aktualizuje čas poslední úpravy"""
        self.updated_at = datetime.utcnow()


class MachineCreate(MachineBase):
    """Schema pro vytvoření stroje"""
    pass


class MachineUpdate(SQLModel):
    """Schema pro aktualizaci stroje"""
    name: Optional[str] = None
    description: Optional[str] = None
    protocol: Optional[ProtocolType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    is_enabled: Optional[bool] = None


class MachineRead(MachineBase):
    """Schema pro čtení stroje"""
    id: int
    created_at: datetime
    updated_at: datetime
