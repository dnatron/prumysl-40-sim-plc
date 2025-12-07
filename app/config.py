"""
Konfigurace aplikace
"""

from pathlib import Path

# Základní cesty
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

# Databáze
DATABASE_URL = f"sqlite:///{DATA_DIR}/config.sqlite"

# Výchozí porty
DEFAULT_OPC_UA_PORT = 4840
DEFAULT_MODBUS_PORT = 5020

# Výchozí IP adresa
DEFAULT_HOST = "127.0.0.1"

# Simulace - interval aktualizace hodnot (v sekundách)
SIMULATION_UPDATE_INTERVAL = 1.0


# Zajistit existenci složky data
DATA_DIR.mkdir(parents=True, exist_ok=True)
