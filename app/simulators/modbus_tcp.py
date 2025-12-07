"""
Modbus TCP Simulátor
Používá knihovnu pymodbus v3.7+
"""

import asyncio
import logging
import struct
from typing import Dict, Optional, List

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
)
from pymodbus.server import ModbusTcpServer

from app.models import Machine, Sensor, DataType
from app.simulators.base import BaseSimulator

logger = logging.getLogger(__name__)


class ModbusTcpSimulator(BaseSimulator):
    """
    Modbus TCP Server simulátor.
    
    Mapování senzorů na holding registry:
    - INT: 1 registr (16-bit)
    - FLOAT: 2 registry (32-bit, IEEE 754)
    - BOOL: 1 registr (0 nebo 1)
    
    Registry jsou přiřazovány sekvenčně od adresy 0.
    """
    
    def __init__(self, machine: Machine, sensors: List[Sensor]):
        super().__init__(machine, sensors)
        self._server: Optional[ModbusTcpServer] = None
        self._context: Optional[ModbusDeviceContext] = None
        self._register_map: Dict[int, tuple] = {}  # sensor_id -> (start_addr, num_registers)
        self._current_address = 0
    
    def _calculate_register_map(self) -> int:
        """
        Vypočítá mapování senzorů na registry.
        Vrátí celkový počet potřebných registrů.
        """
        self._current_address = 0
        
        for sensor_id, state in self.sensor_states.items():
            sensor = state.sensor
            
            # Pokud má senzor definovanou adresu, použij ji
            if sensor.register_address is not None:
                start_addr = sensor.register_address
            else:
                start_addr = self._current_address
            
            # Počet registrů podle datového typu
            if sensor.data_type == DataType.FLOAT:
                num_registers = 2  # 32-bit float = 2x 16-bit registry
            else:
                num_registers = 1  # INT a BOOL = 1 registr
            
            self._register_map[sensor_id] = (start_addr, num_registers)
            
            # Posunout adresu pro další senzor
            self._current_address = max(self._current_address, start_addr + num_registers)
            
            logger.debug(
                f"Modbus: Senzor {sensor.name} -> registry {start_addr}-{start_addr + num_registers - 1}"
            )
        
        return self._current_address
    
    async def _start_server(self) -> None:
        """Spustí Modbus TCP server"""
        # Vypočítat mapování registrů
        total_registers = self._calculate_register_map()
        
        # Minimálně 100 registrů pro každý typ
        block_size = max(100, total_registers + 10)
        
        # Vytvořit datové bloky pro všechny typy registrů
        self._context = ModbusDeviceContext(
            di=ModbusSequentialDataBlock(0, [0] * block_size),  # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0] * block_size),  # Coils
            hr=ModbusSequentialDataBlock(0, [0] * block_size),  # Holding Registers
            ir=ModbusSequentialDataBlock(0, [0] * block_size),  # Input Registers
        )
        
        # Server context
        server_context = ModbusServerContext(
            devices=self._context,
            single=True,
        )
        
        # Vytvořit a spustit server
        self._server = ModbusTcpServer(
            context=server_context,
            address=(self.machine.host, self.machine.port),
        )
        
        # Spustit server v background
        await self._server.serve_forever(background=True)
        
        # Krátké čekání na start serveru
        await asyncio.sleep(0.3)
        
        logger.info(f"Modbus TCP server spuštěn: {self.machine.host}:{self.machine.port}")
    
    async def _stop_server(self) -> None:
        """Zastaví Modbus TCP server"""
        if self._server:
            try:
                await self._server.shutdown()
            except Exception as e:
                logger.debug(f"Modbus stop: {e}")
            self._server = None
        
        self._context = None
        self._register_map.clear()
        
        logger.info("Modbus TCP server zastaven")
    
    async def _update_values(self) -> None:
        """Aktualizuje hodnoty v Modbus registrech"""
        if not self._context:
            return
        
        for sensor_id, state in self.sensor_states.items():
            if sensor_id not in self._register_map:
                continue
            
            start_addr, num_registers = self._register_map[sensor_id]
            values = self._value_to_registers(state.current_value, state.sensor.data_type)
            
            try:
                # Zápis do holding registrů (function code 3)
                self._context.setValues(3, start_addr, values)
            except Exception as e:
                logger.error(f"Chyba při zápisu do Modbus registru: {e}")
    
    def _value_to_registers(self, value: float, data_type: DataType) -> List[int]:
        """
        Převede hodnotu na Modbus registry.
        """
        if data_type == DataType.BOOL:
            return [1 if value else 0]
        
        elif data_type == DataType.INT:
            # 16-bit signed integer
            int_val = int(value)
            # Clamp to 16-bit range
            int_val = max(-32768, min(32767, int_val))
            # Convert to unsigned for register
            if int_val < 0:
                int_val = int_val + 65536
            return [int_val]
        
        else:  # FLOAT
            # 32-bit float (IEEE 754) -> 2x 16-bit registry (big endian)
            packed = struct.pack('>f', float(value))
            high = struct.unpack('>H', packed[0:2])[0]
            low = struct.unpack('>H', packed[2:4])[0]
            return [high, low]
