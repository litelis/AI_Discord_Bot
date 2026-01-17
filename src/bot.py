import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import json
import pickle
from pathlib import Path

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
bot = commands.Bot(command_prefix='/', intents=intents)

# Diccionarios para almacenar datos
chat_histories = {}  # Historial actual por usuario
saved_chats = {}     # Chats guardados {user_id: {chat_name: history}}
channel_config = {}  # Canal configurado por servidor

# Crear carpeta para guardar datos
SAVE_DIR = Path("data")
SAVE_DIR.mkdir(exist_ok=True)

def load_saved_data():
    """Carga chats guardados y configuración de canales."""
    global saved_chats, channel_config
    
    # Cargar chats guardados
    chats_file = SAVE_DIR / "saved_chats.pkl"
    if chats_file.exists():
        try:
            with open(chats_file, 'rb') as f:
                saved_chats = pickle.load(f)
        except:
            saved_chats = {}
    
    # Cargar configuración de canales
    channels_file = SAVE_DIR / "channel_config.pkl"
    if channels_file.exists():
        try:
            with open(channels_file, 'rb') as f:
                channel_config = pickle.load(f)
        except:
            channel_config = {}

def save_chats_data():
    """Guarda los chats en archivo."""
    with open(SAVE_DIR / "saved_chats.pkl", 'wb') as f:
        pickle.dump(saved_chats, f)

def save_channel_config():
    """Guarda la configuración de canales."""
    with open(SAVE_DIR / "channel_config.pkl", 'wb') as f:
        pickle.dump(channel_config, f)

def get_ollama_response(user_id, message):
    """Obtiene respuesta del modelo Ollama manteniendo el contexto."""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    # Añadir mensaje del usuario al historial
    chat_histories[user_id].append({"role": "user", "content": message})
    
    # Construir el prompt con contexto
    context = "\n".join([
        f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}"
        for msg in chat_histories[user_id]
    ])
    
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
    except Exception as e:
        return f"❌ Error al comunicarse con Ollama: {str(e)}"

@bot.event
async def on_ready():
    """Evento cuando el bot se conecta."""
    load_saved_data()
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📋 IDs autorizados: {AUTHORIZED_IDS}')
    print(f'🤖 Modelo Ollama: {MODEL_NAME}')
    print(f'💻 Usando GPU: {"Sí" if USE_GPU else "No"}')
    
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

@bot.event
async def on_message(message):
    """Evento cuando se recibe un mensaje."""
    # Ignorar mensajes del bot
    if message.author == bot.user:
        return
    
    # Procesar comandos
    await bot.process_commands(message)
    
    user_id = str(message.author.id)
    
    # Verificar si el usuario está autorizado
    if user_id not in AUTHORIZED_IDS:
        return
    
    # Verificar si hay canal configurado para este servidor
    if message.guild:
        guild_id = str(message.guild.id)
        if guild_id in channel_config:
            if str(message.channel.id) != channel_config[guild_id]:
                return  # No responder en canales no configurados
    
    # No responder a comandos slash
    if message.content.startswith('/'):
        return
    
    # Mostrar que el bot está escribiendo
    async with message.channel.typing():
        # Obtener respuesta de Ollama
        response = get_ollama_response(user_id, message.content)
        
        # Discord tiene un límite de 2000 caracteres por mensaje
        if len(response) > 2000:
            # Dividir la respuesta en chunks
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await message.channel.send(chunk)
        else:
            await message.channel.send(response)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: No se encontró DISCORD_TOKEN en el archivo .env")
        exit(1)
    
    if not AUTHORIZED_IDS or AUTHORIZED_IDS == ['']:
        print("⚠️ Advertencia: No hay IDs autorizados configurados en AUTHORIZED_IDS")
    
    print("🤖 Iniciando bot...")
    bot.run(TOKEN)
