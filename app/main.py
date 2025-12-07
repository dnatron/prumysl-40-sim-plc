"""
Hlavní FastAPI aplikace - PLC Simulátor pro Industry 4.0
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.database import create_db_and_tables
from app.routers import dashboard_router, machines_router, api_router, simulation_router, sensors_router
from app.simulators.manager import simulation_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management - startup a shutdown"""
    # Startup
    print("🚀 Spouštím PLC Simulátor...")
    create_db_and_tables()
    print("✅ Databáze připravena")
    
    yield
    
    # Shutdown
    print("🛑 Zastavuji PLC Simulátor...")
    await simulation_manager.stop_all()
    print("✅ Simulátor zastaven")


# Vytvoření aplikace
app = FastAPI(
    title="PLC Simulátor",
    description="Simulátor průmyslových PLC strojů pro Industry 4.0 - OPC UA a Modbus TCP",
    version="0.1.0",
    lifespan=lifespan,
)

# Připojení statických souborů
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Registrace routerů
app.include_router(dashboard_router)
app.include_router(machines_router)
app.include_router(api_router)
app.include_router(simulation_router)
app.include_router(sensors_router)


def run():
    """Spustí aplikaci pomocí uvicorn"""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
