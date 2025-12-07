# PLC Simulátor pro Industry 4.0

Webový simulátor průmyslových PLC strojů s podporou protokolů **OPC UA** a **Modbus TCP**.

## Technologie

- **Backend**: Python 3.12 + FastAPI
- **Frontend**: Jinja2, Bootstrap 5, HTMX
- **Databáze**: SQLite + SQLModel
- **Protokoly**: asyncua (OPC UA), pymodbus (Modbus TCP)

## Instalace

```bash
# Pomocí uv (doporučeno)
uv sync

# Nebo pip
pip install -e .
```

## Spuštění

```bash
# Vývojový server
uv run uvicorn app.main:app --reload

# Nebo
python -m app.main
```

Aplikace poběží na http://127.0.0.1:8000

## Struktura projektu

```
pumysl40-plc-sim/
├── app/
│   ├── main.py              # FastAPI aplikace
│   ├── config.py            # Konfigurace
│   ├── database.py          # Databázové připojení
│   ├── models/              # SQLModel modely
│   ├── routers/             # API a UI routes
│   ├── simulators/          # OPC UA a Modbus simulátory
│   ├── templates/           # Jinja2 šablony
│   └── static/              # CSS, JS
├── data/
│   └── config.sqlite        # SQLite databáze
└── pyproject.toml
```

## API Dokumentace

Po spuštění je dostupná na:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
