import logging
from datetime import datetime
from pathlib import Path
import json

class BotLogger:
    """Sistema de logging mejorado para el bot."""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo con fecha y hora exacta
        now = datetime.now()
        log_filename = f"bot_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        self.log_file = self.logs_dir / log_filename
        
        # Configurar logging
        self.setup_logger()
    
    def setup_logger(self):
        """Configura el sistema de logging."""
        # Formato detallado
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Configurar logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logging.info(f"Sistema de logging iniciado: {self.log_file}")
    
    @staticmethod
    def log_command(user_id, command, params=None):
        """Registra uso de comando."""
        logger = logging.getLogger('commands')
        msg = f"User {user_id} ejecutó /{command}"
        if params:
            msg += f" con parámetros: {params}"
        logger.info(msg)
    
    @staticmethod
    def log_message(user_id, message_length, response_time, tokens_per_sec=None):
        """Registra mensaje y respuesta."""
        logger = logging.getLogger('messages')
        msg = f"User {user_id} | Mensaje: {message_length} chars | Tiempo: {response_time:.2f}s"
        if tokens_per_sec:
            msg += f" | Tokens/s: {tokens_per_sec:.1f}"
        logger.info(msg)
    
    @staticmethod
    def log_error(error_type, error_msg, user_id=None):
        """Registra errores."""
        logger = logging.getLogger('errors')
        msg = f"{error_type}: {error_msg}"
        if user_id:
            msg = f"User {user_id} | {msg}"
        logger.error(msg)
    
    @staticmethod
    def log_stats(stat_type, data):
        """Registra estadísticas."""
        logger = logging.getLogger('stats')
        logger.info(f"{stat_type}: {json.dumps(data)}")
