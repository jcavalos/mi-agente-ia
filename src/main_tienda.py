"""
main_tienda.py - Interfaz de prueba del agente vendedor
Ejecuta esto para probar localmente antes de conectar a WhatsApp
"""

from agente_tienda import crear_agente_tienda, responder_mensaje
from config_negocio import NOMBRE_TIENDA, TIPO_ROPA, CATALOGO
import sys

def mostrar_menu():
    """Muestra un menú de opciones para probar el agente"""
    print("\n" + "="*60)
    print(f"  🛍️  AGENTE {NOMBRE_TIENDA.upper()}")
    print(f"  {TIPO_ROPA}")
    print("="*60)
    print("\nEscribe tu pregunta o elige una opción:")
    print("  [1] Ver catálogo")
    print("  [2] Información de envío")
    print("  [3] Preguntar sobre devoluciones")
    print("  [4] Escribir pregunta personalizada")
    print("  [salir] Terminar")
    print("-"*60)

def mostrar_catalogo():
    """Muestra todos los productos disponibles"""
    print("\n📦 CATÁLOGO COMPLETO:\n")
    for id_prod, datos in CATALOGO.items():
        print(f"✦ {datos['nombre']}")
        print(f"  Precio: ${datos['precio']}")
        print(f"  Tallas: {', '.join(datos['tallas'])}")
        print(f"  Colores: {', '.join(datos['colores'])}")
        print(f"  {datos['descripcion']}\n")

def main():
    """Función principal"""
    print("\n🚀 Inicializando agente...")
    
    try:
        agente = crear_agente_tienda()
        print("✅ Agente listo!\n")
    except Exception as e:
        print(f"❌ Error al inicializar el agente: {e}")
        sys.exit(1)

    print("="*60)
    print(f"  ¡Bienvenido a {NOMBRE_TIENDA}!")
    print(f"  Tipo de ropa: {TIPO_ROPA}")
    print("="*60)
    print("Escribe 'salir' para terminar\n")

    while True:
        mostrar_menu()
        opcion = input("\nTu opción: ").strip().lower()

        if opcion in ["salir", "exit", "quit"]:
            print("\n👋 Hasta luego! Gracias por usar el agente.")
            break

        elif opcion == "1":
            mostrar_catalogo()

        elif opcion == "2":
            print("\n📦 INFORMACIÓN DE ENVÍO:")
            pregunta = "¿Cuál es el costo de envío a CDMX y a otros estados?"
            print(f"\n👤 Cliente: {pregunta}")
            respuesta = responder_mensaje(agente, pregunta)
            print(f"🤖 Luna: {respuesta}\n")

        elif opcion == "3":
            print("\n🔄 INFORMACIÓN DE DEVOLUCIONES:")
            pregunta = "¿Puedo devolver una prenda si no me queda?"
            print(f"\n👤 Cliente: {pregunta}")
            respuesta = responder_mensaje(agente, pregunta)
            print(f"🤖 Luna: {respuesta}\n")

        elif opcion == "4":
            pregunta = input("\n📝 Tu pregunta: ").strip()
            if not pregunta:
                print("❌ Debes escribir una pregunta")
                continue
            
            print(f"\n👤 Cliente: {pregunta}")
            respuesta = responder_mensaje(agente, pregunta)
            print(f"🤖 Luna: {respuesta}\n")

        else:
            print("❌ Opción no válida. Intenta de nuevo.\n")


if __name__ == "__main__":
    main()
