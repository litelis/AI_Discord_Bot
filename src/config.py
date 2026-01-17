import os

def create_env_file():
    """Crea o actualiza el archivo .env con la configuración del usuario."""
    print("=" * 60)
    print("⚙️  CONFIGURACIÓN DEL BOT DE DISCORD")
    print("=" * 60)
    print()
    
    # Solicitar token del bot
    print("🔑 TOKEN DEL BOT DE DISCORD")
    print("Para obtenerlo:")
    print("1. Ve a https://discord.com/developers/applications")
    print("2. Selecciona tu aplicación > Bot > Reset Token")
    print()
    token = input("Ingresa el token de tu bot: ").strip()
    
    while not token:
        print("❌ El token no puede estar vacío.")
        token = input("Ingresa el token de tu bot: ").strip()
    
    print()
    
    # Solicitar IDs autorizados
    print("👥 IDS DE USUARIOS AUTORIZADOS")
    print("Para obtener tu ID de Discord:")
    print("1. Activa el Modo Desarrollador (Configuración > Avanzado > Modo Desarrollador)")
    print("2. Click derecho en tu perfil > Copiar ID")
    print()
    print("Puedes ingresar múltiples IDs separados por comas (sin espacios)")
    print("Ejemplo: 123456789012345678,987654321098765432")
    print()
    authorized_ids = input("Ingresa los IDs autorizados: ").strip()
    
    while not authorized_ids:
        print("❌ Debes ingresar al menos un ID autorizado.")
        authorized_ids = input("Ingresa los IDs autorizados: ").strip()
    
    # Limpiar IDs (eliminar espacios)
    authorized_ids = ','.join([id.strip() for id in authorized_ids.split(',')])
    
    print()
    
    # Preguntar por uso de GPU
    print("💻 CONFIGURACIÓN DE ACELERACIÓN")
    print("¿Deseas usar GPU para acelerar la IA?")
    print("Nota: Requiere GPU compatible y configuración de Ollama")
    print("Para más información, consulta GPU_SETUP.md")
    print()
    use_gpu = input("¿Usar GPU? (s/n): ").strip().lower()
    use_gpu_value = "true" if use_gpu in ['s', 'y', 'si', 'yes'] else "false"
    
    print()
    
    # Solicitar canal opcional
    print("📺 CANAL DE DISCORD (OPCIONAL)")
    print("Puedes configurar un canal específico donde el bot responderá.")
    print("Déjalo vacío si quieres que responda en todos los canales.")
    print("Puedes configurarlo después con /setchannel")
    print()
    channel_id = input("ID del canal (opcional): ").strip()
    
    print()
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración del Bot de Discord

# Token del bot de Discord (obtenerlo desde https://discord.com/developers/applications)
DISCORD_TOKEN={token}

# IDs de Discord autorizados (separados por comas, sin espacios)
# Para obtener tu ID: Activa el Modo Desarrollador en Discord > Click derecho en tu perfil > Copiar ID
AUTHORIZED_IDS={authorized_ids}

# Usar GPU para acelerar la IA (true/false)
# Requiere GPU compatible y configuración de Ollama
# Ver GPU_SETUP.md para más información
USE_GPU={use_gpu_value}
"""
    
    # Añadir canal si se proporcionó
    if channel_id:
        env_content += f"""
# ID del canal donde el bot responderá (opcional)
# Puedes cambiarlo con /setchannel
CHANNEL_ID={channel_id}
"""
    
    # Escribir el archivo .env
    try:
        with open('../.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("=" * 60)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print(f"📝 Archivo .env creado exitosamente")
        print(f"🔑 Token configurado")
        print(f"👥 IDs autorizados: {authorized_ids}")
        print(f"💻 GPU habilitada: {'Sí' if use_gpu_value == 'true' else 'No'}")
        if channel_id:
            print(f"📺 Canal configurado: {channel_id}")
        print()
        print("🚀 Próximos pasos:")
        print("1. Ejecuta 'python setup.py' para configurar el entorno")
        print("2. Asegúrate de que Ollama esté ejecutándose")
        if use_gpu_value == 'true':
            print("3. Verifica la configuración de GPU en GPU_SETUP.md")
            print("4. Ejecuta 'python bot.py' para iniciar el bot")
        else:
            print("3. Ejecuta 'python bot.py' para iniciar el bot")
        print()
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"❌ Error al crear el archivo .env: {str(e)}")
        return False

def verify_env_file():
    """Verifica si el archivo .env existe y tiene la configuración necesaria."""
    if not os.path.exists('../.env'):
        return False
    
    try:
        with open('../.env', 'r', encoding='utf-8') as f:
            content = f.read()
            has_token = 'DISCORD_TOKEN=' in content and 'tu_token_aqui' not in content
            has_ids = 'AUTHORIZED_IDS=' in content and '123456789012345678' not in content
            return has_token and has_ids
    except:
        return False

def main():
    print()
    
    if verify_env_file():
        print("✅ El archivo .env ya existe y está configurado.")
        print()
        response = input("¿Deseas reconfigurarlo? (s/n): ").strip().lower()
        
        if response != 's':
            print("⏩ Manteniendo configuración actual.")
            return
        print()
    
    create_env_file()

if __name__ == "__main__":
    main()
