import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import json
import pickle
from pathlib import Path
import asyncio
from datetime import datetime
import threading

# Importar sistemas nuevos
from logger import BotLogger
from personality import PersonalityManager
from chat_export import ChatExporter
from stats import StatsManager
from web_server import start_server_thread

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_IDS = os.getenv('AUTHORIZED_IDS', '').split(',')
CHANNEL_ID = os.getenv('CHANNEL_ID', None)
USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

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
    except Exception as e:
        logger.log_error(f"Error querying Ollama: {str(e)}")
        return f"❌ Error al consultar Ollama: {str(e)}"

def start_web_server():
    """Inicia el servidor web si no está corriendo."""
    global web_server_running, web_server_thread
    
    if not web_server_running:
        try:
            web_server_thread = start_server_thread(host='127.0.0.1', port=5000)
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
    print(f'🤖 Modelo: {MODEL_NAME}')
    print(f'🔗 Ollama URL: {OLLAMA_URL}')
    print(f'👥 IDs autorizados: {len(AUTHORIZED_IDS)}')
    print(f'📋 Usa /help para ver los comandos slash disponibles')

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