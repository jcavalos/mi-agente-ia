from langchain_core.tools import tool
from duckduckgo_search import DDGS

@tool
def buscar_en_internet(query: str) -> str:
    """Busca información actual en internet usando DuckDuckGo. Usa esto cuando necesites datos frescos."""
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=4))
        if not resultados:
            return "No encontré resultados para esa búsqueda."
        return "\n\n".join(
            f"Título: {r.get('title', 'Sin título')}\n"
            f"Resumen: {r.get('body', 'Sin resumen')}\n"
            f"Enlace: {r.get('href', '')}"
            for r in resultados
        )
    except Exception as e:
        return f"Error en la búsqueda: {str(e)}"

@tool
def calcular(expresion: str) -> str:
    """Evalúa una expresión matemática simple. Ejemplo: '2 * (3 + 5)' o '100 / 4'."""
    try:
        # Seguridad básica
        resultado = eval(expresion, {"__builtins__": {}}, {})
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error al calcular '{expresion}': {str(e)}"