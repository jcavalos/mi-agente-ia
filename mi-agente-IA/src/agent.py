from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import time

from src.tools import *

load_dotenv()

MEMORY_FILE = "memory.json"

SYSTEM_PROMPT = """Eres AVALOS, un agente autónomo avanzado.

Tu objetivo es resolver tareas COMPLETAS de forma autónoma.

Siempre:
1. Piensa
2. Decide acción
3. Ejecuta herramienta si es necesario
4. Evalúa resultado
5. Continúa hasta terminar

Responde SIEMPRE en JSON:

{
  "thought": "...",
  "action": "nombre_tool o final",
  "input": "parametros",
  "final_answer": "respuesta final si termina"
}
"""


# 🧠 MEMORIA
def cargar_memoria():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_memoria(memoria):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria[-20:], f, indent=2)  # 🔥 limita tamaño


#  TOOL DISPATCHER
TOOLS = {
    "buscar_en_internet": buscar_en_internet,
    "buscar_noticias": buscar_noticias,
    "buscar_profundo": buscar_profundo,
    "calcular": calcular,
    "ejecutar_powershell": ejecutar_powershell,
    "leer_archivo": leer_archivo,
    "escribir_archivo": escribir_archivo,
    "listar_directorio": listar_directorio,
    "ver_historial": ver_historial,
    "borrar_historial": borrar_historial,
    "obtener_fecha_hora": obtener_fecha_hora,
    "obtener_clima": obtener_clima,
    "resumir_url": resumir_url,
    "analizar_log": analizar_log,
    "verificar_servidores": verificar_servidores,
    "consultar_api": consultar_api,
    "generar_reporte_sistema": generar_reporte_sistema,
}


def ejecutar_tool(nombre, entrada):
    try:
        if nombre not in TOOLS:
            return f"Error: tool {nombre} no existe"

        return TOOLS[nombre](entrada)

    except Exception as e:
        return f"Error ejecutando tool: {str(e)}"


# 🤖 AGENTE AUTÓNOMO
class AutoGPT:
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),  # 🔥 optimizado
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
            max_tokens=500,  # 🔥 evita 429
        )

        self.memoria = cargar_memoria()

    def run(self, objetivo, max_steps=6):
        print(f"\n🎯 Objetivo: {objetivo}\n")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": objetivo}
        ]

        for step in range(max_steps):
            print(f"\n⚙️ Paso {step + 1}")

            try:
                response = self.llm.invoke(messages)
                content = response.content

                print("🧠 RAW:", content)

                data = json.loads(content)

            except Exception as e:
                print("❌ Error parseando respuesta:", e)
                break

            thought = data.get("thought")
            action = data.get("action")
            input_data = data.get("input")
            final_answer = data.get("final_answer")

            print(f"🧠 Pensamiento: {thought}")
            print(f"⚙️ Acción: {action}")

            # 🏁 FINAL
            if action == "final":
                print("\n✅ RESULTADO FINAL:\n")
                print(final_answer)

                self.memoria.append({
                    "objetivo": objetivo,
                    "resultado": final_answer
                })
                guardar_memoria(self.memoria)

                return final_answer

            # 🔧 EJECUTAR TOOL
            resultado = ejecutar_tool(action, input_data)

            print(f"🔧 Resultado tool: {resultado}")

            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": f"Resultado de la tool: {resultado}"
            })

            time.sleep(1)  # evita rate limit

        print("\n⚠️ No se completó en pasos máximos")
        return None


# 🚀 FACTORY
def crear_agente():
    print("🔥 AVALOS AUTO-GPT ACTIVADO")
    print("Modo: Autónomo real")
    print("Memoria: persistente")
    print("Loop: activo\n")

    return AutoGPT()