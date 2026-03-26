from langchain_core.tools import tool
import subprocess
import math
import os
import json
from datetime import date, datetime
from src.memory import historial_como_texto, limpiar_historial as _limpiar

# ─────────────────────────────────────────
# 🌐 BUSCADOR
# ─────────────────────────────────────────
@tool
def buscar_en_internet(query: str) -> str:
    """Busca información actual en internet usando DuckDuckGo."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=5))
        if not resultados:
            return "Sin resultados."
        return "\n\n".join(
            f"Título: {r.get('title')}\nResumen: {r.get('body')}\nURL: {r.get('href')}"
            for r in resultados
        )
    except Exception as e:
        return f"Error al buscar: {str(e)}"


# ─────────────────────────────────────────
# 🧮 CALCULADORA
# ─────────────────────────────────────────
@tool
def calcular(expresion: str) -> str:
    """Evalúa expresiones matemáticas. Soporta: sqrt, pow, abs, round, date, datetime."""
    try:
        permitidos = {
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs,
            "round": round,
            "int": int,
            "float": float,
            "str": str,
            "date": date,
            "datetime": datetime,
            "math": math,
        }
        resultado = eval(expresion, {"__builtins__": None}, permitidos)
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 💻 POWERSHELL — comandos reales
# ─────────────────────────────────────────
@tool
def ejecutar_powershell(comando: str) -> str:
    """
    Ejecuta comandos de PowerShell en Windows.
    Permitidos: Get-Date, Get-Process, Get-Service, Get-ChildItem,
    dir, ipconfig, ping, systeminfo, Get-ComputerInfo, whoami,
    Get-Disk, Get-Volume, tasklist, netstat.
    """
    permitidos = [
        "get-date", "get-process", "get-service", "get-childitem",
        "dir", "ipconfig", "ping", "systeminfo", "get-computerinfo",
        "whoami", "get-disk", "get-volume", "tasklist", "netstat",
        "get-content", "test-path", "resolve-path"
    ]

    comando_lower = comando.lower()
    if not any(cmd in comando_lower for cmd in permitidos):
        return f"Comando no permitido por seguridad: '{comando}'"

    try:
        resultado = subprocess.check_output(
            ["powershell", "-Command", comando],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace"
        )
        return resultado.strip() or "Comando ejecutado sin salida."
    except subprocess.TimeoutExpired:
        return "Error: el comando tardó demasiado (timeout 15s)."
    except subprocess.CalledProcessError as e:
        return f"Error PowerShell:\n{e.output}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 📂 LEER ARCHIVOS
# ─────────────────────────────────────────
@tool
def leer_archivo(ruta: str) -> str:
    """Lee el contenido de un archivo de texto del sistema."""
    try:
        ruta = os.path.abspath(ruta)
        if not os.path.exists(ruta):
            return f"El archivo no existe: {ruta}"
        if os.path.getsize(ruta) > 100_000:
            return "Archivo demasiado grande (>100KB). Usa una ruta más específica."
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            contenido = f.read()
        return f"Contenido de '{ruta}':\n\n{contenido}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# ✍️ ESCRIBIR ARCHIVOS
# ─────────────────────────────────────────
@tool
def escribir_archivo(ruta: str, contenido: str) -> str:
    """Crea o sobreescribe un archivo con el contenido dado."""
    try:
        ruta = os.path.abspath(ruta)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo guardado en: {ruta}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 📋 LISTAR DIRECTORIO
# ─────────────────────────────────────────
@tool
def listar_directorio(ruta: str = ".") -> str:
    """Lista archivos y carpetas de un directorio."""
    try:
        ruta = os.path.abspath(ruta)
        if not os.path.isdir(ruta):
            return f"No es un directorio válido: {ruta}"
        items = os.listdir(ruta)
        if not items:
            return f"Directorio vacío: {ruta}"
        resultado = [f"📁 Contenido de: {ruta}\n"]
        for item in sorted(items):
            full = os.path.join(ruta, item)
            tipo = "📁" if os.path.isdir(full) else "📄"
            resultado.append(f"  {tipo} {item}")
        return "\n".join(resultado)
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 🧠 MEMORIA
# ─────────────────────────────────────────
@tool
def ver_historial(n_ultimos: int = 10) -> str:
    """Muestra las últimas N interacciones del historial de conversación."""
    return historial_como_texto(n_ultimos)

@tool
def borrar_historial() -> str:
    """Limpia todo el historial de conversaciones guardado."""
    return _limpiar()


# ─────────────────────────────────────────
# 🕐 FECHA Y HORA
# ─────────────────────────────────────────
@tool
def obtener_fecha_hora() -> str:
    """Retorna la fecha y hora actual del sistema."""
    ahora = datetime.now()
    return (
        f"Fecha: {ahora.strftime('%d/%m/%Y')}\n"
        f"Hora: {ahora.strftime('%H:%M:%S')}\n"
        f"Día: {ahora.strftime('%A')}"
    )