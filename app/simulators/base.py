"""
Abstraktní třída pro simulátory
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from app.models import Machine, Sensor
from app.services.value_generator import ValueGenerator

logger = logging.getLogger(__name__)


class SimulatorStatus(str, Enum):
    """Stav simulátoru"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SensorState:
    """Stav senzoru v simulaci"""
    sensor: Sensor
    generator: ValueGenerator
    current_value: float = 0.0


@dataclass
class SimulatorState:
    """Stav simulátoru"""
    machine_id: int
    status: SimulatorStatus = SimulatorStatus.STOPPED
    error_message: Optional[str] = None
    sensors: Dict[int, SensorState] = field(default_factory=dict)


class BaseSimulator(ABC):
    """
    Abstraktní třída pro simulátory protokolů.
    Definuje společné rozhraní pro OPC UA a Modbus simulátory.
    """
    
    def __init__(self, machine: Machine, sensors: List[Sensor]):
        self.machine = machine
        self.sensors = sensors
        self.status = SimulatorStatus.STOPPED
        self.error_message: Optional[str] = None
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        
        # Inicializace generátorů pro každý senzor
        self.sensor_states: Dict[int, SensorState] = {}
        for sensor in sensors:
            generator = ValueGenerator(
                simulation_type=sensor.simulation_type,
                data_type=sensor.data_type,
                min_value=sensor.min_value,
                max_value=sensor.max_value,
                initial_value=sensor.initial_value,
            )
            self.sensor_states[sensor.id] = SensorState(
                sensor=sensor,
                generator=generator,
                current_value=sensor.initial_value,
            )
    
    @abstractmethod
    async def _start_server(self) -> None:
        """Spustí protokol-specifický server"""
        pass
    
    @abstractmethod
    async def _stop_server(self) -> None:
        """Zastaví protokol-specifický server"""
        pass
    
    @abstractmethod
    async def _update_values(self) -> None:
        """Aktualizuje hodnoty na serveru"""
        pass
    
    async def start(self) -> bool:
        """Spustí simulaci"""
        if self.status == SimulatorStatus.RUNNING:
            logger.warning(f"Simulátor {self.machine.name} již běží")
            return True
        
        try:
            self.status = SimulatorStatus.STARTING
            self._stop_event.clear()
            
            await self._start_server()
            
            self.status = SimulatorStatus.RUNNING
            self.error_message = None
            
            # Spustit update loop
            self._task = asyncio.create_task(self._update_loop())
            
            logger.info(f"Simulátor {self.machine.name} spuštěn na {self.machine.host}:{self.machine.port}")
            return True
            
        except Exception as e:
            self.status = SimulatorStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Chyba při spouštění simulátoru {self.machine.name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Zastaví simulaci"""
        if self.status == SimulatorStatus.STOPPED:
            logger.warning(f"Simulátor {self.machine.name} již je zastaven")
            return True
        
        try:
            self.status = SimulatorStatus.STOPPING
            self._stop_event.set()
            
            # Počkat na ukončení update loop
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            
            await self._stop_server()
            
            self.status = SimulatorStatus.STOPPED
            self.error_message = None
            
            logger.info(f"Simulátor {self.machine.name} zastaven")
            return True
            
        except Exception as e:
            self.status = SimulatorStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Chyba při zastavování simulátoru {self.machine.name}: {e}")
            return False
    
    async def _update_loop(self) -> None:
        """Hlavní smyčka pro aktualizaci hodnot"""
        from app.config import SIMULATION_UPDATE_INTERVAL
        
        while not self._stop_event.is_set():
            try:
                # Aktualizovat hodnoty senzorů
                for sensor_id, state in self.sensor_states.items():
                    state.current_value = state.generator.get_value()
                
                # Publikovat na server
                await self._update_values()
                
            except Exception as e:
                logger.error(f"Chyba v update loop: {e}")
            
            await asyncio.sleep(SIMULATION_UPDATE_INTERVAL)
    
    def get_state(self) -> SimulatorState:
        """Vrátí aktuální stav simulátoru"""
        return SimulatorState(
            machine_id=self.machine.id,
            status=self.status,
            error_message=self.error_message,
            sensors=self.sensor_states,
        )
    
    def get_current_values(self) -> Dict[str, float]:
        """Vrátí aktuální hodnoty všech senzorů"""
        return {
            state.sensor.name: state.current_value
            for state in self.sensor_states.values()
        }
