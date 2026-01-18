#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Configurador Interactivo
Configuración guiada del archivo .env
"""

from pathlib import Path


def print_banner():
    """Muestra el banner del configurador"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║   ⚙️  Configurador del Bot de Discord           ║
    ║   Configuración paso a paso                      ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)


def get_discord_token() -> str:
    """
    Solicita el token de Discord al usuario
    
    Returns:
        Token de Discord
    """
    print("\n" + "="*60)
    print("🔑 TOKEN DE DISCORD")
    print("="*60)
    print("""
Para obtener tu token de Discord:

1. Ve a https://discord.com/developers/applications
2. Crea una nueva aplicación (o selecciona una existente)
3. Ve a la sección "Bot" en el menú lateral
4. Si no has creado un bot, haz clic en "Add Bot"
5. En la sección "TOKEN", haz clic en "Reset Token" o "Copy"
6. Copia el token (solo se muestra una vez)

IMPORTANTE: 
- Nunca compartas tu token con nadie
- No lo subas a GitHub u otros servicios públicos
- Trata el token como una contraseña

Permisos necesarios para el bot:
- Send Messages
- Read Messages/View Channels
- Use Slash Commands
- Attach Files
""")
    
    while True:
        token = input("Ingresa tu token de Discord: ").strip()
        
        if not token:
            print("❌ El token no puede estar vacío")
            continue
        
        if len(token) < 50:
            print("⚠️  El token parece muy corto. ¿Estás seguro que es correcto?")
            confirm = input("¿Continuar de todos modos? (s/n): ").lower().strip()
            if confirm != 's':
                continue
        
        return token


def get_authorized_ids() -> str:
    """
    Solicita los IDs de usuarios autorizados
    
    Returns:
        String con IDs separados por comas
    """
    print("\n" + "="*60)
    print("👥 USUARIOS AUTORIZADOS")
    print("="*60)
    print("""
Puedes configurar qué usuarios pueden usar el bot.

Para obtener tu ID de Discord:
1. Abre Discord
2. Ve a Configuración > Avanzado
3. Activa "Modo Desarrollador"
4. Haz clic derecho en tu nombre de usuario
5. Selecciona "Copiar ID"

Puedes agregar múltiples IDs separados por comas.
Ejemplo: 123456789,987654321,555666777

Si dejas esto vacío, TODOS los usuarios podrán usar el bot.
""")
    
    ids = input("IDs autorizados (o ENTER para todos): ").strip()
    
    if ids:
        # Validar formato básico
        id_list = [id.strip() for id in ids.split(',')]
        valid_ids = []
        
        for id_str in id_list:
            if id_str.isdigit():
                valid_ids.append(id_str)
            else:
                print(f"⚠️  '{id_str}' no es un ID válido, se ignorará")
        
        if valid_ids:
            result = ','.join(valid_ids)
            print(f"✅ {len(valid_ids)} IDs configurados")
            return result
        else:
            print("⚠️  No se configuraron IDs válidos. El bot será accesible para todos.")
            return ""
    else:
        print("ℹ️  Sin restricciones de usuario. El bot será accesible para todos.")
        return ""


def get_gpu_setting() -> str:
    """
    Pregunta si usar GPU
    
    Returns:
        'true' o 'false'
    """
    print("\n" + "="*60)
    print("🎮 CONFIGURACIÓN DE GPU")
    print("="*60)
    print("""
¿Tu sistema tiene una GPU compatible con CUDA?

Si tienes una GPU NVIDIA y has instalado los drivers CUDA,
puedes habilitar la aceleración por GPU para Ollama.

Esto mejorará significativamente la velocidad de respuesta.

Si no estás seguro o no tienes GPU, selecciona 'No'.
""")
    
    while True:
        choice = input("¿Usar GPU? (s/n): ").lower().strip()
        
        if choice == 's':
            print("✅ GPU habilitada")
            return "true"
        elif choice == 'n':
            print("ℹ️  GPU deshabilitada, se usará CPU")
            return "false"
        else:
            print("❌ Por favor ingresa 's' o 'n'")


def create_env_file(token: str, ids: str, use_gpu: str):
    """
    Crea el archivo .env con la configuración
    
    Args:
        token: Token de Discord
        ids: IDs autorizados
        use_gpu: Si usar GPU
    """
    env_content = f"""# Configuración del Bot de Discord con Ollama
# Generado automáticamente el {Path(__file__).stat().st_mtime}

# Token de Discord (REQUERIDO)
# Obtén tu token en: https://discord.com/developers/applications
DISCORD_TOKEN={token}

# IDs de usuarios autorizados (opcional)
# Separa múltiples IDs con comas
# Si está vacío, todos los usuarios pueden usar el bot
AUTHORIZED_IDS={ids}

# Usar GPU para Ollama (opcional)
# Mejora el rendimiento si tienes GPU compatible
USE_GPU={use_gpu}

# IMPORTANTE:
# - NO compartas este archivo con nadie
# - NO lo subas a GitHub o servicios públicos
# - Este archivo está en .gitignore por seguridad
"""
    
    env_path = Path(".env")
    
    # Backup si ya existe
    if env_path.exists():
        backup_path = Path(".env.backup")
        env_path.rename(backup_path)
        print(f"ℹ️  .env anterior guardado como .env.backup")
    
    # Crear nuevo archivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Archivo .env creado correctamente")


def verify_configuration():
    """Verifica que la configuración es correcta"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Error: Archivo .env no fue creado")
        return False
    
    print("\n" + "="*60)
    print("🔍 VERIFICANDO CONFIGURACIÓN")
    print("="*60)
    
    # Leer archivo
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar variables
    checks = [
        ("DISCORD_TOKEN", "Token de Discord"),
        ("AUTHORIZED_IDS", "IDs autorizados"),
        ("USE_GPU", "Configuración de GPU")
    ]
    
    all_ok = True
    for var, desc in checks:
        if var in content:
            print(f"✅ {desc} configurado")
        else:
            print(f"❌ {desc} falta")
            all_ok = False
    
    return all_ok


def show_next_steps():
    """Muestra los próximos pasos"""
    print("\n" + "="*60)
    print("📋 PRÓXIMOS PASOS")
    print("="*60)
    print("""
1. Asegúrate de que Ollama esté corriendo:
   • Windows: Ollama debería estar corriendo automáticamente
   • Linux/Mac: ollama serve

2. Verifica que el modelo llama3.2 esté descargado:
   ollama list
   
   Si no está, descárgalo:
   ollama pull llama3.2

3. Invita al bot a tu servidor de Discord:
   • Ve a https://discord.com/developers/applications
   • Selecciona tu aplicación
   • Ve a OAuth2 > URL Generator
   • Selecciona: bot, applications.commands
   • Permisos: Send Messages, Use Slash Commands, Attach Files
   • Copia el URL generado y ábrelo en tu navegador
   • Selecciona tu servidor

4. Inicia el bot:
   python main.py

5. En Discord, usa /help para ver todos los comandos

¡Listo! Tu bot debería estar funcionando. 🎉
""")


def main():
    """Función principal del configurador"""
    print_banner()
    
    print("Este configurador te ayudará a establecer la configuración básica del bot.")
    print("Necesitarás:\n")
    print("  • Token de tu bot de Discord")
    print("  • (Opcional) IDs de usuarios autorizados")
    print("  • (Opcional) Configuración de GPU")
    
    input("\n▶️  Presiona ENTER para continuar...")
    
    try:
        # Obtener configuración
        token = get_discord_token()
        ids = get_authorized_ids()
        use_gpu = get_gpu_setting()
        
        # Crear archivo .env
        print("\n" + "="*60)
        print("💾 CREANDO ARCHIVO DE CONFIGURACIÓN")
        print("="*60)
        
        create_env_file(token, ids, use_gpu)
        
        # Verificar
        if verify_configuration():
            print("\n✅ Configuración completada exitosamente")
            show_next_steps()
        else:
            print("\n⚠️  Hubo problemas con la configuración")
            print("   Revisa el archivo .env manualmente")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuración cancelada por el usuario")
        return
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        return


if __name__ == "__main__":
    main()