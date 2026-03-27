import json
import os
from datetime import datetime

MEMORIA_DIR = "memoria"
MEMORIA_FILE = os.path.join(MEMORIA_DIR, "historial.json")


def inicializar_memoria():
    os.makedirs(MEMORIA_DIR, exist_ok=True)
    if not os.path.exists(MEMORIA_FILE):
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def guardar_interaccion(usuario: str, agente: str):
    inicializar_memoria()
    historial = cargar_historial()
    historial.append({
        "timestamp": datetime.now().isoformat(),
        "usuario": usuario,
        "agente": agente
    })
    historial = historial[-100:]  # máximo 100 entradas
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


def cargar_historial():
    inicializar_memoria()
    try:
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def historial_como_texto(n_ultimos: int = 10) -> str:
    historial = cargar_historial()
    if not historial:
        return "Sin historial previo."
    recientes = historial[-n_ultimos:]
    lineas = []
    for h in recientes:
        ts = h.get("timestamp", "")[:16].replace("T", " ")
        lineas.append(f"[{ts}] 👤 {h['usuario']}")
        agente_corto = h['agente'][:200] + "..." if len(h['agente']) > 200 else h['agente']
        lineas.append(f"[{ts}] 🤖 {agente_corto}")
        lineas.append("")
    return "\n".join(lineas)


def limpiar_historial():
    inicializar_memoria()
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return "✅ Historial limpiado."