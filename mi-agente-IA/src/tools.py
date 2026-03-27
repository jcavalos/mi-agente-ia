from langchain_core.tools import tool
import subprocess
import math
import os
import re
import json
import requests
from datetime import date, datetime
from src.memory import historial_como_texto, limpiar_historial as _limpiar


# ─────────────────────────────────────────
# 🌐 BÚSQUEDA GENERAL
# ─────────────────────────────────────────
@tool
def buscar_en_internet(query: str) -> str:
    """
    Busca información actual en internet.
    Úsala para: precios, tipo de cambio, datos actuales, preguntas generales.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=6))
        if not resultados:
            return "Sin resultados para esa búsqueda."
        salida = []
        for i, r in enumerate(resultados, 1):
            salida.append(
                f"[{i}] {r.get('title', 'Sin título')}\n"
                f"    {r.get('body', '')}\n"
                f"    URL: {r.get('href', '')}"
            )
        return "\n\n".join(salida)
    except Exception as e:
        return f"Error al buscar: {str(e)}"


# ─────────────────────────────────────────
# 📰 NOTICIAS RECIENTES
# ─────────────────────────────────────────
@tool
def buscar_noticias(tema: str) -> str:
    """
    Busca noticias recientes sobre un tema específico.
    Úsala para: noticias del día, eventos recientes, actualidad.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            resultados = list(ddgs.news(tema, max_results=5))
        if not resultados:
            return f"No se encontraron noticias sobre: {tema}"
        salida = []
        for r in resultados:
            fecha = r.get("date", "fecha desconocida")
            salida.append(
                f"📰 {r.get('title', '')}\n"
                f"   Fecha: {fecha}\n"
                f"   {r.get('body', '')}\n"
                f"   Fuente: {r.get('source', '')} — {r.get('url', '')}"
            )
        return "\n\n".join(salida)
    except Exception as e:
        return f"Error buscando noticias: {str(e)}"


# ─────────────────────────────────────────
# 🔍 BÚSQUEDA PROFUNDA (múltiples fuentes)
# ─────────────────────────────────────────
@tool
def buscar_profundo(query: str) -> str:
    """
    Búsqueda profunda que combina resultados web + noticias + imágenes descriptivas.
    Úsala para investigaciones técnicas, comparativas, temas complejos.
    """
    try:
        from ddgs import DDGS
        resultado_final = []

        with DDGS() as ddgs:
            # Web general
            web = list(ddgs.text(query, max_results=4))
            if web:
                resultado_final.append("📌 RESULTADOS WEB:")
                for r in web:
                    resultado_final.append(
                        f"  • {r.get('title')}\n"
                        f"    {r.get('body', '')[:200]}\n"
                        f"    {r.get('href')}"
                    )

            # Noticias relacionadas
            news = list(ddgs.news(query, max_results=3))
            if news:
                resultado_final.append("\n📰 NOTICIAS RELACIONADAS:")
                for r in news:
                    resultado_final.append(
                        f"  • {r.get('title')} ({r.get('date', '')})\n"
                        f"    {r.get('body', '')[:150]}"
                    )

        return "\n".join(resultado_final) or "Sin resultados."
    except Exception as e:
        return f"Error en búsqueda profunda: {str(e)}"


# ─────────────────────────────────────────
# 🧮 CALCULADORA
# ─────────────────────────────────────────
@tool
def calcular(expresion: str) -> str:
    """Evalúa expresiones matemáticas. Soporta: sqrt, pow, abs, round, date, datetime."""
    try:
        permitidos = {
            "sqrt": math.sqrt, "pow": pow, "abs": abs,
            "round": round, "int": int, "float": float,
            "str": str, "date": date, "datetime": datetime,
            "math": math, "sum": sum, "min": min, "max": max,
        }
        resultado = eval(expresion, {"__builtins__": None}, permitidos)
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error en cálculo: {str(e)}"


# ─────────────────────────────────────────
# 💻 POWERSHELL
# ─────────────────────────────────────────
@tool
def ejecutar_powershell(comando: str) -> str:
    """
    Ejecuta comandos de PowerShell en Windows.
    Útil para: ver IP, procesos, servicios, info del sistema, archivos.
    Permitidos: ipconfig, ping, Get-Process, Get-Service, Get-ChildItem,
    systeminfo, whoami, tasklist, netstat, Get-Date, Get-ComputerInfo,
    Get-Disk, Get-Volume, dir, Get-Content, Test-Path.
    """
    permitidos = [
        "get-date", "get-process", "get-service", "get-childitem",
        "dir", "ipconfig", "ping", "systeminfo", "get-computerinfo",
        "whoami", "get-disk", "get-volume", "tasklist", "netstat",
        "get-content", "test-path", "resolve-path", "get-item",
        "get-location", "get-host", "get-culture"
    ]

    if not any(cmd in comando.lower() for cmd in permitidos):
        return f"Comando bloqueado: '{comando}'"

    try:
        resultado = subprocess.check_output(
            ["powershell", "-Command", comando],
            stderr=subprocess.STDOUT,
            text=True, timeout=20,
            encoding="utf-8", errors="replace"
        )
        salida = resultado.strip()
        if len(salida) > 3000:
            salida = salida[:3000] + "\n...(truncado)"
        return salida or "Ejecutado sin salida."
    except subprocess.TimeoutExpired:
        return "Timeout (20s)."
    except subprocess.CalledProcessError as e:
        return f"Error:\n{e.output}"
    except FileNotFoundError:
        return "PowerShell no encontrado."
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 📋 ANALIZAR LOGS
# ─────────────────────────────────────────
@tool
def analizar_log(ruta: str, n_lineas: int = 50) -> str:
    """
    Lee las últimas N líneas de un archivo de log y detecta errores críticos.
    Úsala para: revisar logs de aplicaciones, servidores, eventos de Windows.
    """
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            lineas = f.readlines()
        ultimas = lineas[-n_lineas:]
        errores = [l for l in ultimas if any(
            p in l.upper() for p in
            ["ERROR", "CRITICAL", "FATAL", "EXCEPTION", "FAIL", "DENIED"]
        )]
        resumen = f"📋 Log: {ruta}\n"
        resumen += f"Total líneas: {len(lineas)} | Analizadas: {n_lineas}\n"
        resumen += f"⚠️ Errores detectados: {len(errores)}\n\n"
        if errores:
            resumen += "── ERRORES ──\n" + "".join(errores[-10:])
        resumen += "\n── ÚLTIMAS 10 LÍNEAS ──\n" + "".join(ultimas[-10:])
        return resumen
    except FileNotFoundError:
        return f"Archivo no encontrado: {ruta}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 🖧 VERIFICAR SERVIDORES
# ─────────────────────────────────────────
@tool
def verificar_servidores(hosts: str) -> str:
    """
    Verifica conectividad de múltiples hosts separados por coma.
    Ejemplo: '8.8.8.8, google.com, 192.168.1.1'
    """
    lista = [h.strip() for h in hosts.split(",")]
    resultados = []
    for host in lista:
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", host],
                capture_output=True, text=True, timeout=5
            )
            estado = "✅ Online" if result.returncode == 0 else "❌ Offline"
        except Exception:
            estado = "❌ Error"
        resultados.append(f"{estado} — {host}")
    return "\n".join(resultados)


# ─────────────────────────────────────────
# 🔗 CONSULTAR API REST
# ─────────────────────────────────────────
@tool
def consultar_api(url: str, headers_json: str = "{}") -> str:
    """
    Hace GET a cualquier API REST y retorna el resultado.
    Útil para monitorear endpoints, APIs internas o públicas.
    """
    try:
        headers = json.loads(headers_json)
        headers.setdefault("User-Agent", "JARVIS-Agent/1.0")
        response = requests.get(url, headers=headers, timeout=10)
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            data = json.dumps(response.json(), indent=2, ensure_ascii=False)
        else:
            data = response.text
        if len(data) > 2000:
            data = data[:2000] + "\n...(truncado)"
        return f"Status: {response.status_code}\n\n{data}"
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 📊 REPORTE DEL SISTEMA
# ─────────────────────────────────────────
@tool
def generar_reporte_sistema(ruta_salida: str = "reportes/sistema.md") -> str:
    """
    Genera un reporte completo del sistema: info PC, top procesos RAM,
    servicios detenidos, conexiones de red. Lo guarda en un archivo .md.
    """
    comandos = {
        "Info del sistema": (
            "Get-ComputerInfo | Select-Object CsName, OsName, "
            "OsVersion, CsProcessors, "
            "@{N='RAM_GB';E={[math]::Round($_.CsTotalPhysicalMemory/1GB,2)}} "
            "| Format-List"
        ),
        "Top 10 procesos por RAM": (
            "Get-Process | Sort-Object WorkingSet -Descending "
            "| Select-Object -First 10 Name, CPU, "
            "@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB,1)}} "
            "| Format-Table -AutoSize"
        ),
        "Servicios automáticos detenidos": (
            "Get-Service | Where-Object "
            "{$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'} "
            "| Select-Object Name, DisplayName | Format-Table -AutoSize"
        ),
        "Conexiones establecidas": (
            "netstat -an | Select-String 'ESTABLISHED' | Select-Object -First 15"
        ),
        "Espacio en disco": (
            "Get-PSDrive -PSProvider FileSystem "
            "| Select-Object Name, "
            "@{N='Used_GB';E={[math]::Round($_.Used/1GB,2)}}, "
            "@{N='Free_GB';E={[math]::Round($_.Free/1GB,2)}} "
            "| Format-Table -AutoSize"
        ),
    }

    reporte = [
        f"# 📊 Reporte del Sistema\n",
        f"**Generado:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n",
        "---\n"
    ]

    for titulo, cmd in comandos.items():
        try:
            result = subprocess.check_output(
                ["powershell", "-Command", cmd],
                text=True, timeout=15,
                encoding="utf-8", errors="replace"
            )
            reporte.append(f"\n## {titulo}\n```\n{result.strip()[:800]}\n```\n")
        except Exception as e:
            reporte.append(f"\n## {titulo}\n⚠️ Error: {str(e)}\n")

    contenido = "\n".join(reporte)
    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)

    return f"✅ Reporte guardado: {os.path.abspath(ruta_salida)}\n\nPreview:\n{contenido[:400]}..."


# ─────────────────────────────────────────
# 📂 ARCHIVOS
# ─────────────────────────────────────────
@tool
def leer_archivo(ruta: str) -> str:
    """Lee el contenido de un archivo de texto."""
    try:
        ruta = os.path.abspath(ruta)
        if not os.path.exists(ruta):
            return f"No existe: {ruta}"
        if os.path.getsize(ruta) > 150_000:
            return "Archivo demasiado grande (>150KB)."
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            return f"📄 '{ruta}':\n\n{f.read()}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def escribir_archivo(ruta: str, contenido: str) -> str:
    """Crea o sobreescribe un archivo con el contenido dado."""
    try:
        ruta = os.path.abspath(ruta)
        directorio = os.path.dirname(ruta)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"✅ Guardado: {ruta}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def listar_directorio(ruta: str = ".") -> str:
    """Lista archivos y carpetas de un directorio con tamaños."""
    try:
        ruta = os.path.abspath(ruta)
        if not os.path.isdir(ruta):
            return f"No es directorio: {ruta}"
        items = sorted(os.listdir(ruta))
        if not items:
            return f"Vacío: {ruta}"
        lineas = [f"📁 {ruta}\n"]
        for item in items:
            full = os.path.join(ruta, item)
            if os.path.isdir(full):
                lineas.append(f"  📁 {item}/")
            else:
                kb = os.path.getsize(full) / 1024
                lineas.append(f"  📄 {item} ({kb:.1f} KB)")
        return "\n".join(lineas)
    except Exception as e:
        return f"Error: {str(e)}"


# ─────────────────────────────────────────
# 🌤️ CLIMA
# ─────────────────────────────────────────
@tool
def obtener_clima(ciudad: str) -> str:
    """
    Obtiene el clima actual de cualquier ciudad del mundo.
    Ejemplo: 'Ciudad de México', 'Guadalajara', 'Madrid'.
    """
    try:
        url = f"https://wttr.in/{ciudad.replace(' ', '+')}?format=4&lang=es"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"🌤️ Clima en {ciudad}:\n{response.text.strip()}"
        raise Exception(f"HTTP {response.status_code}")
    except Exception:
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                res = list(ddgs.text(f"clima hoy {ciudad}", max_results=2))
            if res:
                return f"🌤️ {ciudad}: {res[0].get('body', 'Sin datos')}"
        except Exception as e2:
            return f"Error obteniendo clima: {str(e2)}"
    return f"No se pudo obtener el clima de {ciudad}."


# ─────────────────────────────────────────
# 🔗 RESUMIR URL
# ─────────────────────────────────────────
@tool
def resumir_url(url: str) -> str:
    """
    Lee y extrae el texto principal de una URL/página web.
    Úsala cuando el usuario comparta un enlace.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        texto = response.text
        texto = re.sub(r'<script[^>]*>.*?</script>', '', texto, flags=re.DOTALL)
        texto = re.sub(r'<style[^>]*>.*?</style>', '', texto, flags=re.DOTALL)
        texto = re.sub(r'<[^>]+>', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        if len(texto) > 2500:
            texto = texto[:2500] + "..."
        return f"📄 {url}:\n\n{texto}"
    except Exception as e:
        return f"Error leyendo URL: {str(e)}"


# ─────────────────────────────────────────
# 🕐 FECHA Y HORA
# ─────────────────────────────────────────
@tool
def obtener_fecha_hora() -> str:
    """Retorna la fecha y hora actual del sistema."""
    ahora = datetime.now()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"]
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return (
        f"📅 {dias[ahora.weekday()]} {ahora.day} de "
        f"{meses[ahora.month]} de {ahora.year}\n"
        f"🕐 {ahora.strftime('%H:%M:%S')}"
    )


# ─────────────────────────────────────────
# 🧠 MEMORIA
# ─────────────────────────────────────────
@tool
def ver_historial(n_ultimos: int = 10) -> str:
    """Muestra las últimas N conversaciones guardadas."""
    return historial_como_texto(n_ultimos)


@tool
def borrar_historial() -> str:
    """Limpia todo el historial de conversaciones."""
    return _limpiar()