#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Actualizador Git
Actualiza el repositorio con los últimos cambios
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def print_banner():
    """Muestra el banner del actualizador"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║   🔄 Actualizador del Repositorio              ║
    ║   Bot de Discord con Ollama                      ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)


def run_command(cmd, description, capture=True):
    """
    Ejecuta un comando y muestra el resultado
    
    Args:
        cmd: Comando a ejecutar (string o lista)
        description: Descripción de la operación
        capture: Si capturar la salida
        
    Returns:
        True si exitoso, False si falló
    """
    print(f"\n▶️  {description}...")
    
    try:
        if capture:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd.split(),
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            result = subprocess.run(
                cmd if isinstance(cmd, list) else cmd.split(),
                check=True
            )
        
        print(f"✅ {description} completado")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        if capture and e.stderr:
            print(f"   Detalles: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"❌ Comando no encontrado para {description}")
        return False


def check_git_installed():
    """Verifica si Git está instalado"""
    print("\n🔍 Verificando Git...")
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Git instalado: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git no está instalado")
        print("   Descarga Git desde: https://git-scm.com/downloads")
        return False


def check_git_repo():
    """Verifica si estamos en un repositorio Git"""
    print("\n🔍 Verificando repositorio Git...")
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True
        )
        print("✅ Repositorio Git encontrado")
        return True
    except subprocess.CalledProcessError:
        print("❌ No es un repositorio Git")
        print("   Inicializa con: git init")
        return False


def check_uncommitted_changes():
    """Verifica si hay cambios sin commitear"""
    print("\n🔍 Verificando cambios sin guardar...")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("⚠️  Hay cambios sin guardar:")
            print(result.stdout)
            return True
        else:
            print("✅ No hay cambios sin guardar")
            return False
            
    except subprocess.CalledProcessError:
        return False


def git_add_all():
    """Añade todos los archivos al stage"""
    return run_command("git add .", "Añadiendo archivos al stage")


def git_commit(message=None):
    """
    Crea un commit con los cambios
    
    Args:
        message: Mensaje del commit
        
    Returns:
        True si exitoso
    """
    if message is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Update: {timestamp}"
    
    return run_command(
        ["git", "commit", "-m", message],
        "Creando commit"
    )


def git_push(remote="origin", branch="main"):
    """
    Push al repositorio remoto
    
    Args:
        remote: Nombre del remoto
        branch: Nombre de la rama
        
    Returns:
        True si exitoso
    """
    return run_command(
        f"git push {remote} {branch}",
        f"Subiendo cambios a {remote}/{branch}"
    )


def git_pull(remote="origin", branch="main"):
    """
    Pull del repositorio remoto
    
    Args:
        remote: Nombre del remoto
        branch: Nombre de la rama
        
    Returns:
        True si exitoso
    """
    return run_command(
        f"git pull {remote} {branch}",
        f"Descargando cambios de {remote}/{branch}"
    )


def show_git_status():
    """Muestra el estado actual del repositorio"""
    print("\n📊 Estado del repositorio:")
    print("="*60)
    run_command("git status", "Estado de Git", capture=False)


def show_recent_commits(count=5):
    """Muestra los últimos commits"""
    print(f"\n📝 Últimos {count} commits:")
    print("="*60)
    run_command(
        f"git log --oneline -n {count}",
        "Historial de commits",
        capture=False
    )


def get_remote_url():
    """Obtiene la URL del remoto"""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def main():
    """Función principal del actualizador"""
    print_banner()
    
    print("Este script ayuda a actualizar el repositorio de GitHub.")
    print("\nOperaciones disponibles:")
    print("  1. Subir cambios (add + commit + push)")
    print("  2. Descargar cambios (pull)")
    print("  3. Ver estado del repositorio")
    print("  4. Ver commits recientes")
    print("  5. Salir")
    
    # Verificaciones previas
    if not check_git_installed():
        print("\n❌ Git es necesario para continuar")
        sys.exit(1)
    
    if not check_git_repo():
        print("\n❌ No estamos en un repositorio Git")
        choice = input("\n¿Deseas inicializar un repositorio aquí? (s/n): ").lower().strip()
        if choice == 's':
            if run_command("git init", "Inicializando repositorio"):
                print("\n✅ Repositorio inicializado")
                print("   Configura el remoto con: git remote add origin <URL>")
        sys.exit(0)
    
    # Mostrar remoto
    remote_url = get_remote_url()
    if remote_url:
        print(f"\n📍 Remoto configurado: {remote_url}")
    else:
        print("\n⚠️  No hay remoto configurado")
        print("   Configura con: git remote add origin <URL>")
    
    while True:
        try:
            print("\n" + "="*60)
            choice = input("\nSelecciona una opción (1-5): ").strip()
            
            if choice == '1':
                # Subir cambios
                print("\n" + "="*60)
                print("📤 SUBIR CAMBIOS")
                print("="*60)
                
                if not check_uncommitted_changes():
                    print("\n✅ No hay cambios para subir")
                    continue
                
                commit_msg = input("\nMensaje del commit (ENTER para auto): ").strip()
                if not commit_msg:
                    commit_msg = None
                
                if git_add_all():
                    if git_commit(commit_msg):
                        confirm = input("\n¿Subir al remoto? (s/n): ").lower().strip()
                        if confirm == 's':
                            git_push()
                        else:
                            print("ℹ️  Cambios guardados localmente")
                
            elif choice == '2':
                # Descargar cambios
                print("\n" + "="*60)
                print("📥 DESCARGAR CAMBIOS")
                print("="*60)
                
                if check_uncommitted_changes():
                    print("\n⚠️  Tienes cambios sin guardar")
                    confirm = input("¿Continuar de todos modos? (s/n): ").lower().strip()
                    if confirm != 's':
                        continue
                
                git_pull()
                
            elif choice == '3':
                # Ver estado
                show_git_status()
                
            elif choice == '4':
                # Ver commits
                show_recent_commits()
                
            elif choice == '5':
                # Salir
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Operación cancelada")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()