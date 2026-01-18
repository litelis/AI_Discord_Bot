#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Bot Principal
Bot de Discord inteligente con IA local usando Ollama
"""

import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import asyncio

# Importar módulos propios
from logger import BotLogger
from personality import PersonalityManager
from chat_export import ChatExporter
from stats import StatsManager

# Cargar variables de entorno
load_dotenv()

# Configuración
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_IDS = [int(id) for id in os.getenv("AUTHORIZED_IDS", "").split(",") if id]
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Inicializar managers
logger = BotLogger()
personality_manager = PersonalityManager()
chat_exporter = ChatExporter()
stats_manager = StatsManager()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Almacenamiento de conversaciones
conversations = {}
response_channel_id = None


def is_authorized(user_id: int) -> bool:
    """Verifica si el usuario está autorizado"""
    if not AUTHORIZED_IDS:
        return True
    return user_id in AUTHORIZED_IDS


def get_conversation(user_id: int) -> list:
    """Obtiene la conversación de un usuario"""
    if user_id not in conversations:
        conversations[user_id] = []
    return conversations[user_id]


def add_to_conversation(user_id: int, role: str, content: str):
    """Añade un mensaje a la conversación"""
    conversation = get_conversation(user_id)
    conversation.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # Limitar a últimos 20 mensajes
    if len(conversation) > 20:
        conversations[user_id] = conversation[-20:]


async def generate_response(user_id: int, prompt: str) -> str:
    """Genera una respuesta usando Ollama"""
    try:
        start_time = datetime.now()
        
        # Obtener personalidad y contexto
        personality = personality_manager.get_personality(user_id)
        system_prompt = personality_manager.get_system_prompt(personality)
        
        # Construir contexto de conversación
        conversation = get_conversation(user_id)
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation[-10:]
        ])
        
        # Construir prompt completo
        full_prompt = f"{system_prompt}\n\nContexto de conversación:\n{context}\n\nUsuario: {prompt}\nAsistente:"
        
        # Llamar a Ollama
        data = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 500
            }
        }
        
        if USE_GPU:
            data["options"]["num_gpu"] = 1
        
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result.get("response", "").strip()
        
        # Calcular tiempo de respuesta
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Registrar estadísticas
        stats_manager.add_interaction(
            user_id=user_id,
            tokens_used=result.get("eval_count", 0),
            response_time=response_time
        )
        
        logger.log_message(user_id, prompt, ai_response, response_time)
        
        return ai_response
        
    except requests.exceptions.Timeout:
        logger.log_error(user_id, "Timeout en Ollama")
        return "⏱️ Lo siento, la respuesta está tardando mucho. Por favor intenta de nuevo."
    except requests.exceptions.ConnectionError:
        logger.log_error(user_id, "Error de conexión con Ollama")
        return "❌ No puedo conectar con Ollama. Asegúrate de que esté corriendo."
    except Exception as e:
        logger.log_error(user_id, f"Error generando respuesta: {str(e)}")
        return f"❌ Error al generar respuesta: {str(e)}"


@bot.event
async def on_ready():
    """Evento cuando el bot está listo"""
    logger.log_info(f"Bot iniciado como {bot.user}")
    print(f"\n✅ Bot conectado como {bot.user}")
    print(f"📊 Servidores: {len(bot.guilds)}")
    print(f"👥 Usuarios autorizados: {len(AUTHORIZED_IDS) if AUTHORIZED_IDS else 'Todos'}")
    
    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        logger.log_info(f"Sincronizados {len(synced)} comandos")
        print(f"🔄 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        logger.log_error("SYSTEM", f"Error sincronizando comandos: {e}")
        print(f"❌ Error sincronizando comandos: {e}")


@bot.event
async def on_message(message):
    """Evento cuando se recibe un mensaje"""
    # Ignorar mensajes del bot
    if message.author == bot.user:
        return
    
    # Verificar canal de respuesta configurado
    global response_channel_id
    if response_channel_id and message.channel.id != response_channel_id:
        return
    
    # Verificar autorización
    if not is_authorized(message.author.id):
        return
    
    # Si el mensaje menciona al bot o es DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            # Obtener contenido sin menciones
            content = message.content.replace(f"<@{bot.user.id}>", "").strip()
            
            if not content:
                await message.channel.send("👋 ¡Hola! ¿En qué puedo ayudarte?")
                return
            
            # Añadir a conversación
            add_to_conversation(message.author.id, "user", content)
            
            # Generar respuesta
            response = await generate_response(message.author.id, content)
            
            # Añadir respuesta a conversación
            add_to_conversation(message.author.id, "assistant", response)
            
            # Enviar respuesta (dividir si es muy larga)
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
    
    await bot.process_commands(message)


@bot.tree.command(name="newchat", description="Inicia una nueva conversación limpiando el historial")
async def newchat(interaction: discord.Interaction):
    """Comando para limpiar el historial de conversación"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message("❌ No estás autorizado para usar este comando.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    conversations[user_id] = []
    
    logger.log_command(user_id, "newchat")
    await interaction.response.send_message("🔄 Conversación reiniciada. ¡Empecemos de nuevo!", ephemeral=True)


@bot.tree.command(name="personality", description="Cambia la personalidad del bot")
@app_commands.describe(style="Elige el estilo de personalidad")
@app_commands.choices(style=[
    app_commands.Choice(name="🎓 Profesional", value="profesional"),
    app_commands.Choice(name="😊 Amigo", value="amigo"),
    app_commands.Choice(name="👨‍🏫 Mentor", value="mentor"),
    app_commands.Choice(name="🎉 Entusiasta", value="entusiasta")
])
async def personality(interaction: discord.Interaction, style: app_commands.Choice[str]):
    """Comando para cambiar la personalidad"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message("❌ No estás autorizado para usar este comando.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    personality_manager.set_personality(user_id, style.value)
    
    descriptions = {
        "profesional": "🎓 formal y preciso",
        "amigo": "😊 casual y cercano",
        "mentor": "👨‍🏫 educativo y paciente",
        "entusiasta": "🎉 energético y motivador"
    }
    
    logger.log_command(user_id, f"personality:{style.value}")
    await interaction.response.send_message(
        f"✅ Personalidad cambiada a: **{style.name}**\n"
        f"Ahora hablaré de forma {descriptions[style.value]}",
        ephemeral=True
    )


@bot.tree.command(name="export", description="Exporta tu historial de chat")
@app_commands.describe(format="Formato de exportación")
@app_commands.choices(format=[
    app_commands.Choice(name="📦 DOB (Discord Ollama Bot)", value="dob"),
    app_commands.Choice(name="📄 TXT (Texto plano)", value="txt")
])
async def export(interaction: discord.Interaction, format: app_commands.Choice[str]):
    """Comando para exportar el chat"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message("❌ No estás autorizado para usar este comando.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    conversation = get_conversation(user_id)
    
    if not conversation:
        await interaction.response.send_message("❌ No hay historial para exportar.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Exportar según formato
        if format.value == "dob":
            filepath = chat_exporter.export_dob(user_id, conversation)
        else:
            filepath = chat_exporter.export_txt(user_id, conversation)
        
        # Enviar archivo
        with open(filepath, 'rb') as f:
            file = discord.File(f, filename=Path(filepath).name)
            await interaction.followup.send(
                f"✅ Historial exportado en formato **{format.name}**",
                file=file,
                ephemeral=True
            )
        
        logger.log_command(user_id, f"export:{format.value}")
        
    except Exception as e:
        logger.log_error(user_id, f"Error exportando: {str(e)}")
        await interaction.followup.send(f"❌ Error al exportar: {str(e)}", ephemeral=True)


@bot.tree.command(name="import", description="Importa un historial de chat previamente exportado")
async def import_chat(interaction: discord.Interaction, archivo: discord.Attachment):
    """Comando para importar un chat"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message("❌ No estás autorizado para usar este comando.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Descargar archivo
        temp_path = f"data/temp_{user_id}_{archivo.filename}"
        await archivo.save(temp_path)
        
        # Importar según extensión
        imported_data = chat_exporter.import_chat(temp_path)
        
        if imported_data:
            conversations[user_id] = imported_data
            await interaction.followup.send(
                f"✅ Historial importado correctamente\n"
                f"📊 {len(imported_data)} mensajes cargados",
                ephemeral=True
            )
            logger.log_command(user_id, "import:success")
        else:
            await interaction.followup.send("❌ Error: Archivo corrupto o inválido", ephemeral=True)
            logger.log_error(user_id, "Import failed: Invalid file")
        
        # Limpiar archivo temporal
        Path(temp_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.log_error(user_id, f"Error importando: {str(e)}")
        await interaction.followup.send(f"❌ Error al importar: {str(e)}", ephemeral=True)


@bot.tree.command(name="stats", description="Muestra tus estadísticas de uso")
async def stats(interaction: discord.Interaction):
    """Comando para ver estadísticas"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message("❌ No estás autorizado para usar este comando.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    user_stats = stats_manager.get_user_stats(user_id)
    
    if not user_stats:
        await interaction.response.send_message("📊 Aún no tienes estadísticas.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Tus Estadísticas",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="💬 Mensajes",
        value=f"{user_stats['total_messages']} mensajes",
        inline=True
    )
    
    embed.add_field(
        name="🔢 Tokens",
        value=f"{user_stats['total_tokens']:,} tokens",
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Tiempo Promedio",
        value=f"{user_stats['avg_response_time']:.2f}s",
        inline=True
    )
    
    embed.set_footer(text=f"Usuario: {interaction.user.name}")
    
    logger.log_command(user_id, "stats")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="setchannel", description="[ADMIN] Configura el canal donde el bot responde")
async def setchannel(interaction: discord.Interaction):
    """Comando para configurar el canal de respuesta"""
    # Verificar permisos de administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Necesitas permisos de administrador.", ephemeral=True)
        return
    
    global response_channel_id
    response_channel_id = interaction.channel.id
    
    logger.log_command(interaction.user.id, f"setchannel:{interaction.channel.id}")
    await interaction.response.send_message(
        f"✅ Canal configurado: {interaction.channel.mention}\n"
        f"El bot solo responderá en este canal.",
        ephemeral=True
    )


@bot.tree.command(name="help", description="Muestra todos los comandos disponibles")
async def help_command(interaction: discord.Interaction):
    """Comando de ayuda"""
    embed = discord.Embed(
        title="🤖 Comandos del Bot",
        description="Lista de comandos disponibles",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💬 Conversación",
        value=(
            "`/newchat` - Reinicia la conversación\n"
            "`/personality` - Cambia el estilo del bot\n"
            "`Menciona al bot` - Habla con la IA"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💾 Datos",
        value=(
            "`/export` - Exporta tu historial\n"
            "`/import` - Importa un historial\n"
            "`/stats` - Ver tus estadísticas"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Admin",
        value="`/setchannel` - Configurar canal del bot",
        inline=False
    )
    
    embed.set_footer(text="Bot de Discord con Ollama v2.0")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


def main():
    """Función principal para iniciar el bot"""
    if not DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN no configurado en .env")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.log_error("SYSTEM", "Token de Discord inválido")
        print("❌ ERROR: Token de Discord inválido")
    except Exception as e:
        logger.log_error("SYSTEM", f"Error fatal: {str(e)}")
        print(f"❌ ERROR FATAL: {e}")


if __name__ == "__main__":
    main()