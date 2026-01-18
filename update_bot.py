# Script para actualizar bot.py
print('Actualizando bot.py...')
import shutil
shutil.copy('src/bot.py', 'src/bot.py.old')
print('✅ Backup creado: src/bot.py.old')
print('ℹ️ Por favor actualiza manualmente src/bot.py con el código del artifact')
print('📝 Cambios principales:')
print('  1. Todos los comandos son ahora slash commands (/)')
print('  2. El servidor web se inicia automáticamente con /stats')
print('  3. Emojis añadidos a las descripciones de comandos')
print('  4. Embeds mejorados con más información')
