import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
from dotenv import load_dotenv
import requests
import json
import pickle
from pathlib import Path
<<<<<<< HEAD
import time
import threading

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import BotLogger
from src.stats import StatsManager
from src.personality import PersonalityManager
from src.chat_export import ChatExporter
from src.web_server import WebServer
=======
import asyncio
from datetime import datetime
import threading

# Importar sistemas nuevos
from logger import BotLogger
from personality import PersonalityManager
from chat_export import ChatExporter
from stats import StatsManager
from web_server import start_web_server
>>>>>>> a3a6423eddddd559e2fc6f80f70026559a4e234a

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_IDS = os.getenv('AUTHORIZED_IDS', '').split(',')
CHANNEL_ID = os.getenv('CHANNEL_ID', None)
USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

# Inicializar sistemas
logger = BotLogger()
stats_manager = StatsManager()
personality_manager = PersonalityManager()
chat_exporter = ChatExporter()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Crear bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Inicializar sistemas
logger = BotLogger()
personality_mgr = PersonalityManager()
exporter = ChatExporter()
stats_mgr = StatsManager()

# Variable global para el servidor web
web_server_running = False
web_server_thread = None

# Diccionarios para almacenar datos
chat_histories = {}
saved_chats = {}
channel_config = {}

# Crear carpeta para guardar datos
SAVE_DIR = Path("data")
SAVE_DIR.mkdir(exist_ok=True)

def load_saved_data():
    """Carga chats guardados y configuración de canales."""
    global saved_chats, channel_config
    
    chats_file = SAVE_DIR / "saved_chats.pkl"
    if chats_file.exists():
        try:
            with open(chats_file, 'rb') as f:
                saved_chats = pickle.load(f)
        except:
            saved_chats = {}
    
    channels_file = SAVE_DIR / "channel_config.pkl"
    if channels_file.exists():
        try:
            with open(channels_file, 'rb') as f:
                channel_config = pickle.load(f)
        except:
            channel_config = {}

def save_channel_config():
    """Guarda la configuración de canales."""
    with open(SAVE_DIR / "channel_config.pkl", 'wb') as f:
        pickle.dump(channel_config, f)

<<<<<<< HEAD
def get_ollama_response(user_id, message):
    """Obtiene respuesta del modelo Ollama manteniendo el contexto."""
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # Obtener personalidad del usuario
    personality = personality_manager.get_personality(user_id)
    system_prompt = personality["system_prompt"]

    # Añadir mensaje del usuario al historial
    chat_histories[user_id].append({"role": "user", "content": message})

    # Construir el prompt con personalidad y contexto
    context_parts = [f"Sistema: {system_prompt}"]
    context_parts.extend([
        f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}"
        for msg in chat_histories[user_id]
    ])
    context = "\n".join(context_parts)

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": context,
            "stream": False
        }

        # Añadir configuración de GPU si está habilitada
        if USE_GPU:
            payload["options"] = {"num_gpu": 1}

        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        ai_response = result.get('response', 'No pude generar una respuesta.')

        # Añadir respuesta del asistente al historial
        chat_histories[user_id].append({"role": "assistant", "content": ai_response})

        return ai_response

    except requests.exceptions.ConnectionError:
        return "❌ Error: No se puede conectar a Ollama. Asegúrate de que Ollama esté ejecutándose."
    except requests.exceptions.Timeout:
        return "❌ Error: La solicitud tomó demasiado tiempo. Intenta con un mensaje más corto."
=======
def save_chats():
    """Guarda todos los chats guardados."""
    with open(SAVE_DIR / "saved_chats.pkl", 'wb') as f:
        pickle.dump(saved_chats, f)

def get_context(user_id):
    """Obtiene el historial de chat del usuario."""
    personality = personality_mgr.get_personality(user_id)
    system_prompt = personality["system_prompt"]
    
    history = chat_histories.get(str(user_id), [])
    context = f"{system_prompt}\n\n"
    
    for msg in history[-10:]:  # Últimos 10 mensajes
        context += f"{msg['role']}: {msg['content']}\n"
    
    return context

async def query_ollama(prompt, user_id):
    """Consulta a Ollama con el prompt y contexto del usuario."""
    start_time = datetime.now()
    context = get_context(user_id)
    full_prompt = context + f"User: {prompt}\nAssistant:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        ai_response = result.get('response', 'Error: No response from model.')
        
        # Actualizar historial
        if str(user_id) not in chat_histories:
            chat_histories[str(user_id)] = []
        
        chat_histories[str(user_id)].append({"role": "User", "content": prompt})
        chat_histories[str(user_id)].append({"role": "Assistant", "content": ai_response})
        
        # Registrar estadísticas
        elapsed = (datetime.now() - start_time).total_seconds()
        tokens = len(full_prompt.split()) + len(ai_response.split())
        stats_mgr.record_interaction(user_id, tokens, elapsed)
        
        logger.log_message(user_id, prompt, ai_response, elapsed)
        
        return ai_response
>>>>>>> a3a6423eddddd559e2fc6f80f70026559a4e234a
    except Exception as e:
        logger.log_error(f"Error querying Ollama: {str(e)}")
        return f"❌ Error al consultar Ollama: {str(e)}"

def start_web_server():
    """Inicia el servidor web si no está corriendo."""
    global web_server_running, web_server_thread

    if not web_server_running:
        try:
            web_server_thread = start_web_server(stats_mgr, host='127.0.0.1', port=5000)
            web_server_running = True
            logger.log_info("Web server started on http://127.0.0.1:5000")
            return True
        except Exception as e:
            logger.log_error(f"Failed to start web server: {str(e)}")
            return False
    return True

@bot.event
async def on_ready():
    """Evento cuando el bot está listo."""
    load_saved_data()
    await bot.tree.sync()
    logger.log_info(f'✅ Bot conectado como {bot.user}')
    print(f'✅ Bot conectado como {bot.user}')
<<<<<<< HEAD
    print(f'📋 IDs autorizados: {AUTHORIZED_IDS}')
    print(f'🤖 Modelo Ollama: {MODEL_NAME}')
    print(f'💻 Usando GPU: {"Sí" if USE_GPU else "No"}')

    # Iniciar servidor web en un hilo separado
    web_server = WebServer(stats_manager, personality_manager, saved_chats, chat_histories)
    web_thread = threading.Thread(target=web_server.run, daemon=True)
    web_thread.start()
    print(f'🌐 Servidor web iniciado en http://localhost:5000')

    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos slash sincronizados')
    except Exception as e:
        print(f'❌ Error al sincronizar comandos: {e}')

@bot.tree.command(name="newchat", description="Limpia el historial de chat actual")
async def newchat(interaction: discord.Interaction):
    """Limpia el historial de chat del usuario."""
    user_id = str(interaction.user.id)
    
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return
    
    if user_id in chat_histories:
        chat_histories[user_id] = []
        await interaction.response.send_message("🔄 Historial de chat limpiado. ¡Empecemos de nuevo!")
    else:
        await interaction.response.send_message("📝 No hay historial previo. ¡Comienza a chatear!")

@bot.tree.command(name="savechat", description="Guarda el chat actual con un nombre")
@app_commands.describe(nombre="Nombre para identificar este chat")
async def savechat(interaction: discord.Interaction, nombre: str):
    """Guarda el chat actual."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    if user_id not in chat_histories or not chat_histories[user_id]:
        await interaction.response.send_message("❌ No hay ningún chat activo para guardar.", ephemeral=True)
        return

    # Inicializar diccionario de usuario si no existe
    if user_id not in saved_chats:
        saved_chats[user_id] = {}

    # Guardar el chat
    saved_chats[user_id][nombre] = chat_histories[user_id].copy()
    save_chats_data()

    # Registrar estadística
    stats_manager.record_chat_saved()
    logger.log_command(user_id, "savechat", {"nombre": nombre})

    await interaction.response.send_message(f"💾 Chat guardado como '{nombre}'")

@bot.tree.command(name="loadchat", description="Carga un chat guardado previamente")
@app_commands.describe(nombre="Nombre del chat a cargar")
async def loadchat(interaction: discord.Interaction, nombre: str):
    """Carga un chat guardado."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    if user_id not in saved_chats or nombre not in saved_chats[user_id]:
        await interaction.response.send_message(f"❌ No existe un chat guardado con el nombre '{nombre}'.", ephemeral=True)
        return

    # Cargar el chat
    chat_histories[user_id] = saved_chats[user_id][nombre].copy()

    # Registrar estadística
    stats_manager.record_chat_loaded()
    logger.log_command(user_id, "loadchat", {"nombre": nombre})

    await interaction.response.send_message(f"📂 Chat '{nombre}' cargado correctamente. ¡Continuemos!")

@bot.tree.command(name="listchats", description="Lista todos los chats guardados")
async def listchats(interaction: discord.Interaction):
    """Lista los chats guardados del usuario."""
    user_id = str(interaction.user.id)
    
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return
    
    if user_id not in saved_chats or not saved_chats[user_id]:
        await interaction.response.send_message("📭 No tienes chats guardados.", ephemeral=True)
        return
    
    # Crear lista de chats
    chat_list = []
    for chat_name, history in saved_chats[user_id].items():
        msg_count = len(history)
        chat_list.append(f"• **{chat_name}** ({msg_count} mensajes)")
    
    message = "💬 **Tus chats guardados:**\n" + "\n".join(chat_list)
    await interaction.response.send_message(message)

@bot.tree.command(name="deletechat", description="Elimina un chat guardado")
@app_commands.describe(nombre="Nombre del chat a eliminar")
async def deletechat(interaction: discord.Interaction, nombre: str):
    """Elimina un chat guardado."""
    user_id = str(interaction.user.id)
    
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return
    
    if user_id not in saved_chats or nombre not in saved_chats[user_id]:
        await interaction.response.send_message(f"❌ No existe un chat guardado con el nombre '{nombre}'.", ephemeral=True)
        return
    
    # Eliminar el chat
    del saved_chats[user_id][nombre]
    save_chats_data()
    
    await interaction.response.send_message(f"🗑️ Chat '{nombre}' eliminado correctamente.")

@bot.tree.command(name="setchannel", description="Configura el canal donde el bot responderá (solo admin)")
@app_commands.describe(canal="Canal donde el bot debe responder")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, canal: discord.TextChannel):
    """Configura el canal del bot."""
    user_id = str(interaction.user.id)
    
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    channel_config[guild_id] = str(canal.id)
    save_channel_config()
    
    await interaction.response.send_message(f"✅ Canal configurado: {canal.mention}")

@bot.tree.command(name="unsetchannel", description="Permite al bot responder en cualquier canal (solo admin)")
@app_commands.checks.has_permissions(administrator=True)
async def unsetchannel(interaction: discord.Interaction):
    """Quita la restricción de canal."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)
    if guild_id in channel_config:
        del channel_config[guild_id]
        save_channel_config()

    await interaction.response.send_message("✅ El bot ahora responderá en cualquier canal.")
=======
    print(f'🤖 Modelo: {MODEL_NAME}')
    print(f'🔗 Ollama URL: {OLLAMA_URL}')
    print(f'👥 IDs autorizados: {len(AUTHORIZED_IDS)}')
    print(f'📋 Usa /help para ver los comandos slash disponibles')
>>>>>>> a3a6423eddddd559e2fc6f80f70026559a4e234a

@bot.tree.command(name="setpersonality", description="Cambia la personalidad del bot")
@app_commands.describe(persona="Personalidad a usar")
@app_commands.choices(persona=[
    app_commands.Choice(name="Profesional", value="profesional"),
    app_commands.Choice(name="Amigo Cercano", value="amigo"),
    app_commands.Choice(name="Mentor Sabio", value="mentor"),
    app_commands.Choice(name="Entusiasta", value="entusiasta")
])
async def setpersonality(interaction: discord.Interaction, persona: str):
    """Cambia la personalidad del bot."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    if personality_manager.set_personality(user_id, persona):
        personality = personality_manager.get_personality(user_id)
        logger.log_command(user_id, "setpersonality", {"persona": persona})
        await interaction.response.send_message(f"✅ Personalidad cambiada a: **{personality['nombre']}**\n{personality['descripcion']}")
    else:
        await interaction.response.send_message("❌ Personalidad no válida.", ephemeral=True)

@bot.tree.command(name="exportchat", description="Exporta un chat guardado")
@app_commands.describe(nombre="Nombre del chat a exportar", formato="Formato de exportación")
@app_commands.choices(formato=[
    app_commands.Choice(name="TXT", value="txt"),
    app_commands.Choice(name="DOB (Propietario)", value="dob")
])
async def exportchat(interaction: discord.Interaction, nombre: str, formato: str):
    """Exporta un chat guardado."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    if user_id not in saved_chats or nombre not in saved_chats[user_id]:
        await interaction.response.send_message(f"❌ No existe un chat guardado con el nombre '{nombre}'.", ephemeral=True)
        return

    chat_history = saved_chats[user_id][nombre]

    try:
        if formato == "txt":
            filepath = chat_exporter.export_to_txt(chat_history, nombre, user_id)
        else:  # dob
            filepath = chat_exporter.export_to_dob(chat_history, nombre, user_id)

        logger.log_command(user_id, "exportchat", {"nombre": nombre, "formato": formato})
        await interaction.response.send_message(f"✅ Chat '{nombre}' exportado como {formato.upper()}.\nArchivo guardado en: `{filepath}`")
    except Exception as e:
        logger.log_error("ExportError", str(e), user_id)
        await interaction.response.send_message(f"❌ Error al exportar: {str(e)}", ephemeral=True)

@bot.tree.command(name="importchat", description="Importa un chat desde archivo")
@app_commands.describe(archivo="Archivo a importar")
async def importchat(interaction: discord.Interaction, archivo: discord.Attachment):
    """Importa un chat desde archivo."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    # Descargar archivo
    try:
        file_content = await archivo.read()
        temp_path = Path("temp_import")
        with open(temp_path, 'wb') as f:
            f.write(file_content)

        # Intentar importar
        if archivo.filename.endswith('.dob'):
            chat_data, error = chat_exporter.import_from_dob(temp_path)
        elif archivo.filename.endswith('.txt'):
            chat_data, error = chat_exporter.import_from_txt(temp_path)
        else:
            await interaction.response.send_message("❌ Formato no soportado. Usa .dob o .txt", ephemeral=True)
            temp_path.unlink()
            return

        if error:
            await interaction.response.send_message(f"❌ Error al importar: {error}", ephemeral=True)
            temp_path.unlink()
            return

        # Guardar chat importado
        if user_id not in saved_chats:
            saved_chats[user_id] = {}

        saved_chats[user_id][chat_data['chat_name']] = chat_data['messages']
        save_chats_data()

        logger.log_command(user_id, "importchat", {"filename": archivo.filename, "chat_name": chat_data['chat_name']})
        await interaction.response.send_message(f"✅ Chat '{chat_data['chat_name']}' importado correctamente ({chat_data['message_count']} mensajes)")

        temp_path.unlink()

    except Exception as e:
        logger.log_error("ImportError", str(e), user_id)
        await interaction.response.send_message(f"❌ Error al procesar archivo: {str(e)}", ephemeral=True)

@bot.tree.command(name="webui", description="Muestra el enlace al panel web")
async def webui(interaction: discord.Interaction):
    """Muestra el enlace al panel web."""
    user_id = str(interaction.user.id)

    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permiso para usar este comando.", ephemeral=True)
        return

    await interaction.response.send_message("🌐 **Panel Web del Bot**\n\nAccede a: http://localhost:5000\n\nDesde ahí podrás:\n• Ver estadísticas detalladas\n• Gestionar chats guardados\n• Cambiar personalidades\n• Exportar/importar chats")

@bot.event
async def on_message(message):
    """Procesa mensajes en canales configurados."""
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    
    # Verificar si está autorizado
    if user_id not in AUTHORIZED_IDS:
        return
    
    # Verificar si el canal está configurado para este servidor
    guild_id = str(message.guild.id) if message.guild else None
    if guild_id and channel_config.get(guild_id) == message.channel.id:
        async with message.channel.typing():
            response = await query_ollama(message.content, message.author.id)
            
            # Dividir respuesta si es muy larga
            if len(response) > 2000:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
    
    # Si no hay canal configurado pero el mensaje es DM, procesar
    elif not message.guild:
        async with message.channel.typing():
            response = await query_ollama(message.content, message.author.id)
            
            if len(response) > 2000:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
    
    await bot.process_commands(message)

# ==================== COMANDOS SLASH ====================

@bot.tree.command(name="newchat", description="🔄 Inicia un nuevo chat limpiando el historial")
async def newchat(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    chat_histories[user_id] = []
    logger.log_command(interaction.user.id, "newchat")
    await interaction.response.send_message("✅ Historial de chat limpiado. ¡Empecemos de nuevo!", ephemeral=True)

@bot.tree.command(name="personality", description="🎭 Cambia la personalidad del bot")
@app_commands.describe(style="Estilo de personalidad que deseas")
@app_commands.choices(style=[
    app_commands.Choice(name="👔 Profesional", value="professional"),
    app_commands.Choice(name="😊 Amigo", value="friendly"),
    app_commands.Choice(name="📚 Mentor", value="mentor"),
    app_commands.Choice(name="🎉 Entusiasta", value="enthusiastic")
])
async def personality(interaction: discord.Interaction, style: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    personality_mgr.set_personality(interaction.user.id, style)
    p_info = personality_mgr.get_personality(interaction.user.id)
    
    logger.log_command(interaction.user.id, f"personality:{style}")
    
    embed = discord.Embed(
        title="🎭 Personalidad Actualizada",
        description=f"**{p_info['name']}**\n{p_info['description']}",
        color=discord.Color.purple()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="export", description="💾 Exporta tu historial de chat")
@app_commands.describe(format="Formato de exportación")
@app_commands.choices(format=[
    app_commands.Choice(name="📦 DOB (formato propietario)", value="dob"),
    app_commands.Choice(name="📄 TXT (texto plano)", value="txt")
])
async def export(interaction: discord.Interaction, format: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    history = chat_histories.get(user_id, [])
    if not history:
        await interaction.response.send_message("❌ No hay historial para exportar.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        if format == "dob":
            file_path = exporter.export_to_dob(history, interaction.user.id)
        else:
            file_path = exporter.export_to_txt(history, interaction.user.id)
        
        logger.log_command(interaction.user.id, f"export:{format}")
        await interaction.followup.send(
            f"✅ Chat exportado en formato **{format.upper()}**\n"
            f"📊 {len(history)} mensajes exportados",
            file=discord.File(file_path),
            ephemeral=True
        )
    except Exception as e:
        logger.log_error(f"Error exporting chat: {str(e)}")
        await interaction.followup.send(f"❌ Error al exportar: {str(e)}", ephemeral=True)

@bot.tree.command(name="import", description="📥 Importa un historial de chat")
@app_commands.describe(file="Archivo de chat exportado (.dob o .txt)")
async def import_chat(interaction: discord.Interaction, file: discord.Attachment):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Descargar archivo
        file_bytes = await file.read()
        temp_path = Path("exports") / f"temp_{user_id}{file.filename[-4:]}"
        temp_path.write_bytes(file_bytes)
        
        # Importar
        history = exporter.import_chat(str(temp_path))
        chat_histories[user_id] = history
        
        temp_path.unlink()  # Eliminar archivo temporal
        
        logger.log_command(interaction.user.id, "import")
        await interaction.followup.send(
            f"✅ Chat importado exitosamente!\n"
            f"📊 {len(history)} mensajes cargados",
            ephemeral=True
        )
    except Exception as e:
        logger.log_error(f"Error importing chat: {str(e)}")
        await interaction.followup.send(f"❌ Error al importar: {str(e)}", ephemeral=True)

@bot.tree.command(name="stats", description="📊 Muestra tus estadísticas y lanza el dashboard web")
async def stats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Iniciar servidor web si no está corriendo
    server_started = start_web_server()
    
    user_stats = stats_mgr.get_user_stats(interaction.user.id)
    
    embed = discord.Embed(
        title="📊 Tus Estadísticas de Uso",
        description="Métricas personales de tu interacción con el bot",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    if user_stats:
        embed.add_field(
            name="💬 Mensajes",
            value=f"**{user_stats['total_messages']}**",
            inline=True
        )
        embed.add_field(
            name="🔤 Tokens",
            value=f"**{user_stats['total_tokens']:,}**",
            inline=True
        )
        embed.add_field(
            name="⏱️ Tiempo Promedio",
            value=f"**{user_stats['avg_response_time']:.2f}s**",
            inline=True
        )
    else:
        embed.add_field(
            name="ℹ️ Sin Datos",
            value="No hay estadísticas disponibles aún.\n¡Empieza a chatear!",
            inline=False
        )
    
    # Información del dashboard web
    if server_started:
        embed.add_field(
            name="🌐 Dashboard Web",
            value="**[Ver Dashboard Completo](http://localhost:5000)**\n"
                  "```\nURL: http://localhost:5000\n"
                  "📈 Gráficos en tiempo real\n"
                  "📊 Estadísticas globales\n"
                  "🔄 Auto-refresh```",
            inline=False
        )
        embed.set_footer(text="✅ Servidor web iniciado automáticamente")
    else:
        embed.set_footer(text="⚠️ No se pudo iniciar el servidor web")
    
    logger.log_command(interaction.user.id, "stats")
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setchannel", description="⚙️ Configura el canal del bot (Solo Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = interaction.channel.id
    
    channel_config[guild_id] = channel_id
    save_channel_config()
    
    logger.log_command(interaction.user.id, f"setchannel:{channel_id}")
    
    embed = discord.Embed(
        title="⚙️ Canal Configurado",
        description=f"El bot ahora solo responderá en {interaction.channel.mention}",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="help", description="❓ Muestra todos los comandos disponibles")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Comandos del Bot",
        description="Lista completa de comandos slash disponibles",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="🔄 /newchat",
        value="Limpia el historial y empieza una conversación nueva",
        inline=False
    )
    embed.add_field(
        name="🎭 /personality",
        value="Cambia la personalidad del bot\n`Opciones: Profesional, Amigo, Mentor, Entusiasta`",
        inline=False
    )
    embed.add_field(
        name="💾 /export",
        value="Exporta tu historial de chat\n`Formatos: DOB (propietario), TXT (texto)`",
        inline=False
    )
    embed.add_field(
        name="📥 /import",
        value="Importa un historial de chat previamente exportado",
        inline=False
    )
    embed.add_field(
        name="📊 /stats",
        value="Muestra tus estadísticas y **lanza el dashboard web**\n`Dashboard: http://localhost:5000`",
        inline=False
    )
    embed.add_field(
        name="⚙️ /setchannel",
        value="**[Admin]** Configura el canal donde el bot responderá",
        inline=False
    )
    embed.add_field(
        name="❓ /help",
        value="Muestra esta ayuda",
        inline=False
    )
    
    embed.set_footer(text="💡 Todos los comandos son slash commands (/)")
    
    logger.log_command(interaction.user.id, "help")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Manejador de errores
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ No tienes permisos para usar este comando.",
            ephemeral=True
        )
    else:
        logger.log_error(f"Command error: {str(error)}")
        await interaction.response.send_message(
            f"❌ Error: {str(error)}",
            ephemeral=True
        )

def run():
    """Función principal para ejecutar el bot."""
    if not TOKEN:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en .env")
        return
    
    if not AUTHORIZED_IDS or AUTHORIZED_IDS == ['']:
        print("❌ ERROR: No hay IDs autorizados en .env")
        return
    
    print("🚀 Iniciando bot...")
    print("📋 Todos los comandos son slash commands (/)")
    print("🌐 El servidor web se iniciará automáticamente con /stats")
    logger.log_info("Bot starting...")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.log_error(f"Bot crashed: {str(e)}")
        print(f"❌ Error crítico: {str(e)}")

if __name__ == "__main__":
    run() 