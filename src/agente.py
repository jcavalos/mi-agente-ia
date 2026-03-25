from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from dotenv import load_dotenv
from src.tools import buscar_en_internet, calcular
import os

load_dotenv()

def crear_agente():
    # Modelo de Groq (gratis)
    llm = ChatGroq(
        model="llama3-8b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )

    # Herramientas disponibles
    tools = [buscar_en_internet, calcular]

    # Prompt estándar de ReAct (razonamiento + acción)
    prompt = hub.pull("hwchase17/react-chat")

    # Memoria de conversación
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Construcción del agente
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    return executor