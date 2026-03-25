# Agente IA con LangChain + Groq

Agente conversacional inteligente con memoria, búsqueda web y cálculos. Construido con Python, LangChain y Llama 3 

## Tecnologías
- Python 3.10+
- LangChain (framework de agentes)
- Groq API (LLM gratuito — Llama 3)
- DuckDuckGo Search (búsqueda sin API key)

## Capacidades
- Responde preguntas con razonamiento paso a paso
- Busca información actual en internet
- Realiza cálculos matemáticos
- Recuerda el historial de la conversación

## Instalación

1. Clona el repositorio
   git clone https://github.com/tu-usuario/mi-agente-ia

2. Instala dependencias
   pip install -r requirements.txt

3. Crea tu .env con tu API key de Groq
   GROQ_API_KEY=tu_clave_aqui

4. Ejecuta el agente
   python -m src.main

5. Ahora que ya controlas el agente, podemos: (ESTO ES LO FALTA)

    agregar tools reales (PowerShell, archivos)
    memoria persistente
    convertirlo en API
    hacerlo autónomo (multi-step tasks)