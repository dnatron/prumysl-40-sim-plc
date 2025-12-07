"""
Testovací OPC UA klient pro ověření simulátoru
"""

import asyncio
from asyncua import Client


async def test_opc_server(url: str = "opc.tcp://127.0.0.1:4840"):
    """Připojí se k OPC UA serveru a vypíše dostupné uzly"""
    
    print(f"🔌 Připojuji se k: {url}")
    
    async with Client(url=url) as client:
        print("✅ Připojeno!")
        
        # Získat root node
        root = client.nodes.root
        print(f"\n📁 Root node: {root}")
        
        # Procházet Objects folder
        objects = client.nodes.objects
        print(f"📁 Objects node: {objects}")
        
        # Vypsat všechny děti Objects
        print("\n🔍 Struktura serveru:")
        await browse_node(objects, indent=0)
        
        # Zkusit najít Machines folder
        print("\n" + "="*50)
        print("📊 Hledám stroje a senzory...")
        
        try:
            # Najít Machines folder
            children = await objects.get_children()
            for child in children:
                name = await child.read_browse_name()
                if "Machines" in str(name):
                    print(f"\n📂 Nalezen: {name}")
                    machines = await child.get_children()
                    for machine in machines:
                        machine_name = await machine.read_browse_name()
                        print(f"  🏭 Stroj: {machine_name}")
                        
                        # Vypsat senzory (proměnné)
                        sensors = await machine.get_children()
                        for sensor in sensors:
                            sensor_name = await sensor.read_browse_name()
                            try:
                                value = await sensor.read_value()
                                print(f"    📈 {sensor_name}: {value}")
                            except:
                                print(f"    📁 {sensor_name} (složka)")
        except Exception as e:
            print(f"⚠️ Chyba při procházení: {e}")


async def browse_node(node, indent=0):
    """Rekurzivně procházení uzlů (max 2 úrovně)"""
    if indent > 2:
        return
    
    try:
        children = await node.get_children()
        for child in children:
            name = await child.read_browse_name()
            try:
                value = await child.read_value()
                print(f"{'  '*indent}├─ {name.Name}: {value}")
            except:
                print(f"{'  '*indent}├─ {name.Name}/")
                await browse_node(child, indent + 1)
    except Exception as e:
        pass


if __name__ == "__main__":
    print("="*50)
    print("🧪 OPC UA Test Client")
    print("="*50)
    
    asyncio.run(test_opc_server())
    
    print("\n" + "="*50)
    print("✅ Test dokončen")
