from langchain.tools import tool
from duckduckgo_search import DDGS

@tool
def buscar_en_internet(query: str) -> str:
    """Busca información actual en internet usando DuckDuckGo."""
    with DDGS() as ddgs:
        resultados = list(ddgs.text(query, max_results=3))
    if not resultados:
        return "No encontré resultados."
    return "\n\n".join(
        f"Título: {r['title']}\nResumen: {r['body']}"
        for r in resultados
    )

@tool
def calcular(expresion: str) -> str:
    """Evalúa una expresión matemática. Ejemplo: '2 + 2 * 10'"""
    try:
        resultado = eval(expresion, {"__builtins__": {}})
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error al calcular: {e}"