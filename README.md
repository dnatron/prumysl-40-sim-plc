# PLC Simulátor pro Industry 4.0

Webový simulátor průmyslových PLC strojů s podporou protokolů **OPC UA** a **Modbus TCP**.

## Ukázky aplikace

![Dashboard - přehled strojů](img/app1.png)

![Přidání nového senzoru](img/app2.png)

![Konfigurace stroje](img/app3.png)

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

## Připojení OPC UA klienta

### Endpoint

Každý stroj s protokolem OPC UA vytvoří vlastní server na zadaném portu:

```
opc.tcp://{host}:{port}
```

Příklad: `opc.tcp://127.0.0.1:4840`

### Struktura adresního prostoru

```
Root
└── Objects
    └── Machines
        └── {název stroje}
            └── {název senzoru}  ← hodnota senzoru
```

### Zjištění NodeId senzorů

Pro připojení externích systémů (např. Data Gateway) potřebujete znát NodeId jednotlivých senzorů.

1. **Spusťte simulátor a stroj** (klikněte na "Start")

2. **Spusťte testovací klient**:
   ```bash
   uv run python test_opc_client.py
   ```

3. **Výstup zobrazí NodeId**:
   ```
   📈 QualifiedName(NamespaceIndex=2, Name='teplota'): 24.5
      NodeId: NodeId(Identifier=3, NamespaceIndex=2, ...)
   ```

4. **Formát pro externí systémy**: `ns=2;i=3`
   - `ns=2` - namespace index
   - `i=3` - numeric identifier

### Příklad konfigurace v Data Gateway

| Pole | Hodnota |
|------|---------|
| Host | `127.0.0.1` |
| Port | `4840` |
| Endpoint | `opc.tcp://127.0.0.1:4840` |
| Adresa tagu | `ns=2;i=3` |

## API Dokumentace

Po spuštění je dostupná na:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
