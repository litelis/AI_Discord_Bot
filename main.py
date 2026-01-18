#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Lanzador Principal
Verifica dependencias y configuración antes de iniciar el bot
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    """Muestra el banner del bot"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║   🤖 Bot de Discord con Ollama - v2.0           ║
    ║   Bot inteligente con IA local                   ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica la versión de Python"""
    print("🔍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 o superior es requerido")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
    return True

def check_ollama():
    """Verifica si Ollama está instalado y corriendo"""
    print("\n🔍 Verificando Ollama...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Ollama está corriendo")
            return True
        else:
            print("⚠️  Ollama instalado pero no responde")
            return False
    except FileNotFoundError:
        print("❌ Ollama no está instalado")
        print("   Instala desde: https://ollama.ai")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama no responde (timeout)")
        return False
    except Exception as e:
        print(f"❌ Error verificando Ollama: {e}")
        return False

def check_ollama_model():
    """Verifica si el modelo llama3.2 está descargado"""
    print("\n🔍 Verificando modelo llama3.2...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "llama3.2" in result.stdout:
            print("✅ Modelo llama3.2 encontrado")
            return True
        else:
            print("⚠️  Modelo llama3.2 no encontrado")
            print("   Descargando modelo... (esto puede tardar varios minutos)")
            pull_result = subprocess.run(
                ["ollama", "pull", "llama3.2"],
                timeout=600
            )
            if pull_result.returncode == 0:
                print("✅ Modelo descargado correctamente")
                return True
            else:
                print("❌ Error descargando el modelo")
                return False
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")
        return False

def check_env_file():
    """Verifica si existe el archivo .env"""
    print("\n🔍 Verificando archivo de configuración...")
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  Archivo .env no encontrado")
        print("   Ejecuta: python src/config.py")
        return False
    
    # Verificar contenido básico
    with open(env_path, 'r') as f:
        content = f.read()
        if "DISCORD_TOKEN" not in content:
            print("⚠️  DISCORD_TOKEN no configurado en .env")
            return False
        if "AUTHORIZED_IDS" not in content:
            print("⚠️  AUTHORIZED_IDS no configurado en .env")
            return False
    
    print("✅ Archivo .env configurado")
    return True

def check_dependencies():
    """Verifica las dependencias necesarias"""
    print("\n🔍 Verificando dependencias...")
    required = ["discord", "dotenv", "requests", "flask", "flask_cors"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Faltan dependencias: {', '.join(missing)}")
        print("   Ejecuta: python src/setup.py")
        return False
    
    print("✅ Todas las dependencias instaladas")
    return True

def create_directories():
    """Crea los directorios necesarios"""
    print("\n🔍 Verificando estructura de directorios...")
    dirs = ["logs", "exports", "data", "web/templates", "web/static/css", "web/static/js"]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")
    return True

def start_bot():
    """Inicia el bot de Discord"""
    print("\n🚀 Iniciando bot de Discord...")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        # Importar y ejecutar el bot
        sys.path.insert(0, str(Path("src")))
        from bot import main
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error iniciando el bot: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    print_banner()
    
    # Verificaciones previas
    checks = [
        ("Versión de Python", check_python_version),
        ("Ollama", check_ollama),
        ("Modelo llama3.2", check_ollama_model),
        ("Configuración", check_env_file),
        ("Dependencias", check_dependencies),
        ("Directorios", create_directories)
    ]
    
    all_ok = True
    for name, check_func in checks:
        if not check_func():
            all_ok = False
            print(f"\n⚠️  {name}: FALLO")
    
    if not all_ok:
        print("\n❌ Hay problemas que deben resolverse antes de continuar")
        print("   Revisa los mensajes anteriores para más detalles")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ Todas las verificaciones pasaron correctamente")
    print("="*50)
    
    time.sleep(1)
    
    # Iniciar el bot
    start_bot()

if __name__ == "__main__":
    main()
