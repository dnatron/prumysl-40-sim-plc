"""
SimulationManager - správa běžících simulací
"""

import logging
from typing import Dict, Optional, List
from sqlmodel import Session, select

from app.models import Machine, Sensor, ProtocolType
from app.simulators.base import BaseSimulator, SimulatorStatus, SimulatorState
from app.simulators.opc_ua import OpcUaSimulator
from app.simulators.modbus_tcp import ModbusTcpSimulator

logger = logging.getLogger(__name__)


class SimulationManager:
    """
    Singleton manager pro správu všech běžících simulací.
    Zajišťuje start/stop simulátorů a sledování jejich stavu.
    """
    
    _instance: Optional["SimulationManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._simulators: Dict[int, BaseSimulator] = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._simulators: Dict[int, BaseSimulator] = {}
            self._initialized = True
            logger.info("SimulationManager inicializován")
    
    async def start_simulation(self, machine: Machine, sensors: List[Sensor]) -> bool:
        """
        Spustí simulaci pro daný stroj.
        
        Args:
            machine: Stroj k simulaci
            sensors: Seznam senzorů stroje
            
        Returns:
            True pokud se simulace úspěšně spustila
        """
        machine_id = machine.id
        
        # Pokud již běží, zastavit
        if machine_id in self._simulators:
            await self.stop_simulation(machine_id)
        
        # Vytvořit správný typ simulátoru
        if machine.protocol == ProtocolType.OPC_UA:
            simulator = OpcUaSimulator(machine, sensors)
        else:
            simulator = ModbusTcpSimulator(machine, sensors)
        
        # Spustit
        success = await simulator.start()
        
        if success:
            self._simulators[machine_id] = simulator
            logger.info(f"Simulace {machine.name} spuštěna ({machine.protocol.value})")
        else:
            logger.error(f"Nepodařilo se spustit simulaci {machine.name}")
        
        return success
    
    async def stop_simulation(self, machine_id: int) -> bool:
        """
        Zastaví simulaci pro daný stroj.
        
        Args:
            machine_id: ID stroje
            
        Returns:
            True pokud se simulace úspěšně zastavila
        """
        if machine_id not in self._simulators:
            logger.warning(f"Simulace pro stroj {machine_id} neběží")
            return True
        
        simulator = self._simulators[machine_id]
        success = await simulator.stop()
        
        if success:
            del self._simulators[machine_id]
            logger.info(f"Simulace stroje {machine_id} zastavena")
        
        return success
    
    async def stop_all(self) -> None:
        """Zastaví všechny běžící simulace"""
        machine_ids = list(self._simulators.keys())
        
        for machine_id in machine_ids:
            await self.stop_simulation(machine_id)
        
        logger.info("Všechny simulace zastaveny")
    
    def get_status(self, machine_id: int) -> SimulatorStatus:
        """Vrátí stav simulace pro daný stroj"""
        if machine_id not in self._simulators:
            return SimulatorStatus.STOPPED
        
        return self._simulators[machine_id].status
    
    def get_state(self, machine_id: int) -> Optional[SimulatorState]:
        """Vrátí kompletní stav simulátoru"""
        if machine_id not in self._simulators:
            return None
        
        return self._simulators[machine_id].get_state()
    
    def get_current_values(self, machine_id: int) -> Optional[Dict[str, float]]:
        """Vrátí aktuální hodnoty senzorů pro daný stroj"""
        if machine_id not in self._simulators:
            return None
        
        return self._simulators[machine_id].get_current_values()
    
    def get_all_running(self) -> List[int]:
        """Vrátí seznam ID všech běžících simulací"""
        return [
            machine_id
            for machine_id, sim in self._simulators.items()
            if sim.status == SimulatorStatus.RUNNING
        ]
    
    def get_error_message(self, machine_id: int) -> Optional[str]:
        """Vrátí chybovou zprávu pokud simulace selhala"""
        if machine_id not in self._simulators:
            return None
        
        return self._simulators[machine_id].error_message
    
    def is_running(self, machine_id: int) -> bool:
        """Zjistí zda simulace běží"""
        return (
            machine_id in self._simulators
            and self._simulators[machine_id].status == SimulatorStatus.RUNNING
        )


# Globální instance
simulation_manager = SimulationManager()
