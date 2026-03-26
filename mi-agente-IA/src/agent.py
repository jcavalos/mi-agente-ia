from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os

from src.tools import (
    buscar_en_internet,
    calcular,
    ejecutar_powershell,
    leer_archivo,
    escribir_archivo,
    listar_directorio,
    ver_historial,
    borrar_historial,
    obtener_fecha_hora,
)

load_dotenv()

SYSTEM_PROMPT = """Eres un agente autónomo inteligente con acceso a herramientas reales.

CAPACIDADES:
- Buscar información actual en internet
- Ejecutar comandos de PowerShell en Windows
- Leer y escribir archivos
- Realizar cálculos matemáticos
- Recordar conversaciones pasadas
- Conocer la fecha y hora actual

COMPORTAMIENTO AUTÓNOMO:
- Descompón tareas complejas en pasos y ejecútalos uno por uno
- Usa múltiples herramientas en secuencia si es necesario
- Si una herramienta falla, intenta con otra estrategia
- Siempre confirma los resultados antes de responder al usuario
- Si no tienes información suficiente, busca en internet

MEMORIA:
- Tienes acceso al historial de conversaciones anteriores
- Úsalo para dar respuestas contextualizadas

Responde siempre en español, de forma clara y directa."""


def crear_agente():
    print("🔥 AGENTE AUTÓNOMO INICIADO 🔥")
    print(f"Modelo: llama-3.1-8b-instant")
    print(f"Tools: búsqueda, PowerShell, archivos, memoria, calculadora\n")

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.6,
    )

    tools = [
        buscar_en_internet,
        calcular,
        ejecutar_powershell,
        leer_archivo,
        escribir_archivo,
        listar_directorio,
        ver_historial,
        borrar_historial,
        obtener_fecha_hora,
    ]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent