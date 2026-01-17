import subprocess
import sys
import os
import time
import platform
from pathlib import Path

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header():
    """Muestra el encabezado del programa."""
    clear_screen()
    print("=" * 60)
    print("🤖 BOT DE DISCORD CON OLLAMA - INICIADOR PRINCIPAL")
    print("=" * 60)
    print()

def check_ollama_installed():
    """Verifica si Ollama está instalado."""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_ollama_running():
    """Verifica si Ollama está ejecutándose."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Inicia el servidor de Ollama."""
    print("🚀 Iniciando servidor Ollama...")
    
    if platform.system() == "Windows":
        # En Windows, Ollama se ejecuta como servicio, solo verificamos que esté disponible
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        # En Linux/Mac
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    
    # Esperar a que Ollama esté listo
    print("⏳ Esperando a que Ollama esté listo...")
    for i in range(30):  # Intentar durante 30 segundos
        if check_ollama_running():
            print("✅ Ollama iniciado correctamente")
            return True
        time.sleep(1)
    
    print("❌ No se pudo iniciar Ollama")
    return False

def check_model_exists(model_name="llama3.2"):
    """Verifica si el modelo está descargado."""
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return model_name in result.stdout
    except:
        return False

def download_model(model_name="llama3.2"):
    """Descarga el modelo de Ollama."""
    print(f"\n📥 Descargando modelo {model_name}...")
    print("Esto puede tomar varios minutos dependiendo de tu conexión...")
    
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"✅ Modelo {model_name} descargado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"⚠️ No se pudo descargar {model_name}, intentando con llama3...")
        try:
            subprocess.run(["ollama", "pull", "llama3"], check=True)
            print("✅ Modelo llama3 descargado como alternativa")
            print("⚠️ NOTA: Actualiza MODEL_NAME en src/bot.py a 'llama3'")
            return True
        except:
            print("❌ Error al descargar modelos")
            return False

def check_env_configured():
    """Verifica si el archivo .env está configurado."""
    if not os.path.exists('.env'):
        return False
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            has_token = 'DISCORD_TOKEN=' in content and 'tu_token_aqui' not in content
            has_ids = 'AUTHORIZED_IDS=' in content and '123456789012345678' not in content
            return has_token and has_ids
    except:
        return False

def run_config():
    """Ejecuta el configurador."""
    print("\n⚙️ Ejecutando configurador...")
    subprocess.run([sys.executable, "src/config.py"])

def check_dependencies():
    """Verifica si las dependencias están instaladas."""
    try:
        import discord
        import dotenv
        import requests
        return True
    except ImportError:
        return False

def install_dependencies():
    """Instala las dependencias."""
    print("\n📦 Instalando dependencias...")
    subprocess.run([sys.executable, "src/setup.py"])

def start_bot():
    """Inicia el bot de Discord."""
    print("\n🤖 Iniciando bot de Discord...")
    print("-" * 60)
    print("Presiona Ctrl+C para detener el bot")
    print("-" * 60)
    print()
    
    try:
        subprocess.run([sys.executable, "src/bot.py"])
    except KeyboardInterrupt:
        print("\n\n⏹️ Bot detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el bot: {e}")

def main():
    print_header()
    
    # 1. Verificar Ollama
    print("1️⃣ Verificando Ollama...")
    if not check_ollama_installed():
        print("❌ Ollama no está instalado")
        print("Por favor, instala Ollama desde: https://ollama.ai")
        print("\nPresiona Enter para salir...")
        input()
        sys.exit(1)
    print("✅ Ollama instalado")
    
    # 2. Iniciar Ollama si no está corriendo
    print("\n2️⃣ Verificando servidor Ollama...")
    if not check_ollama_running():
        if not start_ollama():
            print("\n❌ No se pudo iniciar Ollama")
            print("Intenta iniciarlo manualmente con: ollama serve")
            print("\nPresiona Enter para salir...")
            input()
            sys.exit(1)
    else:
        print("✅ Ollama ya está ejecutándose")
    
    # 3. Verificar modelo
    print("\n3️⃣ Verificando modelo de IA...")
    model_name = "llama3.2"
    if not check_model_exists(model_name):
        print(f"⚠️ Modelo {model_name} no encontrado")
        response = input("¿Deseas descargarlo ahora? (s/n): ").strip().lower()
        if response in ['s', 'y']:
            if not download_model(model_name):
                print("\n❌ No se pudo descargar el modelo")
                print("\nPresiona Enter para salir...")
                input()
                sys.exit(1)
        else:
            print("⏩ Continuando sin descargar modelo...")
    else:
        print(f"✅ Modelo {model_name} disponible")
    
    # 4. Verificar configuración
    print("\n4️⃣ Verificando configuración...")
    if not check_env_configured():
        print("⚠️ Archivo .env no configurado")
        response = input("¿Deseas configurarlo ahora? (s/n): ").strip().lower()
        if response in ['s', 'y']:
            run_config()
            if not check_env_configured():
                print("\n❌ Configuración cancelada o incompleta")
                print("\nPresiona Enter para salir...")
                input()
                sys.exit(1)
        else:
            print("❌ No se puede continuar sin configuración")
            print("\nPresiona Enter para salir...")
            input()
            sys.exit(1)
    print("✅ Configuración encontrada")
    
    # 5. Verificar dependencias
    print("\n5️⃣ Verificando dependencias de Python...")
    if not check_dependencies():
        print("⚠️ Dependencias no instaladas")
        response = input("¿Deseas instalarlas ahora? (s/n): ").strip().lower()
        if response in ['s', 'y']:
            install_dependencies()
            if not check_dependencies():
                print("\n❌ Error al instalar dependencias")
                print("\nPresiona Enter para salir...")
                input()
                sys.exit(1)
        else:
            print("❌ No se puede continuar sin dependencias")
            print("\nPresiona Enter para salir...")
            input()
            sys.exit(1)
    print("✅ Dependencias instaladas")
    
    # 6. Iniciar bot
    print("\n" + "=" * 60)
    print("✅ TODO LISTO - INICIANDO BOT")
    print("=" * 60)
    time.sleep(2)
    
    start_bot()
    
    print("\n" + "=" * 60)
    print("👋 ¡Hasta pronto!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("\nPresiona Enter para salir...")
        input()
        sys.exit(1)
