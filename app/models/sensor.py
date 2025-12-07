"""
Model pro senzor (Sensor) - hodnoty vystavované strojem
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.machine import Machine


class DataType(str, Enum):
    """Datový typ hodnoty senzoru"""
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"


class SimulationType(str, Enum):
    """Typ simulace hodnot"""
    RANDOM = "random"      # Náhodné hodnoty v rozsahu min-max
    SINE = "sine"          # Sinusový průběh
    STEP = "step"          # Skokové změny
    RAMP = "ramp"          # Lineární nárůst/pokles
    CONSTANT = "constant"  # Konstantní hodnota


class SensorBase(SQLModel):
    """Základní atributy senzoru"""
    name: str = Field(index=True, description="Název senzoru (např. 'Teplota motoru')")
    unit: Optional[str] = Field(default=None, description="Jednotka (např. '°C', 'bar')")
    data_type: DataType = Field(default=DataType.FLOAT, description="Datový typ hodnoty")
    initial_value: float = Field(default=0.0, description="Počáteční hodnota")
    min_value: float = Field(default=0.0, description="Minimální hodnota pro simulaci")
    max_value: float = Field(default=100.0, description="Maximální hodnota pro simulaci")
    simulation_type: SimulationType = Field(
        default=SimulationType.RANDOM,
        description="Typ simulace hodnot"
    )
    # Pro Modbus - adresa registru
    register_address: Optional[int] = Field(
        default=None,
        description="Adresa Modbus registru (auto-přiřazeno pokud None)"
    )


class Sensor(SensorBase, table=True):
    """Databázový model senzoru"""
    __tablename__ = "sensors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machines.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relace na stroj
    machine: Optional["Machine"] = Relationship(back_populates="sensors")
    
    def update_timestamp(self):
        """Aktualizuje čas poslední úpravy"""
        self.updated_at = datetime.utcnow()


class SensorCreate(SensorBase):
    """Schema pro vytvoření senzoru"""
    machine_id: int


class SensorUpdate(SQLModel):
    """Schema pro aktualizaci senzoru"""
    name: Optional[str] = None
    unit: Optional[str] = None
    data_type: Optional[DataType] = None
    initial_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    simulation_type: Optional[SimulationType] = None
    register_address: Optional[int] = None


class SensorRead(SensorBase):
    """Schema pro čtení senzoru"""
    id: int
    machine_id: int
    created_at: datetime
    updated_at: datetime
