import subprocess
import sys
import os

def run_command(cmd, shell=True):
    """Ejecuta un comando y retorna el resultado."""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_git_installed():
    """Verifica si Git está instalado."""
    success, output = run_command("git --version")
    if success:
        return True
    else:
        print("❌ Git no está instalado o no está en el PATH.")
        print("Por favor, instala Git desde: https://git-scm.com/downloads")
        return False

def check_git_repo():
    """Verifica si estamos en un repositorio Git."""
    if not os.path.exists('.git'):
        print("❌ Este directorio no es un repositorio Git.")
        print("Por favor, ejecuta este script desde el directorio del proyecto.")
        return False
    return True

def get_current_branch():
    """Obtiene la rama actual."""
    success, output = run_command("git branch --show-current")
    if success:
        return output.strip()
    return "main"

def fetch_updates():
    """Descarga las actualizaciones del repositorio remoto."""
    print("🔍 Verificando actualizaciones disponibles...")
    success, output = run_command("git fetch origin")
    if not success:
        print(f"❌ Error al verificar actualizaciones: {output}")
        return False
    return True

def check_for_updates():
    """Verifica si hay actualizaciones disponibles."""
    branch = get_current_branch()
    
    # Obtener el commit local
    success_local, local_commit = run_command(f"git rev-parse {branch}")
    if not success_local:
        print(f"❌ Error al obtener commit local: {local_commit}")
        return None, None
    
    # Obtener el commit remoto
    success_remote, remote_commit = run_command(f"git rev-parse origin/{branch}")
    if not success_remote:
        print(f"❌ Error al obtener commit remoto: {remote_commit}")
        return None, None
    
    local_commit = local_commit.strip()
    remote_commit = remote_commit.strip()
    
    return local_commit, remote_commit

def show_update_info():
    """Muestra información sobre las actualizaciones disponibles."""
    print("\n📋 Cambios disponibles:")
    print("-" * 60)
    success, output = run_command("git log HEAD..origin/main --oneline --decorate")
    if success and output.strip():
        print(output)
    else:
        print("No hay información detallada de cambios disponible.")
    print("-" * 60)

def apply_updates():
    """Aplica las actualizaciones desde el repositorio remoto."""
    print("\n📥 Descargando actualizaciones...")
    
    # Verificar si hay cambios locales no guardados
    success, output = run_command("git status --porcelain")
    if success and output.strip():
        print("\n⚠️  ADVERTENCIA: Hay cambios locales no guardados:")
        print(output)
        print("\nEstos cambios podrían perderse al actualizar.")
        response = input("¿Deseas guardar estos cambios antes de actualizar? (s/n): ").strip().lower()
        
        if response == 's':
            print("💾 Guardando cambios locales...")
            run_command("git stash")
            print("✅ Cambios guardados temporalmente.")
    
    # Hacer pull de los cambios
    branch = get_current_branch()
    success, output = run_command(f"git pull origin {branch}")
    
    if success:
        print("\n✅ Actualización completada exitosamente!")
        print("\n📝 Recuerda:")
        print("- Si hay nuevas dependencias, ejecuta: python setup.py")
        print("- Verifica tu archivo .env si hay nuevas variables")
        return True
    else:
        print(f"\n❌ Error al aplicar actualizaciones: {output}")
        print("\n💡 Posibles soluciones:")
        print("1. Resuelve conflictos manualmente")
        print("2. Ejecuta: git reset --hard origin/main (⚠️ esto descartará cambios locales)")
        return False

def main():
    print("=" * 60)
    print("🔄 ACTUALIZADOR DEL BOT DE DISCORD")
    print("=" * 60)
    print()
    
    # Verificar Git
    if not check_git_installed():
        sys.exit(1)
    
    # Verificar repositorio
    if not check_git_repo():
        sys.exit(1)
    
    # Obtener rama actual
    branch = get_current_branch()
    print(f"📍 Rama actual: {branch}")
    print()
    
    # Descargar actualizaciones
    if not fetch_updates():
        sys.exit(1)
    
    # Verificar actualizaciones
    local_commit, remote_commit = check_for_updates()
    
    if local_commit is None or remote_commit is None:
        print("❌ No se pudo verificar el estado de actualizaciones.")
        sys.exit(1)
    
    if local_commit == remote_commit:
        print("✅ Tu repositorio está actualizado!")
        print(f"📌 Commit actual: {local_commit[:7]}")
        print()
        print("No hay actualizaciones disponibles.")
    else:
        print("🆕 ¡Hay actualizaciones disponibles!")
        print(f"📌 Versión local:  {local_commit[:7]}")
        print(f"📌 Versión remota: {remote_commit[:7]}")
        
        # Mostrar información de cambios
        show_update_info()
        
        print()
        response = input("¿Deseas actualizar a la última versión? (s/n): ").strip().lower()
        
        if response == 's' or response == 'y':
            if apply_updates():
                print("\n" + "=" * 60)
                print("✅ ACTUALIZACIÓN COMPLETADA")
                print("=" * 60)
            else:
                sys.exit(1)
        else:
            print("\n⏩ Actualización cancelada.")
            print("Puedes ejecutar este script nuevamente cuando quieras actualizar.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
