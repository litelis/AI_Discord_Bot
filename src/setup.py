#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Instalador de Dependencias
Instala todas las dependencias necesarias del bot
"""

import subprocess
import sys
from pathlib import Path


def print_banner():
    """Muestra el banner del instalador"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║   📦 Instalador de Dependencias                 ║
    ║   Bot de Discord con Ollama                      ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)


def check_pip():
    """Verifica que pip esté instalado"""
    print("🔍 Verificando pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ pip instalado: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip no está instalado")
        print("   Instala pip desde: https://pip.pypa.io/en/stable/installation/")
        return False


def upgrade_pip():
    """Actualiza pip a la última versión"""
    print("\n🔄 Actualizando pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print("✅ pip actualizado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  No se pudo actualizar pip: {e}")
        return False


def install_package(package: str, display_name: str = None) -> bool:
    """
    Instala un paquete de Python
    
    Args:
        package: Nombre del paquete con versión (ej: "discord.py>=2.6.4")
        display_name: Nombre a mostrar (opcional)
        
    Returns:
        True si se instaló correctamente
    """
    if display_name is None:
        display_name = package.split('>=')[0].split('==')[0]
    
    print(f"\n📦 Instalando {display_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"✅ {display_name} instalado correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {display_name}")
        print(f"   Detalles: {e.stderr}")
        return False


def verify_installation(package: str) -> bool:
    """
    Verifica que un paquete esté instalado
    
    Args:
        package: Nombre del paquete a verificar
        
    Returns:
        True si está instalado
    """
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def install_all_dependencies() -> bool:
    """
    Instala todas las dependencias necesarias
    
    Returns:
        True si todas se instalaron correctamente
    """
    print("\n" + "="*60)
    print("📦 INSTALANDO DEPENDENCIAS")
    print("="*60)
    
    dependencies = [
        ("discord.py>=2.6.4", "discord.py (Discord API)"),
        ("python-dotenv>=1.2.1", "python-dotenv (Variables de entorno)"),
        ("requests>=2.32.5", "requests (HTTP client)"),
        ("flask>=3.1.2", "Flask (Web server)"),
        ("flask-cors>=6.0.2", "Flask-CORS (CORS support)")
    ]
    
    failed = []
    
    for package, display_name in dependencies:
        if not install_package(package, display_name):
            failed.append(display_name)
    
    if failed:
        print("\n" + "="*60)
        print("❌ INSTALACIÓN INCOMPLETA")
        print("="*60)
        print(f"\nNo se pudieron instalar: {', '.join(failed)}")
        print("\nIntenta instalar manualmente:")
        print(f"   pip install {' '.join([d[0] for d in dependencies])}")
        return False
    else:
        print("\n" + "="*60)
        print("✅ TODAS LAS DEPENDENCIAS INSTALADAS")
        print("="*60)
        return True


def verify_all_imports() -> bool:
    """
    Verifica que todos los módulos se puedan importar
    
    Returns:
        True si todos se importan correctamente
    """
    print("\n" + "="*60)
    print("🔍 VERIFICANDO IMPORTACIONES")
    print("="*60)
    
    modules = [
        ("discord", "discord.py"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS")
    ]
    
    failed = []
    
    for module, display_name in modules:
        print(f"\n🔍 Verificando {display_name}...")
        if verify_installation(module):
            print(f"✅ {display_name} OK")
        else:
            print(f"❌ {display_name} NO disponible")
            failed.append(display_name)
    
    if failed:
        print("\n❌ Algunos módulos no están disponibles:")
        print(f"   {', '.join(failed)}")
        return False
    else:
        print("\n✅ Todos los módulos disponibles")
        return True


def create_requirements_file():
    """Crea el archivo requirements.txt"""
    print("\n📝 Creando requirements.txt...")
    
    requirements = """# Dependencias del Bot de Discord con Ollama
# Instalar con: pip install -r requirements.txt

discord.py>=2.6.4
python-dotenv>=1.2.1
requests>=2.32.5
flask>=3.1.2
flask-cors>=6.0.2
"""
    
    req_file = Path("requirements.txt")
    
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print(f"✅ requirements.txt creado en: {req_file.absolute()}")


def show_summary():
    """Muestra un resumen final"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE LA INSTALACIÓN")
    print("="*60)
    print("""
✅ Dependencias de Python instaladas:
   • discord.py - Integración con Discord
   • python-dotenv - Variables de entorno
   • requests - Cliente HTTP para Ollama
   • Flask - Servidor web para dashboard
   • Flask-CORS - Soporte CORS

📋 Próximos pasos:

1. Asegúrate de tener Ollama instalado:
   https://ollama.ai

2. Descarga el modelo llama3.2:
   ollama pull llama3.2

3. Configura el bot:
   python src/config.py

4. Inicia el bot:
   python main.py

💡 Tips:
   • Usa requirements.txt para reinstalar: pip install -r requirements.txt
   • Actualiza dependencias: pip install --upgrade -r requirements.txt
   • Crea entorno virtual: python -m venv venv
""")


def main():
    """Función principal del instalador"""
    print_banner()
    
    print("Este script instalará todas las dependencias necesarias para el bot.")
    print("\nDependencias a instalar:")
    print("  • discord.py (API de Discord)")
    print("  • python-dotenv (Variables de entorno)")
    print("  • requests (Cliente HTTP)")
    print("  • Flask (Servidor web)")
    print("  • Flask-CORS (Soporte CORS)")
    
    input("\n▶️  Presiona ENTER para continuar...")
    
    try:
        # Verificar pip
        if not check_pip():
            print("\n❌ pip es necesario para continuar")
            sys.exit(1)
        
        # Actualizar pip
        upgrade_pip()
        
        # Instalar dependencias
        if not install_all_dependencies():
            print("\n⚠️  La instalación tuvo problemas")
            choice = input("\n¿Continuar con la verificación? (s/n): ").lower().strip()
            if choice != 's':
                sys.exit(1)
        
        # Verificar importaciones
        if not verify_all_imports():
            print("\n❌ Algunas dependencias no están disponibles")
            print("   Intenta reinstalar o revisa los errores anteriores")
            sys.exit(1)
        
        # Crear requirements.txt
        create_requirements_file()
        
        # Mostrar resumen
        show_summary()
        
        print("\n🎉 ¡Instalación completada exitosamente!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Instalación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()