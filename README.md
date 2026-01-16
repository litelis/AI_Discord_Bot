# 🤖 Bot de Discord con Ollama

Bot de Discord inteligente que utiliza Ollama (modelo gemini-3-flash-preview) para conversaciones con contexto. Solo responde a usuarios autorizados y mantiene el historial de chat para conversaciones más naturales.

## ✨ Características

- 🔐 **Acceso Restringido**: Solo responde a IDs de Discord autorizados
- 💬 **Conversaciones con Contexto**: Mantiene el historial de chat para cada usuario
- 🔄 **Reseteo de Chat**: Comando `/newchat` para limpiar el historial
- 🤖 **IA Local**: Usa Ollama con el modelo gemini-3-flash-preview (ejecutándose en localhost)
- 📝 **Respuestas Largas**: Maneja automáticamente respuestas que exceden el límite de Discord
- 🚀 **Inicio Automático**: Script principal que inicia Ollama y el bot simultáneamente

## 📋 Requisitos Previos

1. **Python 3.8+** instalado
2. **Ollama** instalado ([Descargar aquí](https://ollama.ai))
3. **Git** instalado (para actualizaciones)
4. **Bot de Discord** creado en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)

## 🚀 Instalación Rápida

### Método 1: Instalación Guiada (Recomendado para Primera Vez)

Para configurar todo desde cero, ejecuta:

```bash
python install.py
```

Este script ejecuta en orden:
1. ✅ **Setup** - Configura entorno y descarga modelos
2. ✅ **Config** - Configura TOKEN y usuarios autorizados
3. ✅ **Update** - Verifica actualizaciones del repositorio

Después de cada paso te pregunta si quieres continuar con el siguiente (s/n).

### Método 2: Inicio Rápido (Si Ya Está Configurado)

Una vez configurado, usa:

```bash
python main.py
```

Este script automáticamente:
- ✅ Verifica e inicia Ollama
- ✅ Descarga el modelo de IA si es necesario
- ✅ Te guía en la configuración si no existe
- ✅ Instala dependencias si hace falta
- ✅ Inicia el bot de Discord

### Método 3: Configuración Manual

Si prefieres configurar paso a paso:

**1. Configurar Bot y Usuarios:**

```bash
python src/config.py
```

**2. Instalar Dependencias:**

```bash
python src/setup.py
```

**3. Ejecutar el Bot:**

```bash
python src/bot.py
```

## 🔄 Mantener el Bot Actualizado

Para verificar y aplicar actualizaciones:

```bash
python src/update.py
```

Este script:
- ✅ Verifica automáticamente si hay actualizaciones disponibles
- ✅ Muestra los cambios que se aplicarán
- ✅ Te pregunta si deseas actualizar (s/n)
- ✅ Guarda tus cambios locales antes de actualizar
- ✅ Aplica las actualizaciones automáticamente

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
├── install.py          # 🔧 Instalador completo (setup + config + update)
├── main.py             # 🚀 Lanzador principal (inicio automático)
├── src/                # 📁 Código fuente
│   ├── bot.py          # Código principal del bot
│   ├── config.py       # Configurador interactivo (.env)
│   ├── setup.py        # Instalador de dependencias
│   └── update.py       # Actualizador del repositorio
├── models/             # 📁 Carpeta para modelos de IA
│   └── README.md       # Documentación de modelos
├── .env                # Variables de entorno (no versionado)
├── .gitignore          # Archivos ignorados por Git
├── LICENSE             # Licencia MIT
└── README.md           # Este archivo
```

## 🛠️ Solución de Problemas

### Error: "No se puede conectar a Ollama"

El script `main.py` inicia Ollama automáticamente. Si aún así falla:
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

Ejecuta `python main.py` y el script te preguntará si deseas descargar el modelo automáticamente.

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
- Los modelos de Ollama se gestionan automáticamente por Ollama
- El bot solo responde a usuarios autorizados para mayor seguridad
- Las conversaciones se mantienen en memoria y se pierden al reiniciar el bot
- Usa `python main.py` para el inicio más fácil y automatizado

---

Desarrollado con ❤️ usando Python, Discord.py y Ollama


