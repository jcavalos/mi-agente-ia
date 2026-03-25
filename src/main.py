from src.agent import crear_agente

def main():
    print("=" * 50)
    print("  Agente IA con LangChain + Groq (gratis)")
    print("  Escribe 'salir' para terminar")
    print("=" * 50)

    agente = crear_agente()

    while True:
        pregunta = input("\nTu: ").strip()
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Hasta luego!")
            break
        if not pregunta:
            continue
        try:
            respuesta = agente.invoke({"input": pregunta})
            print(f"\nAgente: {respuesta['output']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()