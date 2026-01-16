import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
import json

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_IDS = os.getenv('AUTHORIZED_IDS', '').split(',')
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemini-3-flash-preview"  # Modelo de Ollama

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Crear bot
bot = commands.Bot(command_prefix='/', intents=intents)

# Diccionario para almacenar historiales de chat por usuario
chat_histories = {}

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
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📋 IDs autorizados: {AUTHORIZED_IDS}')
    print(f'🤖 Modelo Ollama: {MODEL_NAME}')

@bot.command(name='newchat')
async def new_chat(ctx):
    """Limpia el historial de chat del usuario."""
    user_id = str(ctx.author.id)
    
    if user_id not in AUTHORIZED_IDS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return
    
    if user_id in chat_histories:
        chat_histories[user_id] = []
        await ctx.send("🔄 Historial de chat limpiado. ¡Empecemos de nuevo!")
    else:
        await ctx.send("📝 No hay historial previo. ¡Comienza a chatear!")

@bot.event
async def on_message(message):
    # Ignorar mensajes del bot
    if message.author == bot.user:
        return
    
    user_id = str(message.author.id)
    
    # Procesar comandos primero
    await bot.process_commands(message)
    
    # Si el mensaje es un comando, no continuar
    if message.content.startswith('/'):
        return
    
    # Verificar si el usuario está autorizado
    if user_id not in AUTHORIZED_IDS:
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
