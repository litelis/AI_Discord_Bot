# 📁 Carpeta de Modelos

Esta carpeta está destinada para almacenar los modelos de IA de Ollama.

## 🤖 Modelos Soportados

El bot actualmente utiliza:
- **gemini-3-flash-preview** (predeterminado)
- **llama3** (alternativa)

## 📝 Notas

Los modelos de Ollama se almacenan automáticamente en la ubicación del sistema de Ollama, no en esta carpeta. Esta carpeta existe como referencia y puede ser utilizada para:

- Documentación de modelos
- Configuraciones personalizadas
- Archivos de ajuste fino (fine-tuning)
- Prompts del sistema personalizados

## 🔧 Gestión de Modelos

Para ver los modelos instalados:
```bash
ollama list
```

Para descargar un modelo:
```bash
ollama pull gemini-3-flash-preview
```

Para eliminar un modelo:
```bash
ollama rm nombre_del_modelo
```
