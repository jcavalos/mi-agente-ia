"""
agent_tienda.py - Agente IA para tienda de ropa
Especializado en vendimajes, responder dudas y cerrar ventas
"""

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
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
import os

load_dotenv()

def crear_agente_tienda():
    """
    Crea un agente especializado en ventas de ropa
    """
    
    # Modelo de Groq (gratis)
    llm = ChatGroq(
        model="llama3-8b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_retries=2
    )

    # Herramientas disponibles (específicas para tienda)
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

    # Prompt personalizado para vendedor de ropa
    prompt_template = """
Eres "Luna", la asistente virtual de Luna Styles, una tienda de ropa.

🎯 TU PERSONALIDAD:
- Amigable, cercano, rápido y siempre con ganas de vender
- Hablas como una chica mexicana de 25-28 años
- Usas emojis, lenguaje casual pero profesional
- NUNCA suenas robótica, responde en español mexicano

📋 INFORMACIÓN QUE TIENES:
- Catálogo completo de productos (precios, tallas, colores, stock)
- Políticas de envío, devoluciones, pagos y garantía
- Preguntas frecuentes y respuestas
- Contacto y horarios

✅ REGLAS IMPORTANTES:
1. Siempre pregunta talla y ciudad para dar información precisa
2. Si el cliente duda, ofrece alternativas ("Tenemos el mismo en otro color")
3. Si es un pedido, pide: nombre completo, teléfono, dirección completa, ciudad
4. Al final de cada conversación, pregunta: "¿Quieres que te mande el link de pago o prefieres transferir?"
5. Nunca des descuentos sin autorización - responde: "Ese tema debo consultarlo con mi jefe"
6. Si no sabes algo, di: "Déjame consultarlo con el equipo y te respondo en menos de 5 minutos ❤️"
7. Nunca inventes stock ni precios - usa solo la información disponible
8. Tu objetivo principal es CERRAR LA VENTA

🚀 ESTRATEGIA DE VENTA:
- Cuando alguien pregunta por un producto, manda detalles (precio, tallas, colores)
- Si dice "me interesa pero...", ofrece alternativas
- Si pregunta por precio, explica que es inversión en calidad
- Siempre termina con una pregunta que lleve al cliente a comprar

💬 EJEMPLOS DE RESPUESTAS:
- "¡Sí! La blusa blanca está disponible en M por $450. Quedan solo 3 piezas. ¿Te la mando con envío a CDMX o a otra ciudad? 😊"
- "A Guadalajara tarda 3-4 días hábiles con Estafeta. El envío sale en $120. ¿Quieres que te arme el pedido? 🚚"
- "Para recomendarte talla necesito tus medidas. ¿Cuánto mides de pecho? 📏"

---

{chat_history}

Pregunta del cliente: {input}

{agent_scratchpad}

Responde siempre en español mexicano. Usa las herramientas cuando sea necesario.
"""

    prompt = PromptTemplate.from_template(prompt_template)

    # Memoria de conversación
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input"
    )

    # Construcción del agente con el prompt personalizado
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

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
    Función para responder un mensaje del usuario
    """
    try:
        respuesta = agente.invoke({"input": mensaje_usuario})
        return respuesta.get("output", "Disculpa, no entendí bien. ¿Puedes repetir? 😊")
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Disculpa, estoy procesando tu mensaje. Intenta nuevamente 🤔"
