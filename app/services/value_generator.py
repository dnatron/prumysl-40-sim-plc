"""
Generátory hodnot pro simulaci senzorů
"""

import math
import random
import time
from typing import Union
from app.models.sensor import SimulationType, DataType


class ValueGenerator:
    """
    Generátor hodnot pro simulaci senzorů.
    Podporuje různé typy simulace: random, sine, step, ramp, constant
    """
    
    def __init__(
        self,
        simulation_type: SimulationType,
        data_type: DataType,
        min_value: float,
        max_value: float,
        initial_value: float = 0.0,
    ):
        self.simulation_type = simulation_type
        self.data_type = data_type
        self.min_value = min_value
        self.max_value = max_value
        self.initial_value = initial_value
        
        # Interní stav
        self._current_value = initial_value
        self._start_time = time.time()
        self._step_direction = 1  # Pro RAMP: 1 = nahoru, -1 = dolů
        self._last_step_time = time.time()
        
    def get_value(self) -> Union[float, int, bool]:
        """Vrátí aktuální hodnotu podle typu simulace"""
        
        if self.simulation_type == SimulationType.CONSTANT:
            raw_value = self.initial_value
            
        elif self.simulation_type == SimulationType.RANDOM:
            raw_value = self._generate_random()
            
        elif self.simulation_type == SimulationType.SINE:
            raw_value = self._generate_sine()
            
        elif self.simulation_type == SimulationType.STEP:
            raw_value = self._generate_step()
            
        elif self.simulation_type == SimulationType.RAMP:
            raw_value = self._generate_ramp()
            
        else:
            raw_value = self.initial_value
        
        # Převod na správný datový typ
        return self._convert_to_type(raw_value)
    
    def _generate_random(self) -> float:
        """Generuje náhodnou hodnotu v rozsahu min-max"""
        return random.uniform(self.min_value, self.max_value)
    
    def _generate_sine(self) -> float:
        """
        Generuje sinusový průběh.
        Perioda je 10 sekund, hodnoty oscillují mezi min a max.
        """
        elapsed = time.time() - self._start_time
        period = 10.0  # sekund
        
        # Sinusová vlna od 0 do 1
        normalized = (math.sin(2 * math.pi * elapsed / period) + 1) / 2
        
        # Škálování na rozsah
        return self.min_value + normalized * (self.max_value - self.min_value)
    
    def _generate_step(self) -> float:
        """
        Generuje skokové změny.
        Každé 2 sekundy se hodnota změní na náhodnou hodnotu v rozsahu.
        """
        current_time = time.time()
        step_interval = 2.0  # sekund
        
        if current_time - self._last_step_time >= step_interval:
            self._current_value = random.uniform(self.min_value, self.max_value)
            self._last_step_time = current_time
            
        return self._current_value
    
    def _generate_ramp(self) -> float:
        """
        Generuje lineární nárůst/pokles.
        Hodnota se pomalu zvyšuje/snižuje a pak obrací směr.
        """
        elapsed = time.time() - self._start_time
        
        # Rychlost změny: celý rozsah za 20 sekund
        rate = (self.max_value - self.min_value) / 20.0
        
        # Aktuální pozice v cyklu (ping-pong efekt)
        cycle_position = (elapsed * rate) % (2 * (self.max_value - self.min_value))
        
        if cycle_position <= (self.max_value - self.min_value):
            # Vzestupná fáze
            return self.min_value + cycle_position
        else:
            # Sestupná fáze
            return self.max_value - (cycle_position - (self.max_value - self.min_value))
    
    def _convert_to_type(self, value: float) -> Union[float, int, bool]:
        """Převede hodnotu na správný datový typ"""
        
        if self.data_type == DataType.BOOL:
            # Pro bool: hodnota nad středem rozsahu = True
            threshold = (self.min_value + self.max_value) / 2
            return value > threshold
            
        elif self.data_type == DataType.INT:
            return int(round(value))
            
        else:  # FLOAT
            return round(value, 2)
    
    def reset(self):
        """Resetuje generátor do počátečního stavu"""
        self._current_value = self.initial_value
        self._start_time = time.time()
        self._last_step_time = time.time()
