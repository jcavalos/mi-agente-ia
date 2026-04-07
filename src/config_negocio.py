"""
Configuración del negocio - Personaliza esto con tus datos reales
"""

NOMBRE_TIENDA = "Glamour Global"  # Cambia por el nombre de tu tienda
TIPO_ROPA = "Ropa casual y formal para mujeres"  # Ajusta según lo que vendes

# ===== CATÁLOGO DE PRODUCTOS =====
CATALOGO = {
    "blusa_blanca": {
        "nombre": "Blusa Blanca Clásica",
        "precio": 450,
        "tallas": ["XS", "S", "M", "L", "XL"],
        "colores": ["Blanco", "Negro", "Gris"],
        "material": "Algodón 100%",
        "stock": {"XS": 2, "S": 5, "M": 3, "L": 4, "XL": 2},
        "descripcion": "Blusa básica versátil, perfecta para trabajo o casual",
        "foto": "blusa_blanca.jpg"
    },
    "vestido_negro": {
        "nombre": "Vestido Negro Elegante",
        "precio": 850,
        "tallas": ["XS", "S", "M", "L", "XL", "XXL"],
        "colores": ["Negro", "Azul marino"],
        "material": "Poliéster con licra",
        "stock": {"XS": 1, "S": 3, "M": 5, "L": 4, "XL": 2, "XXL": 1},
        "descripcion": "Vestido elegante para eventos especiales",
        "foto": "vestido_negro.jpg"
    },
    "jeans_azul": {
        "nombre": "Jeans Azul Oscuro",
        "precio": 650,
        "tallas": ["25", "26", "27", "28", "29", "30", "31", "32"],
        "colores": ["Azul oscuro", "Azul claro"],
        "material": "Denim 98% algodón, 2% elastano",
        "stock": {"25": 2, "26": 4, "27": 6, "28": 5, "29": 3, "30": 2, "31": 1, "32": 1},
        "descripcion": "Jeans cómodo y duradero, ajuste perfecto",
        "foto": "jeans_azul.jpg"
    },
    "chamarra_cuero": {
        "nombre": "Chamarra de Cuero Sintético",
        "precio": 1200,
        "tallas": ["XS", "S", "M", "L", "XL"],
        "colores": ["Negro", "Marrón"],
        "material": "Cuero sintético de alta calidad",
        "stock": {"XS": 1, "S": 2, "M": 3, "L": 2, "XL": 1},
        "descripcion": "Chamarra de moda, perfecta para cualquier outfit",
        "foto": "chamarra_cuero.jpg"
    },
    "top_deportivo": {
        "nombre": "Top Deportivo con Soporte",
        "precio": 350,
        "tallas": ["XS", "S", "M", "L", "XL"],
        "colores": ["Negro", "Gris", "Rosa", "Azul"],
        "material": "Poliéster con licra",
        "stock": {"XS": 4, "S": 6, "M": 8, "L": 5, "XL": 3},
        "descripcion": "Top deportivo cómodo con máximo soporte",
        "foto": "top_deportivo.jpg"
    },
}

# ===== POLÍTICAS DEL NEGOCIO =====
POLITICAS = {
    "envio": {
        "cdmx": {
            "tiempo": "1-2 días hábiles",
            "costo": 0,  # Envío gratis CDMX
            "empresa": "Mensajería local"
        },
        "mexico": {
            "tiempo": "3-5 días hábiles",
            "costo": 120,
            "empresa": "Estafeta/DHL"
        },
        "otros": {
            "tiempo": "5-7 días hábiles",
            "costo": 150,
            "empresa": "DHL Internacional"
        }
    },
    "devoluciones": {
        "dias": 7,
        "politica": "El cliente paga el envío de regreso",
        "condiciones": "Debe estar sin usar, con etiqueta original"
    },
    "pagos": [
        "Transferencia bancaria",
        "Efectivo",
            ],
    "garantia": "Garantía de 30 días contra defectos de fabricación"
}

# ===== PREGUNTAS FRECUENTES =====
PREGUNTAS_FRECUENTES = {
    "tallas": "Usa nuestra guía de medidas. Mide tu pecho, cintura y caderas. ¿Cuáles son tus medidas? 📏",
    "envio": "A CDMX es gratis en 1-2 días. Al resto de México es $120 en 3-5 días. ¿A dónde lo mandamos?",
    "devolucion": "Puedes devolver en 7 días si está sin usar con etiqueta. Tú pagas el envío de regreso.",
    "pago": "Aceptamos transferencia, Mercado Pago, y PayPal. ¿Cuál prefieres?",
    "descuento": "Tenemos promociones especiales. ¿Sigues nuestras redes? Ahí posteamos descuentos.",
}

# ===== INFORMACIÓN DE CONTACTO =====
CONTACTO = {
    "whatsapp": "55 1234 5678",  # Cambia por tu WhatsApp
    "instagram": "@lunastyles",  # Cambia por tu IG
    "facebook": "Luna Styles",   # Cambiar por nuestro FB
    "email": "hola@lunastyles.com", # Crear un correo para la tienda
    "horario": "Lunes a Domingo 10:00 AM - 8:00 PM"
}

# ===== INSTRUCCIONES DEL AGENTE (Prompt Sistema) =====
INSTRUCCIONES_AGENTE = """
Eres "Eli", la asistente virtual de Glamour Global.
Tu estilo es amigable, cercano, rápido y siempre con ganas de vender.
Hablas como una chica mexicana de 25-28 años: usas emojis, lenguaje casual pero profesional.
Nunca suenas robótica. Siempre respondes en español mexicano.

REGLAS IMPORTANTES:
1. Siempre pregunta talla y ciudad para dar información precisa
2. Si el cliente duda, ofrece alternativas ("Tenemos el mismo en otro color")
3. Si es un pedido, pide: nombre completo, teléfono y dirección completa
4. Al final de cada conversación, pregunta: "¿Quieres que te mande el link de pago o prefieres transferir?"
5. Nunca des descuentos sin autorización del dueño
6. Si no sabes algo, di: "Déjame consultarlo con el equipo y te respondo en menos de 5 minutos ❤️"
7. Nunca inventes stock ni precios - usa la información del catálogo

INFORMACIÓN QUE CONOCES:
- Catálogo completo con precios, tallas, colores y stock actual
- Políticas de envío, devoluciones, pagos y garantía
- Horarios y canales de contacto

TU OBJETIVO: Responder rápido, resolver dudas y cerrar la venta.
"""

# ===== EJEMPLOS DE RESPUESTAS (agregar todo el catalogo de ropa) =====
EJEMPLOS_ENTRENAMIENTO = [
    {
        "pregunta": "¿Tienen la blusa blanca en talla M?",
        "respuesta": "¡Sí! La blusa blanca está disponible en M por $450. Quedan solo 3 piezas. ¿Te la mando con envío a CDMX o a otra ciudad? 😊"
    },
    {
        "pregunta": "¿Cuánto tarda el envío a Guadalajara?",
        "respuesta": "A Guadalajara tarda 3-4 días hábiles con Estafeta. El envío sale en $120. ¿Quieres que te arme el pedido con el código de seguimiento? 🚚"
    },
    {
        "pregunta": "¿Qué talla me queda?",
        "respuesta": "Para recomendarte talla necesito tus medidas. ¿Cuánto mides de pecho, cintura y caderas? Te ayudo a encontrar la perfecta 📏"
    },
    {
        "pregunta": "Quiero comprar el vestido negro",
        "respuesta": "¡Excelente elección! El vestido negro es hermoso. ¿Qué talla necesitas? Lo tengo en XS, S, M, L, XL y XXL. 💃"
    },
    {
        "pregunta": "¿Aceptan tarjeta?",
        "respuesta": "Sí, aceptamos tarjeta de débito/crédito, transferencia, Mercado Pago, Oxxo Pay y PayPal. ¿Cuál es tu forma favorita? 💳"
    }
]
