# 🤖 Bot de Discord con Ollama

Bot de Discord inteligente que utiliza Ollama (modelo gemini-3-flash-preview) para conversaciones con contexto. Solo responde a usuarios autorizados y mantiene el historial de chat para conversaciones más naturales.

## ✨ Características

- 🔐 **Acceso Restringido**: Solo responde a IDs de Discord autorizados
- 💬 **Conversaciones con Contexto**: Mantiene el historial de chat para cada usuario
- 🔄 **Reseteo de Chat**: Comando `/newchat` para limpiar el historial
- 🤖 **IA Local**: Usa Ollama con el modelo gemini-3-flash-preview (ejecutándose en localhost)
- 📝 **Respuestas Largas**: Maneja automáticamente respuestas que exceden el límite de Discord

## 📋 Requisitos Previos

1. **Python 3.8+** instalado
2. **Ollama** instalado y ejecutándose ([Descargar aquí](https://ollama.ai))
3. **Bot de Discord** creado en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)

## 🚀 Instalación Rápida

### 1. Configurar Bot y Usuarios Autorizados

Primero, ejecuta el script de configuración interactivo:

```bash
python config.py
```

Este script te pedirá:
- 🔑 **Token del Bot de Discord** (desde el [Portal de Desarrolladores](https://discord.com/developers/applications))
- 👥 **IDs de usuarios autorizados** (tu ID de Discord y otros que quieras autorizar)

El script creará automáticamente el archivo `.env` con tu configuración.

### 2. Instalación del Entorno

Después de configurar, ejecuta:

```bash
python setup.py
```

Este script automáticamente:
- ✅ Crea el entorno virtual `.venv`
- ✅ Instala todas las dependencias (`discord.py`, `python-dotenv`, `requests`)
- ✅ Verifica si Ollama está instalado
- ✅ Descarga el modelo `gemini-3-flash-preview` de Ollama (con fallback a llama3)

### 3. Ejecutar el Bot

Asegúrate de que Ollama esté ejecutándose, luego:

```bash
python bot.py
```

## 🎮 Uso

### Conversación Normal

Simplemente envía mensajes directos al bot en cualquier canal donde esté presente. El bot mantendrá el contexto de la conversación.

```
Usuario: Hola, ¿cómo estás?
Bot: ¡Hola! Estoy funcionando perfectamente. ¿En qué puedo ayudarte hoy?

Usuario: ¿Recuerdas de qué hablamos antes?
Bot: Sí, acabas de preguntarme cómo estaba...
```

### Comando `/newchat`

Limpia el historial de conversación para empezar de cero:

```
/newchat
```

## 🔧 Estructura del Proyecto

```
bot/
├── bot.py              # Código principal del bot
├── config.py           # Configurador interactivo (.env)
├── setup.py            # Script de configuración automática
├── .env                # Variables de entorno (no versionado)
├── .gitignore          # Archivos ignorados por Git
├── LICENSE             # Licencia MIT
├── README.md           # Este archivo
└── .venv/              # Entorno virtual (creado por setup.py)
```

## 🛠️ Solución de Problemas

### Error: "No se puede conectar a Ollama"

Asegúrate de que Ollama esté ejecutándose:
```bash
ollama serve
```

### Error: "No tienes permiso para usar este comando"

Verifica que tu ID de Discord esté en la lista `AUTHORIZED_IDS` del archivo `.env`.

### El bot no responde

1. Verifica que el bot tenga los permisos necesarios en el servidor
2. Asegúrate de que tu ID esté en `AUTHORIZED_IDS`
3. Revisa que Ollama esté ejecutándose en `localhost:11434`

### Modelo no disponible

Si gemini-3-flash-preview no está disponible, el setup.py automáticamente intentará descargar llama3 como alternativa. En ese caso, actualiza la variable `MODEL_NAME` en bot.py a `"llama3"`.

## 📚 Dependencias

- `discord.py` - Librería para interactuar con Discord
- `python-dotenv` - Cargar variables de entorno desde `.env`
- `requests` - Comunicación HTTP con Ollama

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Siéntete libre de abrir issues o pull requests.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## ⚠️ Notas Importantes

- El archivo `.env` **NUNCA** debe ser versionado en Git (ya está en `.gitignore`)
- Ollama debe estar ejecutándose localmente para que el bot funcione
- El bot solo responde a usuarios autorizados para mayor seguridad
- Las conversaciones se mantienen en memoria y se pierden al reiniciar el bot

---

Desarrollado con ❤️ usando Python, Discord.py y Ollama
