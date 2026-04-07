"""
agente_tienda.py - Agente IA para tienda de ropa
Especializado en ventas, atención al cliente y cierre de pedidos
"""

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Importar herramientas
from tools_tienda import (
    buscar_producto,
    verificar_stock,
    calcular_envio,
    consultar_politica,
    responder_faq,
    registrar_pedido,
    generar_carrito,
    obtener_contacto
)

# Cargar variables de entorno
load_dotenv()


def crear_agente_tienda():
    """
    Crea un agente especializado en ventas de ropa
    """

    # 🔑 Modelo LLM (Groq)
    llm = ChatGroq(
        model="llama3-8b-8192",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_retries=2
    )

    # 🛠️ Herramientas disponibles
    tools = [
        buscar_producto,
        verificar_stock,
        calcular_envio,
        consultar_politica,
        responder_faq,
        registrar_pedido,
        generar_carrito,
        obtener_contacto
    ]

    # 🧠 Prompt ReAct COMPLETO (corregido)
    prompt_template = """
Eres "Eli", la asistente virtual de Glamour Global, una tienda de ropa.

🎯 PERSONALIDAD:
- Amigable, cercana, persuasiva
- Hablas como una chica mexicana moderna
- Usas emojis de forma natural 😊
- Tu objetivo es vender

🛠️ HERRAMIENTAS DISPONIBLES:
{tools}

Puedes usar estas herramientas:
{tool_names}

📋 REGLAS:
- Nunca inventes datos
- Usa herramientas para productos, stock o envíos
- Siempre intenta cerrar la venta
- Pregunta talla y ciudad cuando sea necesario

🧠 FORMATO OBLIGATORIO:

Pregunta: {input}
Pensamiento: analiza qué hacer
Acción: una de [{tool_names}]
Entrada de la acción: input para la herramienta
Observación: resultado
... (puedes repetir)
Pensamiento: ya tengo la respuesta
Respuesta final: respuesta final al cliente

---

📜 HISTORIAL:
{chat_history}

{agent_scratchpad}
"""

    prompt = PromptTemplate.from_template(prompt_template)

    # 🧠 Memoria (IMPORTANTE: texto, no mensajes)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False,
        input_key="input"
    )

    # 🤖 Crear agente ReAct
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # ⚙️ Executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=False
    )

    return executor


def responder_mensaje(agente, mensaje_usuario: str) -> str:
    """
    Responde un mensaje del usuario usando el agente
    """
    try:
        respuesta = agente.invoke({"input": mensaje_usuario})
        return respuesta.get("output", "Disculpa, no entendí bien 😅 ¿puedes repetir?")
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Ups, tuve un problema procesando tu mensaje 🤔 inténtalo de nuevo"
    