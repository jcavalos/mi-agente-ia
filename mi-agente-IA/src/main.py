from langchain_core.messages import HumanMessage, AIMessage
from src.agent import crear_agente

def main():
    agente = crear_agente()
    chat_history = []

    while True:
        pregunta = input("Tú: ")

        if pregunta.lower() in ["salir", "exit"]:
            break

        chat_history.append(HumanMessage(content=pregunta))

        respuesta = agente.invoke({
            "messages": chat_history
        })

        print("🤖:", respuesta["messages"][-1].content)

        chat_history.append(
            AIMessage(content=respuesta["messages"][-1].content)
        )

if __name__ == "__main__":
    main()