# 🚀 Configuración de GPU para el Bot de Discord

## 📋 Descripción

Este documento explica cómo configurar tu sistema para usar la GPU con Ollama y el bot de Discord, lo que puede acelerar significativamente las respuestas de la IA.

## ⚡ Ventajas de usar GPU

- **Velocidad:** Respuestas hasta 10x más rápidas
- **Modelos más grandes:** Capacidad para usar modelos más potentes
- **Menor latencia:** Experiencia más fluida para los usuarios
- **Mejor rendimiento:** Procesamiento paralelo más eficiente

## 🖥️ Requisitos

### Hardware
- **GPU NVIDIA:** GTX 1060 o superior (recomendado: RTX series)
- **VRAM:** Mínimo 6GB (recomendado: 8GB o más)
- **RAM:** Mínimo 16GB de RAM del sistema

### Software
- **Drivers NVIDIA:** Última versión de drivers
- **CUDA Toolkit:** Versión 11.8 o superior
- **Windows:** Windows 10/11 (64-bit)

## 📥 Instalación

### 1. Verificar GPU Compatible

Abre PowerShell y ejecuta:

```powershell
nvidia-smi
```

Deberías ver información sobre tu GPU. Si aparece un error, actualiza los drivers de NVIDIA.

### 2. Instalar CUDA Toolkit

1. Descarga CUDA Toolkit desde: https://developer.nvidia.com/cuda-downloads
2. Selecciona tu sistema operativo
3. Sigue el instalador (acepta las opciones predeterminadas)
4. Reinicia tu computadora

### 3. Verificar Instalación de CUDA

```powershell
nvcc --version
```

Deberías ver la versión de CUDA instalada.

### 4. Configurar Ollama para GPU

Ollama detecta automáticamente la GPU en la mayoría de casos. Para verificar:

```powershell
ollama list
```

Cuando ejecutes un modelo, verás en los logs si está usando GPU.

## ⚙️ Configuración del Bot

### Opción 1: Durante la Configuración Inicial

Al ejecutar `python src/config.py`, el script te preguntará:

```
¿Deseas usar GPU para acelerar la IA? (s/n):
```

Responde **s** para habilitar GPU.

### Opción 2: Configuración Manual

Edita el archivo `.env` y añade/modifica:

```env
USE_GPU=true
```

Para deshabilitar GPU:

```env
USE_GPU=false
```

## 🧪 Prueba de Rendimiento

### Probar sin GPU (RAM)

1. En `.env`, establece: `USE_GPU=false`
2. Ejecuta: `python main.py`
3. Envía un mensaje al bot y mide el tiempo de respuesta

### Probar con GPU

1. En `.env`, establece: `USE_GPU=true`
2. Reinicia el bot: `python main.py`
3. Envía el mismo mensaje y compara el tiempo

**Nota:** La primera ejecución con GPU puede ser más lenta mientras se carga el modelo en VRAM.

## 📊 Monitoreo de Uso de GPU

### Durante la Ejecución

Abre otra terminal y ejecuta:

```powershell
nvidia-smi -l 1
```

Esto mostrará el uso de GPU cada segundo. Deberías ver:
- **GPU-Util:** % de uso de la GPU
- **Memory-Usage:** VRAM utilizada
- **Power:** Consumo energético

### Logs del Bot

El bot mostrará en la consola:

```
✅ Bot conectado como [nombre]
📋 IDs autorizados: [IDs]
🤖 Modelo Ollama: gemini-3-flash-preview
💻 Usando GPU: Sí
```

## 🔧 Solución de Problemas

### La GPU no se detecta

**Síntomas:** El bot funciona pero no usa GPU

**Soluciones:**
1. Verifica drivers de NVIDIA actualizados
2. Reinstala CUDA Toolkit
3. Verifica que Ollama esté usando la versión con soporte GPU
4. Reinicia Ollama: `taskkill /F /IM ollama.exe` y vuelve a iniciar

### Error "CUDA out of memory"

**Síntomas:** Error al procesar mensajes largos

**Soluciones:**
1. Usa un modelo más pequeño (llama3 en lugar de gemini)
2. Cierra otras aplicaciones que usen GPU
3. Reduce el tamaño del contexto con `/newchat`
4. Considera actualizar a una GPU con más VRAM

### Bajo rendimiento con GPU

**Síntomas:** GPU habilitada pero no mejora velocidad

**Soluciones:**
1. Verifica que el modelo esté en VRAM (nvidia-smi)
2. Asegúrate que el modelo esté completamente descargado
3. Cierra aplicaciones en segundo plano
4. Verifica temperatura de GPU (no debe hacer throttling)

### Bot se congela

**Síntomas:** El bot no responde al usar GPU

**Soluciones:**
1. Verifica que tienes suficiente VRAM libre
2. Reduce el tamaño del contexto
3. Reinicia Ollama
4. Desactiva GPU temporalmente y reporta el problema

## 💾 Modelos Recomendados por GPU

### 6GB VRAM
- llama3 (recomendado)
- mistral
- gemma

### 8GB VRAM
- llama3
- gemini-3-flash-preview
- codellama

### 12GB+ VRAM
- Cualquier modelo
- Múltiples modelos en memoria

## 🔄 Cambiar entre GPU y RAM

### En Tiempo Real

No necesitas reiniciar el sistema, solo el bot:

1. Edita `.env` y cambia `USE_GPU`
2. Detén el bot (Ctrl+C)
3. Inicia el bot nuevamente: `python main.py`

### Cuándo usar RAM vs GPU

**Usa RAM cuando:**
- No tienes GPU compatible
- La GPU está ocupada con otras tareas (gaming, renderizado)
- Quieres ahorrar energía
- Los mensajes son muy cortos y simples

**Usa GPU cuando:**
- Necesitas respuestas más rápidas
- Usas modelos grandes
- Hay múltiples usuarios simultáneos
- Mensajes largos o complejos

## 📈 Benchmarks Aproximados

| Configuración | Tiempo Respuesta | Uso Memoria | Energía |
|---------------|------------------|-------------|---------|
| RAM (16GB) | 5-15 seg | 2-4GB RAM | Bajo |
| GPU (RTX 3060) | 1-3 seg | 4-6GB VRAM | Medio |
| GPU (RTX 4090) | 0.5-1 seg | 6-8GB VRAM | Alto |

*Tiempos aproximados para mensajes de complejidad media con gemini-3-flash-preview*

## 🆘 Recursos Adicionales

- **Ollama GPU Docs:** https://github.com/ollama/ollama/blob/main/docs/gpu.md
- **NVIDIA CUDA Docs:** https://docs.nvidia.com/cuda/
- **Discord del Proyecto:** [Tu servidor de Discord]
- **Issues de GitHub:** https://github.com/litelis/AI_Discord_Bot/issues

## ⚠️ Notas Importantes

1. **Consumo energético:** GPU consume más energía que RAM
2. **Calor:** Monitorea temperaturas, especialmente en laptops
3. **VRAM suficiente:** Asegúrate de tener VRAM libre antes de iniciar
4. **Drivers actualizados:** Mantén drivers de NVIDIA al día
5. **Primera carga:** Primera ejecución con GPU será lenta (carga modelo a VRAM)

## 📞 Soporte

Si tienes problemas:
1. Revisa esta guía completa
2. Verifica los logs del bot
3. Ejecuta `nvidia-smi` y revisa el estado
4. Abre un issue en GitHub con detalles completos

---

**Última actualización:** 2026-01-17  
**Versión:** 1.0  
