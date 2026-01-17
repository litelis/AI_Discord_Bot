import os
import sys
import subprocess
import platform

def run_command(cmd, shell=True):
    """Ejecuta un comando y retorna el resultado."""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def create_virtualenv():
    """Crea el entorno virtual."""
    print("📦 Creando entorno virtual...")
    if os.path.exists(".venv"):
        print("✅ El entorno virtual ya existe.")
    else:
        success, output = run_command(f"{sys.executable} -m venv .venv")
        if success:
            print("✅ Entorno virtual creado.")
        else:
            print(f"❌ Error al crear entorno virtual: {output}")
            sys.exit(1)

def get_pip_path():
    """Obtiene la ruta del pip del entorno virtual."""
    if platform.system() == "Windows":
        return os.path.join(".venv", "Scripts", "pip.exe")
    else:
        return os.path.join(".venv", "bin", "pip")

def install_dependencies():
    """Instala las dependencias en el entorno virtual."""
    print("📥 Instalando dependencias...")
    pip_path = get_pip_path()
    
    dependencies = ["discord.py", "python-dotenv", "requests", "flask", "flask-cors"]
    
    for dep in dependencies:
        print(f"  Instalando {dep}...")
        success, output = run_command(f"{pip_path} install {dep}")
        if success:
            print(f"  ✅ {dep} instalado.")
        else:
            print(f"  ❌ Error instalando {dep}: {output}")

def check_ollama():
    """Verifica si Ollama está instalado."""
    print("🤖 Verificando Ollama...")
    success, output = run_command("ollama --version")
    if success:
        print(f"✅ Ollama encontrado: {output.strip()}")
        return True
    else:
        print("❌ Ollama no está instalado.")
        print("Por favor, instala Ollama desde: https://ollama.ai")
        return False

def pull_model():
    """Descarga el modelo de Ollama."""
    print("📥 Descargando modelo llama3.2.2...")
    print("Esto puede tomar varios minutos dependiendo de tu conexión...")
    success, output = run_command("ollama pull llama3.2.2")
    if success:
        print("✅ Modelo llama3.2.2 descargado correctamente.")
        return True
    else:
        print(f"⚠️ No se pudo descargar llama3.2.2: {output}")
        print("Intentando con modelo alternativo llama3.2...")
        success_alt, output_alt = run_command("ollama pull llama3.2")
        if success_alt:
            print("✅ Modelo llama3.2 descargado correctamente como alternativa.")
            print("⚠️ IMPORTANTE: Actualiza bot.py para usar 'llama3.2' en lugar de 'llama3.2.2'")
            return True
        else:
            print(f"❌ Error al descargar modelo alternativo: {output_alt}")
            return False

def main():
    print("=" * 60)
    print("🚀 CONFIGURACIÓN DEL BOT DE DISCORD CON OLLAMA")
    print("=" * 60)
    
    # Crear entorno virtual
    create_virtualenv()
    
    # Instalar dependencias
    install_dependencies()
    
    # Verificar Ollama
    if check_ollama():
        pull_model()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("\n📝 Próximos pasos:")
    print("1. Ejecuta 'python config.py' para configurar TOKEN y IDs autorizados")
    print("2. Asegúrate de que Ollama esté ejecutándose (ollama serve)")
    print("3. Ejecuta el bot con: python bot.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()


