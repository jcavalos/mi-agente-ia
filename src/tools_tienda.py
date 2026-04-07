"""
tools_tienda.py - Herramientas especializadas para la tienda de ropa
"""

from langchain.tools import tool
from config_negocio import CATALOGO, POLITICAS, PREGUNTAS_FRECUENTES, CONTACTO
import json

# ===== HERRAMIENTA: Buscar Productos =====
@tool
def buscar_producto(nombre_o_tipo: str) -> str:
    """
    Busca un producto en el catálogo por nombre o tipo.
    Ejemplo: "blusa blanca", "jeans", "vestido"
    """
    nombre_o_tipo = nombre_o_tipo.lower().strip()
    
    resultados = []
    for id_producto, datos in CATALOGO.items():
        if (nombre_o_tipo in datos["nombre"].lower() or 
            nombre_o_tipo in datos["descripcion"].lower() or
            nombre_o_tipo in datos["material"].lower()):
            resultados.append(datos)
    
    if not resultados:
        return "No encontré ese producto en nuestro catálogo. ¿Buscas ropa casual, formal, deportiva...? Cuéntame más 👗"
    
    respuesta = "Encontré estos productos:\n\n"
    for i, prod in enumerate(resultados, 1):
        respuesta += f"{i}. {prod['nombre']}\n"
        respuesta += f"   Precio: ${prod['precio']}\n"
        respuesta += f"   Tallas: {', '.join(prod['tallas'])}\n"
        respuesta += f"   Colores: {', '.join(prod['colores'])}\n"
        respuesta += f"   {prod['descripcion']}\n\n"
    
    return respuesta

# ===== HERRAMIENTA: Verificar Stock =====
@tool
def verificar_stock(producto: str, talla: str) -> str:
    """
    Verifica el stock disponible de un producto en una talla específica.
    Ejemplo: "blusa blanca", "M"
    """
    producto = producto.lower().strip()
    talla = talla.upper().strip()
    
    # Buscar el producto
    producto_encontrado = None
    for id_prod, datos in CATALOGO.items():
        if producto in datos["nombre"].lower() or producto in id_prod.lower():
            producto_encontrado = datos
            break
    
    if not producto_encontrado:
        return "No encontré ese producto. ¿Cuál es el nombre exacto? 🤔"
    
    # Verificar talla
    if talla not in producto_encontrado["stock"]:
        return f"Esa talla no disponible. Tengo estas: {', '.join(producto_encontrado['tallas'])} 📏"
    
    cantidad = producto_encontrado["stock"][talla]
    
    if cantidad == 0:
        return f"Lo siento, la talla {talla} se acabó. ¿Te interesa otra talla o color? 💔"
    elif cantidad <= 2:
        return f"¡Apúrate! Solo quedan {cantidad} piezas de talla {talla} 🔥"
    else:
        return f"Sí, hay {cantidad} disponibles de talla {talla}. ¿Te lo mando? ✅"

# ===== HERRAMIENTA: Calcular Costo de Envío =====
@tool
def calcular_envio(ciudad: str, producto: str = None) -> str:
    """
    Calcula el costo y tiempo de envío según la ciudad.
    Ejemplo: "CDMX", "Guadalajara", "Monterrey"
    """
    ciudad = ciudad.lower().strip()
    
    if "cdmx" in ciudad or "méxico" in ciudad or "mexico" in ciudad:
        return "📍 **CDMX**: Envío GRATIS en 1-2 días hábiles 🎉"
    
    # México (estados)
    ciudades_mexico = ["gdl", "guadalajara", "monterrey", "cancun", "playa del carmen", 
                       "merida", "oaxaca", "veracruz", "puebla", "toluca"]
    
    if any(c in ciudad for c in ciudades_mexico) or "méxico" in ciudad.lower():
        return "📍 Envío a tu ciudad: $120 en 3-5 días hábiles con Estafeta/DHL. ¿Dónde exactamente? 🚚"
    
    return "¿En qué estado o ciudad estás? Te paso el costo de envío exacto 📦"

# ===== HERRAMIENTA: Obtener Información de Política =====
@tool
def consultar_politica(tema: str) -> str:
    """
    Consulta las políticas: "devoluciones", "pagos", "envio", "garantia"
    """
    tema = tema.lower().strip()
    
    if "devolucion" in tema or "cambio" in tema:
        info = POLITICAS["devoluciones"]
        return (f"🔄 **DEVOLUCIONES Y CAMBIOS**:\n"
                f"- Plazo: {info['dias']} días\n"
                f"- {info['politica']}\n"
                f"- Condiciones: {info['condiciones']}")
    
    elif "pago" in tema:
        return (f"💳 **FORMAS DE PAGO**:\n"
                f"- {', '.join(POLITICAS['pagos'])}\n"
                f"Elige la que más te convenga 😊")
    
    elif "envio" in tema:
        return (f"📦 **ENVÍOS**:\n"
                f"- CDMX: Gratis en 1-2 días\n"
                f"- Resto de México: $120 en 3-5 días\n"
                f"¿A dónde te lo mando?")
    
    elif "garantia" in tema:
        return f"✅ {POLITICAS['garantia']}"
    
    else:
        return "¿Sobre qué política quieres saber? (devoluciones, pagos, envío, garantía)"

# ===== HERRAMIENTA: Responder FAQ =====
@tool
def responder_faq(tema: str) -> str:
    """
    Responde preguntas frecuentes automáticamente.
    Temas: "tallas", "envio", "devolucion", "pago", "descuento"
    """
    tema = tema.lower().strip()
    
    for palabra_clave, respuesta in PREGUNTAS_FRECUENTES.items():
        if palabra_clave in tema:
            return respuesta
    
    return "Esa pregunta no la tengo en mi base de datos, pero déjame consultarla 🤔"

# ===== HERRAMIENTA: Iniciar Pedido =====
@tool
def registrar_pedido(nombre: str, telefono: str, producto: str, talla: str, cantidad: int = 1) -> str:
    """
    Registra los datos iniciales de un pedido.
    Deberías guardar esto en una base de datos o Google Sheets.
    """
    return (f"✅ **PEDIDO REGISTRADO**\n"
            f"Cliente: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Producto: {producto}\n"
            f"Talla: {talla}\n"
            f"Cantidad: {cantidad}\n\n"
            f"Ahora te voy a mandar las opciones de pago 💳")

# ===== HERRAMIENTA: Generar Resumen de Carrito =====
@tool
def generar_carrito(producto: str, talla: str, cantidad: int = 1, ciudad: str = "") -> str:
    """
    Genera un resumen del carrito con precio total incluyendo envío.
    """
    producto = producto.lower().strip()
    
    # Buscar producto
    producto_encontrado = None
    for id_prod, datos in CATALOGO.items():
        if producto in datos["nombre"].lower() or producto in id_prod.lower():
            producto_encontrado = datos
            break
    
    if not producto_encontrado:
        return "No encontré ese producto 🤔"
    
    precio_unitario = producto_encontrado["precio"]
    subtotal = precio_unitario * cantidad
    
    # Calcular envío
    envio = 0
    if ciudad:
        if "cdmx" not in ciudad.lower():
            envio = 120
    
    total = subtotal + envio
    
    resumen = f"""
📦 **TU CARRITO**:
- {producto_encontrado['nombre']} (Talla {talla})
- Cantidad: {cantidad}
- Precio unitario: ${precio_unitario}
- Subtotal: ${subtotal}
- Envío: ${envio}
---
**TOTAL: ${total}**

¿Quieres proceder al pago? 💳
"""
    
    return resumen

# ===== HERRAMIENTA: Obtener Contacto =====
@tool
def obtener_contacto(canal: str = "general") -> str:
    """
    Obtiene información de contacto según el canal.
    """
    canal = canal.lower().strip()
    
    if "whatsapp" in canal:
        return f"💬 WhatsApp: {CONTACTO['whatsapp']}"
    elif "instagram" in canal or "ig" in canal:
        return f"📸 Instagram: {CONTACTO['instagram']}"
    elif "facebook" in canal or "fb" in canal:
        return f"👍 Facebook: {CONTACTO['facebook']}"
    elif "email" in canal:
        return f"📧 Email: {CONTACTO['email']}"
    else:
        return (f"📞 **CONTÁCTANOS**:\n"
                f"WhatsApp: {CONTACTO['whatsapp']}\n"
                f"Instagram: {CONTACTO['instagram']}\n"
                f"Facebook: {CONTACTO['facebook']}\n"
                f"Email: {CONTACTO['email']}\n"
                f"Horario: {CONTACTO['horario']}")
