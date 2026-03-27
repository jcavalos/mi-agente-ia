import sys
from src.agent import crear_agente
from src.memory import (
    guardar_interaccion,
    historial_como_texto,
    limpiar_historial,
    cargar_historial
)
from langchain_core.messages import HumanMessage, AIMessage


AYUDA = """
╔══════════════════════════════════════════════════╗
║           JARVIS — COMANDOS DISPONIBLES          ║
╠══════════════════════════════════════════════════╣
║  /ayuda      → mostrar esta ayuda               ║
║  /historial  → ver conversaciones pasadas        ║
║  /limpiar    → borrar historial                  ║
║  /sistema    → reporte completo del sistema      ║
║  /buscar X   → búsqueda rápida de X             ║
║  /url X      → resumir contenido de URL X        ║
║  /clima X    → clima de ciudad X                 ║
║  /ping X,Y   → verificar hosts                  ║
║  /salir      → cerrar JARVIS                     ║
╚══════════════════════════════════════════════════╝

Ejemplos de preguntas:
  • "tipo de cambio USD a MXN hoy"
  • "analiza el log C:\\app\\error.log"
  • "busca vulnerabilidades críticas de esta semana"
  • "genera reporte del sistema y guárdalo"
  • "verifica si 8.8.8.8 y google.com responden"
"""


def procesar_comando_rapido(cmd: str) -> str | None:
    """Convierte comandos /slash en prompts naturales para el agente."""
    cmd = cmd.strip()
    if cmd == "/ayuda":
        return None  # se maneja aparte
    if cmd == "/historial":
        return None
    if cmd == "/limpiar":
        return None
    if cmd == "/sistema":
        return "genera un reporte completo del sistema y guárdalo en reportes/sistema.md"
    if cmd.startswith("/buscar "):
        query = cmd[8:].strip()
        return f"haz una búsqueda profunda sobre: {query}"
    if cmd.startswith("/url "):
        url = cmd[5:].strip()
        return f"resume el contenido de esta URL: {url}"
    if cmd.startswith("/clima "):
        ciudad = cmd[7:].strip()
        return f"dime el clima actual de {ciudad}"
    if cmd.startswith("/ping "):
        hosts = cmd[6:].strip()
        return f"verifica la conectividad de estos hosts: {hosts}"
    return cmd  # no es comando slash, es texto normal


def main():
    agent = crear_agente()
    historial_sesion = []

    print(AYUDA)
    print("─" * 50)

    while True:
        try:
            entrada = input("\n💬 Tú: ").strip()

            if not entrada:
                continue

            # ── Comandos que no van al agente ──
            if entrada.lower() in ["/salir", "salir", "exit", "quit"]:
                print("\n👋 JARVIS desconectado.")
                break

            if entrada.lower() in ["/ayuda", "ayuda", "help"]:
                print(AYUDA)
                continue

            if entrada.lower() in ["/historial", "historial"]:
                print("\n📋 HISTORIAL:\n")
                print(historial_como_texto(20))
                continue

            if entrada.lower() in ["/limpiar", "limpiar"]:
                print(limpiar_historial())
                historial_sesion = []
                continue

            # ── Convertir comandos slash ──
            prompt = procesar_comando_rapido(entrada)
            if prompt is None:
                continue

            # ── Invocar agente con historial de sesión ──
            estado = {
                "messages": historial_sesion + [
                    HumanMessage(content=prompt)
                ]
            }

            print("\n⚙️  Procesando...", end="\r")
            respuesta = agent.invoke(estado)
            mensajes = respuesta.get("messages", [])
            respuesta_texto = (
                mensajes[-1].content if mensajes else "Sin respuesta."
            )

            print(f"\n🤖 JARVIS:\n{respuesta_texto}\n")

            # ── Actualizar historial de sesión (últimos 5 turnos) ──
            historial_sesion.append(HumanMessage(content=prompt))
            historial_sesion.append(AIMessage(content=respuesta_texto))
            historial_sesion = historial_sesion[-10:]

            # ── Guardar en disco ──
            guardar_interaccion(usuario=entrada, agente=respuesta_texto)

        except KeyboardInterrupt:
            print("\n\n⛔ Interrumpido. Escribe /salir para cerrar.")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


# ── Modo no interactivo: python -m src.main "tarea aquí" ──
if __name__ == "__main__":
    if len(sys.argv) > 1:
        tarea = " ".join(sys.argv[1:])
        agent = crear_agente()
        estado = {"messages": [HumanMessage(content=tarea)]}
        respuesta = agent.invoke(estado)
        mensajes = respuesta.get("messages", [])
        print(mensajes[-1].content if mensajes else "Sin respuesta.")
    else:
        main()