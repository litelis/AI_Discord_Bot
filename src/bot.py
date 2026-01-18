import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import threading
import requests
import pickle
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Importar módulos locales (asumiendo que están en la misma carpeta o en el path)
try:
    from logger import BotLogger
    from stats import StatsManager
    from personality import PersonalityManager
    from chat_export import ChatExporter
    from web_server import WebServer
except ImportError:
    # Intento de importación alternativa si se ejecuta desde fuera de src
    sys.path.append(str(Path(__file__).parent))
    from logger import BotLogger
    from stats import StatsManager
    from personality import PersonalityManager
    from chat_export import ChatExporter
    from web_server import WebServer

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

# Variables globales y almacenamiento
web_server_running = False
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

def save_chats_data():
    """Guarda los chats en disco."""
    with open(SAVE_DIR / "saved_chats.pkl", 'wb') as f:
        pickle.dump(saved_chats, f)

def save_channel_config():
    """Guarda la configuración de canales."""
    with open(SAVE_DIR / "channel_config.pkl", 'wb') as f:
        pickle.dump(channel_config, f)

def get_ollama_response(user_id, message):
    """Obtiene respuesta del modelo Ollama manteniendo el contexto."""
    user_id = str(user_id)
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # Obtener personalidad del usuario
    personality = personality_manager.get_personality(user_id)
    system_prompt = personality["system_prompt"]

    # Añadir mensaje del usuario al historial temporal para el contexto
    current_history = chat_histories[user_id] + [{"role": "user", "content": message}]
    
    # Construir contexto (últimos 10 mensajes para no saturar)
    context_msgs = current_history[-10:]
    context_str = f"System: {system_prompt}\n"
    for msg in context_msgs:
        role = "User" if msg['role'] == "user" else "Assistant"
        context_str += f"{role}: {msg['content']}\n"
    
    context_str += "Assistant:"

    start_time = datetime.now()

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": context_str,
            "stream": False
        }

        if USE_GPU:
            payload["options"] = {"num_gpu": 1}

        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        ai_response = result.get('response', 'No pude generar una respuesta.')

        # Actualizar historial real
        chat_histories[user_id].append({"role": "user", "content": message})
        chat_histories[user_id].append({"role": "assistant", "content": ai_response})

        # Registrar estadísticas
        elapsed = (datetime.now() - start_time).total_seconds()
        tokens = len(context_str.split()) + len(ai_response.split()) # Estimación básica
        stats_manager.record_message(user_id, len(message), elapsed, tokens)
        logger.log_message(user_id, len(message), elapsed)

        return ai_response

    except requests.exceptions.ConnectionError:
        return "❌ Error: No se puede conectar a Ollama. Asegúrate de que Ollama esté ejecutándose."
    except Exception as e:
        logger.log_error("Ollama Error", str(e), user_id)
        return f"❌ Error: {str(e)}"

@bot.event
async def on_ready():
    """Evento cuando el bot está listo."""
    global web_server_running
    load_saved_data()
    
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📋 IDs autorizados: {len(AUTHORIZED_IDS)}')
    print(f'🤖 Modelo Ollama: {MODEL_NAME}')
    
    # Iniciar servidor web si no está corriendo
    if not web_server_running:
        try:
            web_server = WebServer(stats_manager, personality_manager, saved_chats, chat_histories)
            web_thread = threading.Thread(target=web_server.run, daemon=True)
            web_thread.start()
            web_server_running = True
            print(f'🌐 Servidor web iniciado en http://localhost:5000')
        except Exception as e:
            print(f"❌ Error al iniciar servidor web: {e}")

    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos slash sincronizados')
    except Exception as e:
        print(f'❌ Error al sincronizar comandos: {e}')

@bot.event
async def on_message(message):
    """Procesa mensajes."""
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    
    if user_id not in AUTHORIZED_IDS:
        return
    
    # Verificar configuración de canal
    guild_id = str(message.guild.id) if message.guild else None
    allowed_channel = channel_config.get(guild_id)
    
    # Responder si: es DM O (está en guild Y es el canal correcto) O (está en guild Y no hay canal configurado)
    should_respond = False
    if not message.guild:
        should_respond = True
    elif allowed_channel and str(message.channel.id) == allowed_channel:
        should_respond = True
    elif not allowed_channel and message.guild:
        should_respond = True # Responder en todos si no hay config
        
    if should_respond and not message.content.startswith(bot.command_prefix):
        async with message.channel.typing():
            # Ejecutar en thread aparte para no bloquear el bot
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, get_ollama_response, user_id, message.content)
            
            if len(response) > 2000:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
    
    await bot.process_commands(message)

# ==================== COMANDOS SLASH ====================

@bot.tree.command(name="newchat", description="🗑️ Limpia el historial de chat actual")
async def newchat(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return
    
    chat_histories[user_id] = []
    logger.log_command(user_id, "newchat")
    await interaction.response.send_message("✅ Historial limpiado. ¡Empecemos de nuevo!")

@bot.tree.command(name="savechat", description="💾 Guarda el chat actual")
@app_commands.describe(nombre="Nombre para identificar este chat")
async def savechat(interaction: discord.Interaction, nombre: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return

    if user_id not in chat_histories or not chat_histories[user_id]:
        await interaction.response.send_message("❌ No hay chat activo para guardar.", ephemeral=True)
        return

    if user_id not in saved_chats:
        saved_chats[user_id] = {}

    saved_chats[user_id][nombre] = chat_histories[user_id].copy()
    save_chats_data()
    stats_manager.record_chat_saved()
    
    await interaction.response.send_message(f"💾 Chat guardado como '**{nombre}**'")

@bot.tree.command(name="loadchat", description="📂 Carga un chat guardado")
@app_commands.describe(nombre="Nombre del chat a cargar")
async def loadchat(interaction: discord.Interaction, nombre: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return

    if user_id not in saved_chats or nombre not in saved_chats[user_id]:
        await interaction.response.send_message(f"❌ No existe el chat '{nombre}'.", ephemeral=True)
        return

    chat_histories[user_id] = saved_chats[user_id][nombre].copy()
    stats_manager.record_chat_loaded()
    
    await interaction.response.send_message(f"📂 Chat '**{nombre}**' cargado.")

@bot.tree.command(name="listchats", description="📋 Lista tus chats guardados")
async def listchats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return
    
    if user_id not in saved_chats or not saved_chats[user_id]:
        await interaction.response.send_message("📭 No tienes chats guardados.", ephemeral=True)
        return
    
    chat_list = [f"• **{name}** ({len(msgs)} msgs)" for name, msgs in saved_chats[user_id].items()]
    await interaction.response.send_message("💬 **Chats guardados:**\n" + "\n".join(chat_list))

@bot.tree.command(name="personality", description="🎭 Cambia la personalidad del bot")
@app_commands.choices(style=[
    app_commands.Choice(name="👔 Profesional", value="profesional"),
    app_commands.Choice(name="😊 Amigo", value="amigo"),
    app_commands.Choice(name="📚 Mentor", value="mentor"),
    app_commands.Choice(name="🎉 Entusiasta", value="entusiasta")
])
async def personality(interaction: discord.Interaction, style: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return
    
    personality_manager.set_personality(user_id, style)
    p_info = personality_manager.get_personality(user_id)
    
    await interaction.response.send_message(f"✅ Personalidad: **{p_info['nombre']}**\n{p_info['descripcion']}")

@bot.tree.command(name="export", description="📤 Exporta un chat guardado a archivo")
@app_commands.describe(nombre="Nombre del chat", formato="TXT o DOB")
@app_commands.choices(formato=[
    app_commands.Choice(name="📄 TXT", value="txt"),
    app_commands.Choice(name="📦 DOB", value="dob")
])
async def export(interaction: discord.Interaction, nombre: str, formato: str):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return

    if user_id not in saved_chats or nombre not in saved_chats[user_id]:
        await interaction.response.send_message(f"❌ Chat '{nombre}' no encontrado.", ephemeral=True)
        return

    history = saved_chats[user_id][nombre]
    try:
        if formato == "txt":
            path = chat_exporter.export_to_txt(history, nombre, user_id)
        else:
            path = chat_exporter.export_to_dob(history, nombre, user_id)
            
        await interaction.response.send_message(f"✅ Exportado.", file=discord.File(path))
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="import", description="📥 Importa un archivo de chat")
async def import_chat(interaction: discord.Interaction, archivo: discord.Attachment):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return

    await interaction.response.defer()
    try:
        content = await archivo.read()
        temp = Path("temp_import_" + archivo.filename)
        with open(temp, 'wb') as f:
            f.write(content)
            
        if archivo.filename.endswith('.dob'):
            data, err = chat_exporter.import_from_dob(temp)
        else:
            data, err = chat_exporter.import_from_txt(temp)
            
        temp.unlink() # Borrar temporal
        
        if err:
            await interaction.followup.send(f"❌ Error: {err}")
            return
            
        if user_id not in saved_chats: saved_chats[user_id] = {}
        saved_chats[user_id][data['chat_name']] = data['messages']
        save_chats_data()
        
        await interaction.followup.send(f"✅ Chat '**{data['chat_name']}**' importado.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error crítico: {e}")

@bot.tree.command(name="stats", description="📊 Ver estadísticas y panel web")
async def stats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in AUTHORIZED_IDS:
        await interaction.response.send_message("❌ No autorizado.", ephemeral=True)
        return

    summary = stats_manager.get_stats_summary()
    embed = discord.Embed(title="📊 Estadísticas", color=discord.Color.blue())
    embed.add_field(name="Mensajes Totales", value=str(summary['total_messages']))
    embed.add_field(name="Tiempo Promedio", value=f"{summary['avg_response_time']:.2f}s")
    embed.add_field(name="🌐 Panel Web", value="http://localhost:5000", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setchannel", description="⚙️ Configura el canal de respuesta (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_config[guild_id] = str(interaction.channel.id)
    save_channel_config()
    await interaction.response.send_message(f"✅ Bot configurado para responder en {interaction.channel.mention}")

import asyncio # Necesario para run_in_executor

if __name__ == "__main__":
    if not TOKEN:
        print("❌ FALTA TOKEN EN .ENV")
    else:
        bot.run(TOKEN)