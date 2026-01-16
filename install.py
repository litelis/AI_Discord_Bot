import subprocess
import sys
import os

def print_header():
    """Muestra el encabezado del programa."""
    print()
    print("=" * 60)
    print("🔧 INSTALADOR COMPLETO DEL BOT DE DISCORD")
    print("=" * 60)
    print()
    print("Este script ejecutará los siguientes pasos:")
    print("1. 📦 Setup - Configurar entorno y dependencias")
    print("2. ⚙️  Config - Configurar variables de entorno")
    print("3. 🔄 Update - Verificar actualizaciones del repositorio")
    print()
    print("=" * 60)
    print()

def run_script(script_name, description):
    """Ejecuta un script de Python y retorna el resultado."""
    print(f"\n🚀 Ejecutando {description}...")
    print("-" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print("-" * 60)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError:
        print("-" * 60)
        print(f"⚠️ {description} terminó con errores")
        return False
    except FileNotFoundError:
        print("-" * 60)
        print(f"❌ Error: No se encontró {script_name}")
        return False
    except Exception as e:
        print("-" * 60)
        print(f"❌ Error inesperado: {e}")
        return False

def ask_continue(next_step):
    """Pregunta al usuario si desea continuar con el siguiente paso."""
    print()
    response = input(f"¿Deseas continuar con {next_step}? (s/n): ").strip().lower()
    return response in ['s', 'y', 'si', 'yes']

def main():
    print_header()
    
    # Lista de pasos a ejecutar
    steps = [
        {
            'script': 'src/setup.py',
            'description': 'Setup (Configuración del entorno)',
            'name': 'Config (Configuración de variables)'
        },
        {
            'script': 'src/config.py',
            'description': 'Config (Configuración de variables)',
            'name': 'Update (Actualización del repositorio)'
        },
        {
            'script': 'src/update.py',
            'description': 'Update (Actualización del repositorio)',
            'name': None  # Último paso
        }
    ]
    
    completed_steps = []
    skipped_steps = []
    
    # Ejecutar cada paso
    for i, step in enumerate(steps):
        step_number = i + 1
        total_steps = len(steps)
        
        print()
        print("=" * 60)
        print(f"PASO {step_number}/{total_steps}: {step['description'].upper()}")
        print("=" * 60)
        
        # Ejecutar el script
        success = run_script(step['script'], step['description'])
        
        if success:
            completed_steps.append(step['description'])
        
        # Si no es el último paso, preguntar si continuar
        if step['name'] is not None:
            print()
            if not ask_continue(step['name']):
                print(f"⏩ Saltando {step['name']}...")
                skipped_steps.append(step['name'])
                # Añadir los pasos restantes a skipped
                for j in range(i + 1, len(steps)):
                    if steps[j]['name']:
                        skipped_steps.append(steps[j]['name'])
                break
    
    # Resumen final
    print()
    print("=" * 60)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 60)
    print()
    
    if completed_steps:
        print("✅ Pasos completados:")
        for step in completed_steps:
            print(f"   • {step}")
    
    if skipped_steps:
        print()
        print("⏩ Pasos omitidos:")
        for step in skipped_steps:
            print(f"   • {step}")
    
    print()
    print("=" * 60)
    print("🎉 INSTALACIÓN FINALIZADA")
    print("=" * 60)
    print()
    print("📝 Próximos pasos:")
    print("• Ejecuta 'python main.py' para iniciar el bot")
    print("• O ejecuta 'python src/bot.py' directamente")
    print()
    print("💡 Consejos:")
    print("• Asegúrate de que Ollama esté ejecutándose")
    print("• Verifica tu archivo .env antes de iniciar el bot")
    print("• Usa 'python src/update.py' para actualizar más tarde")
    print()
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Instalación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
