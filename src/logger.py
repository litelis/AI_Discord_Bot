#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Sistema de Logging
Logging avanzado con múltiples niveles y archivos separados
"""

import logging
from datetime import datetime
from pathlib import Path
import json


class BotLogger:
    """Gestor de logging para el bot"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Inicializa el sistema de logging
        
        Args:
            log_dir: Directorio donde guardar los logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Timestamp para nombres de archivo
        self.timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        
        # Configurar loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Configura los diferentes loggers"""
        # Formato de log
        log_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Logger principal
        self.main_logger = logging.getLogger('bot_main')
        self.main_logger.setLevel(logging.DEBUG)
        
        main_handler = logging.FileHandler(
            self.log_dir / f'bot_{self.timestamp}.log',
            encoding='utf-8'
        )
        main_handler.setFormatter(log_format)
        self.main_logger.addHandler(main_handler)
        
        # Logger de comandos
        self.command_logger = logging.getLogger('bot_commands')
        self.command_logger.setLevel(logging.INFO)
        
        command_handler = logging.FileHandler(
            self.log_dir / f'commands_{self.timestamp}.log',
            encoding='utf-8'
        )
        command_handler.setFormatter(log_format)
        self.command_logger.addHandler(command_handler)
        
        # Logger de errores
        self.error_logger = logging.getLogger('bot_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(
            self.log_dir / f'errors_{self.timestamp}.log',
            encoding='utf-8'
        )
        error_handler.setFormatter(log_format)
        self.error_logger.addHandler(error_handler)
        
        # También log a consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        
        self.main_logger.addHandler(console_handler)
    
    def log_info(self, message: str):
        """
        Log de información general
        
        Args:
            message: Mensaje a registrar
        """
        self.main_logger.info(message)
    
    def log_debug(self, message: str):
        """
        Log de debug
        
        Args:
            message: Mensaje a registrar
        """
        self.main_logger.debug(message)
    
    def log_error(self, user_id: int | str, error: str):
        """
        Log de errores
        
        Args:
            user_id: ID del usuario o SYSTEM
            error: Descripción del error
        """
        message = f"User {user_id}: {error}"
        self.error_logger.error(message)
        self.main_logger.error(message)
    
    def log_command(self, user_id: int, command: str):
        """
        Log de comandos ejecutados
        
        Args:
            user_id: ID del usuario
            command: Comando ejecutado
        """
        message = f"User {user_id} executed: /{command}"
        self.command_logger.info(message)
        self.main_logger.info(message)
    
    def log_message(self, user_id: int, prompt: str, response: str, response_time: float):
        """
        Log de mensajes e interacciones
        
        Args:
            user_id: ID del usuario
            prompt: Mensaje del usuario
            response: Respuesta del bot
            response_time: Tiempo de respuesta en segundos
        """
        # Log básico
        message = f"User {user_id} - Response time: {response_time:.2f}s"
        self.main_logger.info(message)
        
        # Log detallado en JSON
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response": response[:100] + "..." if len(response) > 100 else response,
            "response_time": response_time,
            "prompt_length": len(prompt),
            "response_length": len(response)
        }
        
        # Guardar interacciones detalladas
        interactions_file = self.log_dir / f'interactions_{self.timestamp}.jsonl'
        with open(interactions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(interaction_data, ensure_ascii=False) + '\n')
    
    def log_startup(self, config: dict):
        """
        Log de inicio del bot con configuración
        
        Args:
            config: Diccionario con la configuración
        """
        self.main_logger.info("="*60)
        self.main_logger.info("BOT STARTING")
        self.main_logger.info("="*60)
        
        for key, value in config.items():
            # No loguear tokens completos
            if 'token' in key.lower():
                value = value[:8] + "..." if value else "NOT SET"
            self.main_logger.info(f"{key}: {value}")
        
        self.main_logger.info("="*60)
    
    def log_shutdown(self):
        """Log de cierre del bot"""
        self.main_logger.info("="*60)
        self.main_logger.info("BOT SHUTTING DOWN")
        self.main_logger.info("="*60)
    
    def get_log_files(self) -> list:
        """
        Obtiene lista de archivos de log
        
        Returns:
            Lista de rutas de archivos de log
        """
        return list(self.log_dir.glob('*.log'))
    
    def get_latest_errors(self, count: int = 10) -> list:
        """
        Obtiene los últimos errores registrados
        
        Args:
            count: Número de errores a obtener
            
        Returns:
            Lista de errores recientes
        """
        errors = []
        error_files = sorted(
            self.log_dir.glob('errors_*.log'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if error_files:
            with open(error_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                errors = lines[-count:]
        
        return errors
    
    def get_interaction_stats(self) -> dict:
        """
        Obtiene estadísticas de las interacciones
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "total_interactions": 0,
            "avg_response_time": 0,
            "total_prompt_chars": 0,
            "total_response_chars": 0
        }
        
        interaction_files = list(self.log_dir.glob('interactions_*.jsonl'))
        
        if not interaction_files:
            return stats
        
        total_time = 0
        
        for file in interaction_files:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        stats["total_interactions"] += 1
                        total_time += data.get("response_time", 0)
                        stats["total_prompt_chars"] += data.get("prompt_length", 0)
                        stats["total_response_chars"] += data.get("response_length", 0)
                    except json.JSONDecodeError:
                        continue
        
        if stats["total_interactions"] > 0:
            stats["avg_response_time"] = total_time / stats["total_interactions"]
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """
        Limpia logs antiguos
        
        Args:
            days: Días de antigüedad para eliminar
        """
        import time
        
        cutoff_time = time.time() - (days * 86400)
        deleted = 0
        
        for log_file in self.log_dir.glob('*.log'):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                deleted += 1
        
        for log_file in self.log_dir.glob('*.jsonl'):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                deleted += 1
        
        if deleted > 0:
            self.main_logger.info(f"Cleaned up {deleted} old log files")


# Ejemplo de uso
if __name__ == "__main__":
    logger = BotLogger()
    
    # Test de logging
    logger.log_startup({
        "DISCORD_TOKEN": "token_example_12345",
        "OLLAMA_MODEL": "llama3.2",
        "USE_GPU": False
    })
    
    logger.log_info("Bot iniciado correctamente")
    logger.log_command(123456789, "newchat")
    logger.log_message(123456789, "Hola bot", "¡Hola! ¿Cómo estás?", 1.23)
    logger.log_error(123456789, "Error de prueba")
    
    print("\n📊 Estadísticas de interacciones:")
    stats = logger.get_interaction_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    logger.log_shutdown()
    print("\n✅ Logs creados en:", logger.log_dir)