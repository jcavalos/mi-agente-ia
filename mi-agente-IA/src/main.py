from src.agent import crear_agente
from src.memory import guardar_interaccion, historial_como_texto
from langchain_core.messages import HumanMessage, SystemMessage

def construir_estado(objetivo: str, historial_previo: list) -> dict:
    """Construye el estado con historial incluido para memoria persistente."""
    # Inyectar historial como contexto en el primer mensaje
    contexto_historial = historial_como_texto(n_ultimos=8)

    mensaje_con_contexto = (
        f"[HISTORIAL RECIENTE]\n{contexto_historial}\n\n"
        f"[NUEVO OBJETIVO]\n{objetivo}"
    )

    mensajes = historial_previo + [
        HumanMessage(content=mensaje_con_contexto)
    ]

    return {"messages": mensajes}


def main():
    agent = crear_agente()
    historial_sesion = []  # historial en memoria RAM para la sesión actual

    print("💡 Comandos especiales:")
    print("  'historial' → ver conversaciones pasadas")
    print("  'limpiar'   → borrar historial")
    print("  'salir'     → terminar\n")

    while True:
        try:
            objetivo = input("🎯 Tú: ").strip()

            if not objetivo:
                continue

            if objetivo.lower() == "salir":
                print("👋 Hasta luego!")
                break

            if objetivo.lower() == "historial":
                print("\n📋 Historial:\n", historial_como_texto(20), "\n")
                continue

            if objetivo.lower() == "limpiar":
                from src.memory import limpiar_historial
                print(limpiar_historial())
                historial_sesion = []
                continue

            # Construir estado con historial
            estado = construir_estado(objetivo, historial_sesion)

            # Invocar agente
            respuesta = agent.invoke(estado)

            # Extraer respuesta final
            mensajes = respuesta.get("messages", [])
            respuesta_texto = ""
            if mensajes:
                ultimo = mensajes[-1]
                respuesta_texto = ultimo.content
                print(f"\n🤖 Agente: {respuesta_texto}\n")
            else:
                print("\n🤖 Sin respuesta\n")

            # Guardar en historial de sesión (solo user + assistant)
            historial_sesion.append(HumanMessage(content=objetivo))
            if respuesta_texto:
                from langchain_core.messages import AIMessage
                historial_sesion.append(AIMessage(content=respuesta_texto))

            # Mantener solo los últimos 6 mensajes en RAM
            historial_sesion = historial_sesion[-6:]

            # Guardar en disco
            guardar_interaccion(usuario=objetivo, agente=respuesta_texto)

        except KeyboardInterrupt:
            print("\n⛔ Detenido por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()