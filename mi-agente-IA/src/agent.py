from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from src.tools import buscar_en_internet, calcular
import os

load_dotenv()

def crear_agente():
    print("🔥 ESTE ES EL AGENT CORRECTO 🔥")
    print("Modelo:", "llama-3.1-8b-instant")
    print("Archivo:", __file__)

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.6,
    )

    tools = [buscar_en_internet, calcular]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="Eres un asistente útil que puede buscar en internet y hacer cálculos."
    )

    return agent