#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Instalador Guiado
Instalador completo e interactivo del bot
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Muestra el banner del instalador"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║   🤖 Instalador Bot de Discord con Ollama       ║
    ║   Instalación guiada paso a paso                 ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)

def print_step(step, total, description):
    """Imprime el paso actual"""
    print(f"\n{'='*60}")
    print(f"📍 Paso {step}/{total}: {description}")
    print('='*60)

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n▶️  {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        print(f"   Detalles: {e.stderr}")
        return False

def create_directory_structure():
    """Crea la estructura de directorios"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        "src",
        "web/templates",
        "web/static/css",
        "web/static/js",
        "logs",
        "exports",
        "data"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Estructura de directorios creada")
    return True

def install_dependencies():
    """Instala las dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    dependencies = [
        "discord.py>=2.6.4",
        "python-dotenv>=1.2.1",
        "requests>=2.32.5",
        "flask>=3.1.2",
        "flask-cors>=6.0.2"
    ]
    
    for dep in dependencies:
        if not run_command(
            f'pip install "{dep}"',
            f"Instalando {dep.split('>=')[0]}"
        ):
            return False
    
    return True

def create_requirements_txt():
    """Crea el archivo requirements.txt"""
    print("\n📝 Creando requirements.txt...")
    
    requirements = """discord.py>=2.6.4
python-dotenv>=1.2.1
requests>=2.32.5
flask>=3.1.2
flask-cors>=6.0.2
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    print("✅ requirements.txt creado")
    return True

def create_gitignore():
    """Crea el archivo .gitignore"""
    print("\n📝 Creando .gitignore...")
    
    gitignore = """# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
logs/
*.log

# Data
data/*.json
exports/
*.dob

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore)
    
    print("✅ .gitignore creado")
    return True

def create_license():
    """Crea el archivo LICENSE con licencia MIT"""
    print("\n📝 Creando LICENSE (MIT)...")
    
    license_text = """MIT License

Copyright (c) 2026 Bot de Discord con Ollama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open("LICENSE", "w", encoding="utf-8") as f:
        f.write(license_text)
    
    print("✅ LICENSE creado")
    return True

def check_ollama():
    """Verifica si Ollama está instalado"""
    print("\n🔍 Verificando Ollama...")
    
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Ollama está instalado")
            return True
        else:
            print("⚠️  Ollama no responde correctamente")
            return False
    except FileNotFoundError:
        print("❌ Ollama NO está instalado")
        print("\n📌 Debes instalar Ollama desde: https://ollama.ai")
        print("   1. Descarga el instalador para tu sistema operativo")
        print("   2. Instala Ollama")
        print("   3. Ejecuta este instalador nuevamente")
        return False
    except Exception as e:
        print(f"❌ Error verificando Ollama: {e}")
        return False

def pull_ollama_model():
    """Descarga el modelo llama3.2 de Ollama"""
    print("\n🤖 Descargando modelo llama3.2...")
    print("   ⚠️  Esto puede tardar varios minutos dependiendo de tu conexión")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", "llama3.2"],
            timeout=600
        )
        
        if result.returncode == 0:
            print("✅ Modelo llama3.2 descargado")
            return True
        else:
            print("❌ Error descargando el modelo")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout descargando el modelo (la descarga continúa en segundo plano)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configure_bot():
    """Ejecuta el configurador del bot"""
    print("\n⚙️  Configuración del bot...")
    print("   A continuación se te pedirá la configuración del bot")
    
    try:
        subprocess.run([sys.executable, "src/config.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Error en la configuración")
        return False

def main():
    """Función principal del instalador"""
    print_banner()
    
    print("\n🎯 Este instalador configurará todo lo necesario para el bot")
    print("   El proceso incluye:")
    print("   • Verificación de requisitos")
    print("   • Instalación de dependencias")
    print("   • Creación de estructura de archivos")
    print("   • Descarga del modelo de IA")
    print("   • Configuración del bot")
    
    input("\n▶️  Presiona ENTER para continuar...")
    
    steps = [
        (1, 7, "Crear estructura de directorios", create_directory_structure),
        (2, 7, "Crear requirements.txt", create_requirements_txt),
        (3, 7, "Crear .gitignore", create_gitignore),
        (4, 7, "Crear LICENSE", create_license),
        (5, 7, "Instalar dependencias Python", install_dependencies),
        (6, 7, "Verificar Ollama", check_ollama),
        (7, 7, "Descargar modelo llama3.2", pull_ollama_model),
    ]
    
    for step, total, description, func in steps:
        print_step(step, total, description)
        
        if not func():
            print(f"\n❌ Error en el paso {step}: {description}")
            print("   La instalación no puede continuar")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Instalación base completada con éxito")
    print("="*60)
    
    print("\n📋 Próximos pasos:")
    print("   1. Configurar el bot: python src/config.py")
    print("   2. Crear archivos del bot en src/")
    print("   3. Iniciar el bot: python main.py")
    
    configure = input("\n¿Deseas configurar el bot ahora? (s/n): ").lower().strip()
    
    if configure == 's':
        if configure_bot():
            print("\n✅ ¡Todo listo! Ahora puedes iniciar el bot con:")
            print("   python main.py")
        else:
            print("\n⚠️  Puedes configurar el bot más tarde con:")
            print("   python src/config.py")
    else:
        print("\n📝 Recuerda configurar el bot antes de iniciarlo:")
        print("   python src/config.py")
    
    print("\n🎉 ¡Instalación completada!")

if __name__ == "__main__":
    main()
