import os
import json
from datetime import datetime
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_core.documents import Document

VECTORSTORE_PATH = "memoria/vectorstore"
DOCUMENTOS_DIR = "documentos"
INDEX_LOG = "memoria/index_log.json"

# ─────────────────────────────────────────
# Embeddings (modelo multilingüe español/inglés)
# ─────────────────────────────────────────
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


# ─────────────────────────────────────────
# Cargadores por tipo de archivo
# ─────────────────────────────────────────
def cargar_pdf(ruta: str) -> list[Document]:
    try:
        import fitz  # pymupdf
        doc = fitz.open(ruta)
        docs = []
        for i, page in enumerate(doc):
            texto = page.get_text()
            if texto.strip():
                docs.append(Document(
                    page_content=texto,
                    metadata={
                        "source": ruta,
                        "tipo": "pdf",
                        "pagina": i + 1,
                        "archivo": Path(ruta).name
                    }
                ))
        return docs
    except Exception as e:
        print(f"  ⚠️ Error PDF {ruta}: {e}")
        return []


def cargar_texto(ruta: str, tipo: str = "texto") -> list[Document]:
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            contenido = f.read()
        if not contenido.strip():
            return []
        return [Document(
            page_content=contenido,
            metadata={
                "source": ruta,
                "tipo": tipo,
                "archivo": Path(ruta).name
            }
        )]
    except Exception as e:
        print(f"  ⚠️ Error {ruta}: {e}")
        return []


def cargar_correo(ruta: str) -> list[Document]:
    """Carga correos en formato .txt o .eml"""
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            contenido = f.read()
        # extraer campos básicos si es formato email
        lineas = contenido.split("\n")
        metadata = {"source": ruta, "tipo": "correo", "archivo": Path(ruta).name}
        for linea in lineas[:10]:
            if linea.lower().startswith("from:"):
                metadata["de"] = linea[5:].strip()
            elif linea.lower().startswith("subject:") or linea.lower().startswith("asunto:"):
                metadata["asunto"] = linea.split(":", 1)[1].strip()
            elif linea.lower().startswith("date:") or linea.lower().startswith("fecha:"):
                metadata["fecha"] = linea.split(":", 1)[1].strip()
        return [Document(page_content=contenido, metadata=metadata)]
    except Exception as e:
        print(f"  ⚠️ Error correo {ruta}: {e}")
        return []


def cargar_ticket(ruta: str) -> list[Document]:
    """Carga tickets en .txt, .md o .json"""
    try:
        if ruta.endswith(".json"):
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            # soporta lista de tickets o ticket individual
            if isinstance(data, list):
                docs = []
                for ticket in data:
                    texto = json.dumps(ticket, ensure_ascii=False, indent=2)
                    docs.append(Document(
                        page_content=texto,
                        metadata={
                            "source": ruta,
                            "tipo": "ticket",
                            "ticket_id": ticket.get("id", ""),
                            "estado": ticket.get("estado", ""),
                            "archivo": Path(ruta).name
                        }
                    ))
                return docs
            else:
                texto = json.dumps(data, ensure_ascii=False, indent=2)
                return [Document(
                    page_content=texto,
                    metadata={"source": ruta, "tipo": "ticket",
                              "archivo": Path(ruta).name}
                )]
        else:
            return cargar_texto(ruta, tipo="ticket")
    except Exception as e:
        print(f"  ⚠️ Error ticket {ruta}: {e}")
        return []


# ─────────────────────────────────────────
# Indexador principal
# ─────────────────────────────────────────
def indexar_documentos(directorio: str = DOCUMENTOS_DIR) -> str:
    """
    Escanea la carpeta documentos/ y sus subcarpetas,
    detecta el tipo de archivo y lo indexa en FAISS.
    """
    os.makedirs("memoria", exist_ok=True)
    os.makedirs(directorio, exist_ok=True)

    # crear subcarpetas si no existen
    for sub in ["pdfs", "tickets", "codigo", "correos"]:
        os.makedirs(os.path.join(directorio, sub), exist_ok=True)

    print(f"\n📂 Escaneando {directorio}...")
    todos_docs = []
    conteo = {"pdf": 0, "codigo": 0, "ticket": 0, "correo": 0, "otro": 0}

    extensiones = {
        ".pdf": ("pdf", cargar_pdf),
        ".py": ("codigo", lambda r: cargar_texto(r, "codigo")),
        ".js": ("codigo", lambda r: cargar_texto(r, "codigo")),
        ".ts": ("codigo", lambda r: cargar_texto(r, "codigo")),
        ".java": ("codigo", lambda r: cargar_texto(r, "codigo")),
        ".cs": ("codigo", lambda r: cargar_texto(r, "codigo")),
        ".txt": ("otro", lambda r: cargar_texto(r, "texto")),
        ".md": ("otro", lambda r: cargar_texto(r, "texto")),
        ".json": ("ticket", cargar_ticket),
        ".eml": ("correo", cargar_correo),
        ".log": ("ticket", lambda r: cargar_texto(r, "log")),
    }

    # detectar tipo por carpeta padre también
    carpeta_tipo = {
        "pdfs": "pdf",
        "tickets": "ticket",
        "codigo": "codigo",
        "correos": "correo",
    }

    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            ext = Path(archivo).suffix.lower()

            # detectar por carpeta padre
            carpeta = Path(raiz).name.lower()
            if carpeta in carpeta_tipo and ext in [".txt", ".md"]:
                tipo_forzado = carpeta_tipo[carpeta]
                if tipo_forzado == "ticket":
                    docs = cargar_ticket(ruta)
                elif tipo_forzado == "correo":
                    docs = cargar_correo(ruta)
                else:
                    docs = cargar_texto(ruta, tipo_forzado)
                conteo[tipo_forzado] = conteo.get(tipo_forzado, 0) + len(docs)
                todos_docs.extend(docs)
                continue

            if ext in extensiones:
                tipo, cargador = extensiones[ext]
                docs = cargador(ruta)
                if docs:
                    conteo[tipo] = conteo.get(tipo, 0) + len(docs)
                    todos_docs.extend(docs)
                    print(f"  ✅ [{tipo}] {archivo} — {len(docs)} fragmento(s)")

    if not todos_docs:
        return "⚠️ No se encontraron documentos para indexar. Agrega archivos a la carpeta documentos/"

    print(f"\n✂️ Dividiendo en chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(todos_docs)
    print(f"   {len(chunks)} chunks generados de {len(todos_docs)} documentos")

    print(f"\n🧠 Generando embeddings (puede tardar 1-2 min)...")
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)

    # guardar log de indexación
    log = {
        "fecha": datetime.now().isoformat(),
        "total_docs": len(todos_docs),
        "total_chunks": len(chunks),
        "conteo_por_tipo": conteo
    }
    with open(INDEX_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    resumen = (
        f"\n✅ INDEXACIÓN COMPLETA\n"
        f"   📄 PDFs      : {conteo.get('pdf', 0)} fragmentos\n"
        f"   🎫 Tickets   : {conteo.get('ticket', 0)} fragmentos\n"
        f"   💻 Código    : {conteo.get('codigo', 0)} fragmentos\n"
        f"   📧 Correos   : {conteo.get('correo', 0)} fragmentos\n"
        f"   📝 Otros     : {conteo.get('otro', 0)} fragmentos\n"
        f"   🔢 Total chunks: {len(chunks)}\n"
        f"   💾 Guardado en: {VECTORSTORE_PATH}"
    )
    print(resumen)
    return resumen


# ─────────────────────────────────────────
# TOOLS para el agente
# ─────────────────────────────────────────
@tool
def buscar_en_documentos(query: str) -> str:
    """
    Busca en documentos internos indexados: PDFs, procedimientos,
    manuales, tickets de soporte, código fuente y correos.
    SIEMPRE úsala antes de buscar en internet para preguntas
    sobre procedimientos internos, errores conocidos o políticas.
    """
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return "⚠️ Base de documentos no inicializada. Ejecuta /indexar primero."
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        resultados = vectorstore.similarity_search_with_score(query, k=5)
        if not resultados:
            return "No encontré información relevante en los documentos internos."

        salida = [f"📚 Resultados en documentos internos para: '{query}'\n"]
        for i, (doc, score) in enumerate(resultados, 1):
            relevancia = round((1 - score) * 100, 1)
            meta = doc.metadata
            tipo = meta.get("tipo", "doc")
            fuente = meta.get("archivo", meta.get("source", "desconocido"))
            pagina = f" p.{meta.get('pagina', '')}" if meta.get("pagina") else ""
            asunto = f" | Asunto: {meta.get('asunto', '')}" if meta.get("asunto") else ""

            salida.append(
                f"[{i}] 📎 {tipo.upper()} — {fuente}{pagina}{asunto}\n"
                f"    Relevancia: {relevancia}%\n"
                f"    {doc.page_content[:400]}\n"
            )
        return "\n".join(salida)
    except Exception as e:
        return f"Error buscando en documentos: {str(e)}"


@tool
def buscar_tickets_similares(problema: str) -> str:
    """
    Busca tickets de soporte anteriores similares al problema descrito.
    Úsala para: encontrar soluciones ya aplicadas, errores conocidos,
    problemas recurrentes.
    """
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return "⚠️ Base no inicializada."
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH, embeddings,
            allow_dangerous_deserialization=True
        )
        # buscar solo en tickets
        resultados = vectorstore.similarity_search(
            problema,
            k=8,
            filter={"tipo": "ticket"}
        )
        if not resultados:
            # si no hay tickets, busca en todo
            resultados = vectorstore.similarity_search(problema, k=4)

        if not resultados:
            return "No se encontraron tickets similares."

        salida = [f"🎫 Tickets similares al problema: '{problema}'\n"]
        for i, doc in enumerate(resultados[:5], 1):
            salida.append(
                f"[{i}] {doc.metadata.get('archivo', 'ticket')}\n"
                f"    {doc.page_content[:300]}\n"
            )
        return "\n".join(salida)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def buscar_en_codigo(query: str) -> str:
    """
    Busca en el código fuente indexado: funciones, clases, errores,
    patrones de código, implementaciones específicas.
    Úsala cuando el usuario pregunte cómo está implementado algo
    o busque un fragmento de código específico.
    """
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return "⚠️ Base no inicializada."
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH, embeddings,
            allow_dangerous_deserialization=True
        )
        resultados = vectorstore.similarity_search(
            query, k=5,
            filter={"tipo": "codigo"}
        )
        if not resultados:
            resultados = vectorstore.similarity_search(query, k=3)

        if not resultados:
            return "No se encontró código relacionado."

        salida = [f"💻 Código encontrado para: '{query}'\n"]
        for i, doc in enumerate(resultados, 1):
            archivo = doc.metadata.get("archivo", "código")
            salida.append(
                f"[{i}] 📄 {archivo}\n"
                f"```\n{doc.page_content[:500]}\n```\n"
            )
        return "\n".join(salida)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def estado_base_conocimiento() -> str:
    """Muestra el estado actual de la base de conocimiento indexada."""
    try:
        if not os.path.exists(INDEX_LOG):
            return "⚠️ Base no inicializada. Usa /indexar para comenzar."
        with open(INDEX_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
        fecha = log.get("fecha", "")[:16].replace("T", " ")
        conteo = log.get("conteo_por_tipo", {})
        return (
            f"📊 BASE DE CONOCIMIENTO\n"
            f"   Última actualización: {fecha}\n"
            f"   Total documentos   : {log.get('total_docs', 0)}\n"
            f"   Total chunks       : {log.get('total_chunks', 0)}\n"
            f"   ├─ PDFs            : {conteo.get('pdf', 0)}\n"
            f"   ├─ Tickets         : {conteo.get('ticket', 0)}\n"
            f"   ├─ Código          : {conteo.get('codigo', 0)}\n"
            f"   ├─ Correos         : {conteo.get('correo', 0)}\n"
            f"   └─ Otros           : {conteo.get('otro', 0)}\n"
        )
    except Exception as e:
        return f"Error: {str(e)}"