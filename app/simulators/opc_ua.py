"""
OPC UA Simulátor
Používá knihovnu asyncua (opcua-asyncio)
"""

import logging
from typing import Dict, Optional, List
from asyncua import Server, ua

from app.models import Machine, Sensor, DataType
from app.simulators.base import BaseSimulator

logger = logging.getLogger(__name__)


class OpcUaSimulator(BaseSimulator):
    """
    OPC UA Server simulátor.
    
    Struktura adresního prostoru:
    Root → Objects → Machines → {machine_name} → {sensor_name}
    """
    
    def __init__(self, machine: Machine, sensors: List[Sensor]):
        super().__init__(machine, sensors)
        self._server: Optional[Server] = None
        self._nodes: Dict[int, object] = {}  # sensor_id -> UA node
        self._ua_types: Dict[int, ua.VariantType] = {}  # sensor_id -> UA type
    
    async def _start_server(self) -> None:
        """Spustí OPC UA server"""
        self._server = Server()
        
        await self._server.init()
        
        # Nastavení endpointu
        endpoint = f"opc.tcp://{self.machine.host}:{self.machine.port}"
        self._server.set_endpoint(endpoint)
        
        # Nastavení jména serveru
        self._server.set_server_name(f"PLC Simulator - {self.machine.name}")
        
        # Registrace namespace
        uri = f"urn:plc-simulator:{self.machine.name}"
        idx = await self._server.register_namespace(uri)
        
        # Vytvoření struktury: Objects -> Machines -> {machine_name}
        objects = self._server.nodes.objects
        
        # Složka Machines
        machines_folder = await objects.add_folder(idx, "Machines")
        
        # Složka pro tento stroj
        machine_folder = await machines_folder.add_folder(idx, self.machine.name)
        
        # Přidání senzorů jako proměnných
        for sensor_id, state in self.sensor_states.items():
            sensor = state.sensor
            
            # Určení UA datového typu
            ua_type = self._get_ua_type(sensor.data_type)
            initial_value = self._convert_value(state.current_value, sensor.data_type)
            
            # Vytvoření proměnné
            node = await machine_folder.add_variable(
                idx,
                sensor.name,
                initial_value,
                varianttype=ua_type,
            )
            
            # Povolit zápis (pro případné ruční změny)
            await node.set_writable()
            
            self._nodes[sensor_id] = node
            self._ua_types[sensor_id] = ua_type
            
            logger.debug(f"OPC UA: Přidán senzor {sensor.name} ({sensor.data_type.value})")
        
        # Spustit server
        await self._server.start()
        
        logger.info(f"OPC UA server spuštěn: {endpoint}")
    
    async def _stop_server(self) -> None:
        """Zastaví OPC UA server"""
        if self._server:
            await self._server.stop()
            self._server = None
            self._nodes.clear()
            self._ua_types.clear()
            logger.info("OPC UA server zastaven")
    
    async def _update_values(self) -> None:
        """Aktualizuje hodnoty na OPC UA serveru"""
        if not self._server:
            return
        
        for sensor_id, state in self.sensor_states.items():
            if sensor_id in self._nodes:
                node = self._nodes[sensor_id]
                ua_type = self._ua_types[sensor_id]
                value = self._convert_value(state.current_value, state.sensor.data_type)
                
                try:
                    # Použít ua.Variant s explicitním typem pro správný zápis
                    variant = ua.Variant(value, ua_type)
                    await node.write_value(variant)
                except Exception as e:
                    logger.error(f"Chyba při zápisu hodnoty {state.sensor.name}: {e}")
    
    def _get_ua_type(self, data_type: DataType) -> ua.VariantType:
        """Převede datový typ na UA VariantType"""
        mapping = {
            DataType.FLOAT: ua.VariantType.Float,
            DataType.INT: ua.VariantType.Int32,
            DataType.BOOL: ua.VariantType.Boolean,
        }
        return mapping.get(data_type, ua.VariantType.Float)
    
    def _convert_value(self, value: float, data_type: DataType):
        """Převede hodnotu na správný Python typ pro UA"""
        if data_type == DataType.BOOL:
            return bool(value)
        elif data_type == DataType.INT:
            return int(value)
        else:
            return float(value)
