# 🤖 Bot de Discord con Ollama - Versión Avanzada 2.0

Bot de Discord inteligente con IA local usando Ollama (llama3.2), ahora con **características avanzadas profesionales**.

## ✨ Características Principales

### 🎭 Sistema de Personalidades
- **4 personalidades predefinidas**: Profesional, Amigo, Mentor, Entusiasta
- Cada personalidad tiene un system prompt único
- Personalización por usuario
- Comando /personality para cambiar entre estilos

### 📊 Sistema de Estadísticas Avanzado
- Tracking completo de interacciones
- Métricas por usuario: mensajes, tokens, tiempos
- Estadísticas globales del bot
- API REST para consulta de stats
- Dashboard web en tiempo real

### 💾 Export/Import de Chats
- Formato propietario .DOB con marca de agua
- Export a TXT con checksum de integridad
- Verificación de autenticidad al importar
- Magic bytes únicos del bot
- Protección contra manipulación

### 📝 Sistema de Logging Detallado
- Logs con timestamp preciso
- Archivos nombrados por fecha
- Múltiples niveles: DEBUG, INFO, ERROR
- Logging de comandos, mensajes y errores
- Rotación automática de logs

### 🌐 Dashboard Web
- Interface web moderna con Flask
- Gráficos interactivos con Chart.js
- Visualización de estadísticas en tiempo real
- API REST completa
- Auto-refresh cada 30 segundos
- Diseño responsivo y moderno

## 📦 Estructura del Proyecto

`
bot/
├── src/
│   ├── bot.py              # Bot principal con todas las características
│   ├── logger.py           # Sistema de logging avanzado
│   ├── personality.py      # Gestión de personalidades
│   ├── chat_export.py      # Export/Import de chats
│   ├── stats.py            # Sistema de estadísticas
│   ├── web_server.py       # Servidor Flask para dashboard
│   ├── config.py           # Configurador interactivo
│   ├── setup.py            # Instalador de dependencias
│   └── update.py           # Actualizador del repositorio
├── web/
│   ├── templates/
│   │   └── dashboard.html  # Dashboard web
│   └── static/
│       ├── css/           # Estilos
│       └── js/            # Scripts
├── logs/                   # Logs del bot (auto-generados)
├── exports/                # Chats exportados (auto-generados)
├── data/                   # Datos persistentes
├── install.py              # Instalador completo guiado
├── main.py                 # Lanzador automático
├── README.md               # Esta documentación
└── .env                    # Variables de entorno (NO VERSIONADO)
`

## 🚀 Instalación

### Método Rápido
`ash
python install.py
`

### Método Manual
`ash
# 1. Instalar dependencias
python src/setup.py

# 2. Configurar .env
python src/config.py

# 3. Actualizar repo (opcional)
python src/update.py
`

## 📋 Dependencias

`
discord.py >= 2.6.4
python-dotenv >= 1.2.1
requests >= 2.32.5
flask >= 3.1.2
flask-cors >= 6.0.2
`

## 🎮 Comandos del Bot

### Comandos de Usuario
| Comando | Descripción |
|---------|-------------|
| /newchat | Limpia el historial de conversación |
| /personality | Cambia la personalidad del bot |
| /export | Exporta tu historial (DOB o TXT) |
| /import | Importa un historial previamente exportado |
| /stats | Muestra tus estadísticas personales |
| /help | Lista todos los comandos |

### Comandos de Admin
| Comando | Descripción |
|---------|-------------|
| /setchannel | Configura el canal de respuesta del bot |

## 🌐 Dashboard Web

### Iniciar Dashboard
`ash
python src/web_server.py
`

El dashboard estará disponible en: http://localhost:5000

### Características del Dashboard
- 📊 Visualización de estadísticas globales
- 📈 Gráfico de actividad por hora
- 👥 Lista de top usuarios
- 🔄 Auto-refresh cada 30 segundos
- 📱 Diseño responsivo

### API Endpoints
- GET /api/stats - Estadísticas globales
- GET /api/users - Lista de usuarios
- GET /api/user/<id> - Stats de usuario específico
- GET /api/health - Health check

## 🎭 Personalidades Disponibles

### 1. Profesional
- Tono formal y preciso
- Respuestas estructuradas
- Enfoque en eficiencia

### 2. Amigo
- Tono casual y cercano
- Conversación natural
- Uso de emojis

### 3. Mentor
- Tono educativo y paciente
- Explicaciones detalladas
- Fomenta el aprendizaje

### 4. Entusiasta
- Tono energético y positivo
- Celebra logros
- Motivador

## 💾 Formatos de Exportación

### Formato DOB (Discord Ollama Bot)
- Formato binario propietario
- Magic bytes: DOB1
- Marca de agua y timestamp
- Verificación de integridad
- No manipulable

### Formato TXT
- Texto plano legible
- Checksum MD5
- Timestamp de exportación
- Fácil de compartir

## 📝 Sistema de Logging

### Ubicación de Logs
`
logs/
├── bot_YYYY_MM_DD_HH_MM_SS.log    # Log principal
├── commands_YYYY_MM_DD_HH_MM_SS.log # Log de comandos
└── errors_YYYY_MM_DD_HH_MM_SS.log   # Log de errores
`

### Información Registrada
- ✅ Inicio/parada del bot
- 💬 Todos los mensajes procesados
- 🎯 Comandos ejecutados
- ❌ Errores y excepciones
- 📊 Estadísticas de interacción

## ⚙️ Configuración (.env)

`env
DISCORD_TOKEN=tu_token_aqui
AUTHORIZED_IDS=id1,id2,id3
USE_GPU=false
`

## 🔧 Uso Diario

### Iniciar el Bot
`ash
python main.py
`

### Ver Logs en Tiempo Real
`ash
Get-Content logs\bot_*.log -Wait  # Windows
tail -f logs/bot_*.log            # Linux/Mac
`

### Acceder al Dashboard
1. Iniciar bot con python main.py
2. Abrir navegador en http://localhost:5000
3. Ver estadísticas en tiempo real

## 🔄 Actualización

`ash
python src/update.py
`

El script:
1. Verifica actualizaciones disponibles
2. Muestra cambios pendientes
3. Pregunta antes de aplicar
4. Guarda cambios locales automáticamente

## 🐛 Troubleshooting

### Bot no responde
- Verificar Ollama corriendo: ollama serve
- Verificar ID en AUTHORIZED_IDS
- Revisar logs en carpeta logs/

### Dashboard no carga
- Verificar Flask instalado: pip install flask flask-cors
- Verificar puerto 5000 disponible
- Revisar logs de errores

### Error al exportar/importar
- Verificar carpeta exports/ existe
- Verificar permisos de escritura
- Revisar integridad del archivo

## 📈 Estadísticas Disponibles

### Por Usuario
- Total de mensajes
- Total de tokens procesados
- Tiempo promedio de respuesta
- Historial de interacciones

### Globales
- Usuarios activos
- Mensajes totales del bot
- Tokens procesados totales
- Actividad por hora del día
- Comandos más usados

## 🚧 Próximas Características

- [ ] Base de datos SQLite para persistencia
- [ ] Sistema de roles y permisos
- [ ] Múltiples modelos de Ollama seleccionables
- [ ] Rate limiting por usuario
- [ ] Webhooks para notificaciones
- [ ] Backup automático de datos
- [ ] Multi-idioma
- [ ] Tests automatizados

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 👨‍💻 Desarrollo

### Estructura de Código
- Código comentado en español
- Convenciones PEP 8
- Type hints donde sea posible
- Docstrings para funciones principales

### Commits
`ash
git add .
git commit -m "Feature: Descripción del cambio"
git push origin main
`

## 🌟 Changelog

### v2.0 (2026-01-17)
- ✅ Sistema de personalidades
- ✅ Export/Import de chats
- ✅ Sistema de logging avanzado
- ✅ Estadísticas completas
- ✅ Dashboard web con Flask
- ✅ API REST
- ✅ Gráficos interactivos

### v1.2 (2026-01-16)
- ✅ Install.py guiado
- ✅ Main.py auto-lanzador
- ✅ Update.py mejorado

### v1.0 (2026-01-15)
- ✅ Bot básico funcional
- ✅ Integración con Ollama
- ✅ Sistema de comandos

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:
1. Fork del repositorio
2. Crear rama feature
3. Commit de cambios
4. Push a la rama
5. Abrir Pull Request

## 📞 Soporte

- **GitHub Issues**: Para reportar bugs
- **Discussions**: Para preguntas y sugerencias
- **Wiki**: Documentación extendida

---

**Desarrollado con ❤️ usando Ollama y Discord.py**

*Última actualización: 2026-01-17*
