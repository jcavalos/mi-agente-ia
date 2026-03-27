from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os, shutil, uuid
from datetime import datetime

from src.agent import crear_agente
from src.rag import indexar_documentos
from src.memory import guardar_interaccion, cargar_historial, limpiar_historial
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="JARVIS — Soporte IT + Dev", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Agente único compartido (thread-safe con LangGraph)
agent = crear_agente()

# Sesiones por usuario (en memoria — para producción usar Redis)
sesiones: dict[str, list] = {}


class Mensaje(BaseModel):
    mensaje: str
    usuario_id: str = "default"


class RespuestaChat(BaseModel):
    respuesta: str
    usuario_id: str
    timestamp: str
    fuentes: list[str] = []


@app.get("/")
async def root():
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"status": "JARVIS API activa", "docs": "/docs"}


@app.post("/chat", response_model=RespuestaChat)
async def chat(msg: Mensaje):
    try:
        # obtener o crear sesión del usuario
        if msg.usuario_id not in sesiones:
            sesiones[msg.usuario_id] = []

        historial = sesiones[msg.usuario_id]

        estado = {
            "messages": historial + [HumanMessage(content=msg.mensaje)]
        }

        respuesta = agent.invoke(estado)
        mensajes = respuesta.get("messages", [])
        texto = mensajes[-1].content if mensajes else "Sin respuesta."

        # actualizar sesión (últimos 10 mensajes)
        historial.append(HumanMessage(content=msg.mensaje))
        historial.append(AIMessage(content=texto))
        sesiones[msg.usuario_id] = historial[-10:]

        # guardar en disco con id de usuario
        guardar_interaccion(
            usuario=f"[{msg.usuario_id}] {msg.mensaje}",
            agente=texto
        )

        return RespuestaChat(
            respuesta=texto,
            usuario_id=msg.usuario_id,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/subir-documento")
async def subir_documento(
    archivo: UploadFile = File(...),
    tipo: str = Form(default="auto")
):
    """Sube un documento y lo agrega a la base de conocimiento."""
    try:
        # detectar carpeta por tipo
        carpetas = {
            "pdf": "documentos/pdfs",
            "ticket": "documentos/tickets",
            "codigo": "documentos/codigo",
            "correo": "documentos/correos",
            "auto": "documentos",
        }
        carpeta = carpetas.get(tipo, "documentos")
        os.makedirs(carpeta, exist_ok=True)

        ruta = os.path.join(carpeta, archivo.filename)
        with open(ruta, "wb") as f:
            shutil.copyfileobj(archivo.file, f)

        return {
            "mensaje": f"✅ Archivo '{archivo.filename}' subido correctamente",
            "ruta": ruta,
            "siguiente": "Llama a POST /indexar para actualizar la base de conocimiento"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/indexar")
async def indexar():
    """Re-indexa todos los documentos de la carpeta documentos/"""
    try:
        resultado = indexar_documentos()
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sesiones")
async def ver_sesiones():
    return {
        "sesiones_activas": len(sesiones),
        "usuarios": list(sesiones.keys())
    }


@app.delete("/sesion/{usuario_id}")
async def limpiar_sesion(usuario_id: str):
    if usuario_id in sesiones:
        del sesiones[usuario_id]
    return {"mensaje": f"Sesión de {usuario_id} limpiada"}


@app.get("/historial")
async def historial():
    return {"historial": cargar_historial()}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agente": "activo",
        "sesiones": len(sesiones),
        "timestamp": datetime.now().isoformat()
    }