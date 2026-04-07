"""
integraciones.py - Conexiones a WhatsApp, Instagram, Facebook y otras redes
Incluye ejemplos para cada plataforma
"""

from agent_tienda import crear_agente_tienda, responder_mensaje
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv()

class IntegracionRedes:
    """
    Clase para integrar el agente con diferentes redes sociales
    """
    
    def __init__(self):
        self.agente = crear_agente_tienda()
        self.historial_conversaciones = []
    
    # ===== WHATSAPP =====
    def procesar_mensaje_whatsapp(self, numero_cliente: str, mensaje: str, nombre_cliente: str = "Cliente"):
        """
        Procesa un mensaje de WhatsApp Business API
        Integración típica: Twilio, Wati, ManyChat
        """
        print(f"\n📱 [WhatsApp] {nombre_cliente} ({numero_cliente}): {mensaje}")
        
        respuesta = responder_mensaje(self.agente, mensaje)
        
        # Guardar en historial
        self._guardar_conversacion(
            canal="WhatsApp",
            numero_cliente=numero_cliente,
            nombre_cliente=nombre_cliente,
            mensaje_cliente=mensaje,
            respuesta_agente=respuesta
        )
        
        return respuesta
    
    # ===== INSTAGRAM =====
    def procesar_mensaje_instagram(self, usuario_ig: str, mensaje: str):
        """
        Procesa un DM de Instagram
        Integración típica: ManyChat, Chatfuel
        """
        print(f"\n📸 [Instagram] @{usuario_ig}: {mensaje}")
        
        respuesta = responder_mensaje(self.agente, mensaje)
        
        self._guardar_conversacion(
            canal="Instagram",
            usuario_ig=usuario_ig,
            mensaje_cliente=mensaje,
            respuesta_agente=respuesta
        )
        
        return respuesta
    
    # ===== FACEBOOK =====
    def procesar_mensaje_facebook(self, id_usuario_fb: str, mensaje: str, nombre: str = "Usuario"):
        """
        Procesa un mensaje del Messenger de Facebook
        Integración típica: ManyChat, Chatfuel
        """
        print(f"\n👍 [Facebook] {nombre}: {mensaje}")
        
        respuesta = responder_mensaje(self.agente, mensaje)
        
        self._guardar_conversacion(
            canal="Facebook Messenger",
            id_usuario=id_usuario_fb,
            nombre_cliente=nombre,
            mensaje_cliente=mensaje,
            respuesta_agente=respuesta
        )
        
        return respuesta
    
    # ===== TIKTOK =====
    def procesar_mensaje_tiktok(self, usuario_tiktok: str, mensaje: str):
        """
        Procesa un DM de TikTok (generalmente mediante integraciones)
        """
        print(f"\n🎵 [TikTok] @{usuario_tiktok}: {mensaje}")
        
        respuesta = responder_mensaje(self.agente, mensaje)
        
        self._guardar_conversacion(
            canal="TikTok",
            usuario_tiktok=usuario_tiktok,
            mensaje_cliente=mensaje,
            respuesta_agente=respuesta
        )
        
        return respuesta
    
    # ===== WEB CHAT (tu sitio web) =====
    def procesar_mensaje_web(self, nombre_cliente: str, email: str, mensaje: str):
        """
        Procesa un mensaje del chat en tu sitio web
        """
        print(f"\n🌐 [Web Chat] {nombre_cliente} ({email}): {mensaje}")
        
        respuesta = responder_mensaje(self.agente, mensaje)
        
        self._guardar_conversacion(
            canal="Web Chat",
            nombre_cliente=nombre_cliente,
            email=email,
            mensaje_cliente=mensaje,
            respuesta_agente=respuesta
        )
        
        return respuesta
    
    # ===== Guardar historial =====
    def _guardar_conversacion(self, canal: str, mensaje_cliente: str, respuesta_agente: str, **kwargs):
        """
        Guarda cada conversación en un historial
        Esto puede conectarse a Google Sheets, base de datos, etc.
        """
        conversacion = {
            "timestamp": datetime.now().isoformat(),
            "canal": canal,
            "cliente": kwargs.get("nombre_cliente", kwargs.get("usuario_ig", kwargs.get("usuario_tiktok", "Desconocido"))),
            "mensaje_cliente": mensaje_cliente,
            "respuesta_agente": respuesta_agente,
            "metadata": {k: v for k, v in kwargs.items() if k not in ["nombre_cliente"]}
        }
        
        self.historial_conversaciones.append(conversacion)
        
        # Opcional: Guardar en archivo JSON
        self._exportar_historial()
    
    def _exportar_historial(self, archivo="historial_conversaciones.json"):
        """
        Exporta el historial a un archivo JSON
        """
        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(self.historial_conversaciones, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ No se pudo guardar el historial: {e}")
    
    def obtener_estadisticas(self):
        """
        Retorna estadísticas básicas de conversaciones
        """
        total = len(self.historial_conversaciones)
        canales = {}
        
        for conv in self.historial_conversaciones:
            canal = conv["canal"]
            canales[canal] = canales.get(canal, 0) + 1
        
        return {
            "total_conversaciones": total,
            "por_canal": canales,
            "timestamp": datetime.now().isoformat()
        }


# ===== EJEMPLOS DE USO =====
if __name__ == "__main__":
    print("🚀 Inicializando integraciones...\n")
    
    integ = IntegracionRedes()
    
    # Ejemplo 1: WhatsApp
    print("\n" + "="*60)
    print("EJEMPLO 1: WhatsApp")
    print("="*60)
    respuesta_wp = integ.procesar_mensaje_whatsapp(
        numero_cliente="+525512345678",
        nombre_cliente="María",
        mensaje="¿Tienen la blusa blanca en talla M?"
    )
    print(f"🤖 Respuesta: {respuesta_wp}")
    
    # Ejemplo 2: Instagram
    print("\n" + "="*60)
    print("EJEMPLO 2: Instagram DM")
    print("="*60)
    respuesta_ig = integ.procesar_mensaje_instagram(
        usuario_ig="maria.fashion",
        mensaje="¿Cuánto cuesta el vestido negro y cuál es el envío a Guadalajara?"
    )
    print(f"🤖 Respuesta: {respuesta_ig}")
    
    # Ejemplo 3: Facebook
    print("\n" + "="*60)
    print("EJEMPLO 3: Facebook Messenger")
    print("="*60)
    respuesta_fb = integ.procesar_mensaje_facebook(
        id_usuario_fb="123456789",
        nombre="Juan",
        mensaje="Quiero comprar el top deportivo en negro, talla M"
    )
    print(f"🤖 Respuesta: {respuesta_fb}")
    
    # Ejemplo 4: Web Chat
    print("\n" + "="*60)
    print("EJEMPLO 4: Web Chat")
    print("="*60)
    respuesta_web = integ.procesar_mensaje_web(
        nombre_cliente="Carlos",
        email="carlos@email.com",
        mensaje="¿Cuáles son sus políticas de devolución?"
    )
    print(f"🤖 Respuesta: {respuesta_web}")
    
    # Mostrar estadísticas
    print("\n" + "="*60)
    print("ESTADÍSTICAS")
    print("="*60)
    stats = integ.obtener_estadisticas()
    print(f"Total de conversaciones: {stats['total_conversaciones']}")
    print(f"Por canal: {stats['por_canal']}")
