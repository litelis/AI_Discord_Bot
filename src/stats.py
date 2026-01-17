import pickle
from pathlib import Path
from datetime import datetime
import json

class StatsManager:
    """Gestor de estadísticas del bot."""
    
    def __init__(self):
        self.data_dir = Path("../data")
        self.stats_file = self.data_dir / "stats.pkl"
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Carga estadísticas guardadas."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return self.create_empty_stats()
        return self.create_empty_stats()
    
    def create_empty_stats(self):
        """Crea estructura de estadísticas vacía."""
        return {
            "total_messages": 0,
            "total_tokens": 0,
            "response_times": [],
            "tokens_per_second": [],
            "messages_by_user": {},
            "commands_used": {},
            "chats_saved": 0,
            "chats_loaded": 0,
            "average_message_length": 0,
            "peak_usage_hour": None,
            "started_at": datetime.now().isoformat()
        }
    
    def save_stats(self):
        """Guarda estadísticas."""
        with open(self.stats_file, 'wb') as f:
            pickle.dump(self.stats, f)
    
    def record_message(self, user_id, message_length, response_time, tokens=None, tokens_per_sec=None):
        """Registra un mensaje."""
        self.stats["total_messages"] += 1
        self.stats["response_times"].append(response_time)
        
        if tokens:
            self.stats["total_tokens"] += tokens
        
        if tokens_per_sec:
            self.stats["tokens_per_second"].append(tokens_per_sec)
        
        # Por usuario
        if user_id not in self.stats["messages_by_user"]:
            self.stats["messages_by_user"][user_id] = {
                "count": 0,
                "total_length": 0,
                "avg_response_time": 0
            }
        
        user_stats = self.stats["messages_by_user"][user_id]
        user_stats["count"] += 1
        user_stats["total_length"] += message_length
        
        # Calcular promedio de tiempo de respuesta
        if user_stats["avg_response_time"] == 0:
            user_stats["avg_response_time"] = response_time
        else:
            user_stats["avg_response_time"] = (
                (user_stats["avg_response_time"] * (user_stats["count"] - 1) + response_time) 
                / user_stats["count"]
            )
        
        self.save_stats()
    
    def record_command(self, command_name):
        """Registra uso de comando."""
        if command_name not in self.stats["commands_used"]:
            self.stats["commands_used"][command_name] = 0
        self.stats["commands_used"][command_name] += 1
        self.save_stats()
    
    def record_chat_saved(self):
        """Registra chat guardado."""
        self.stats["chats_saved"] += 1
        self.save_stats()
    
    def record_chat_loaded(self):
        """Registra chat cargado."""
        self.stats["chats_loaded"] += 1
        self.save_stats()
    
    def get_average_response_time(self):
        """Obtiene tiempo promedio de respuesta."""
        if not self.stats["response_times"]:
            return 0
        return sum(self.stats["response_times"]) / len(self.stats["response_times"])
    
    def get_average_tokens_per_second(self):
        """Obtiene promedio de tokens por segundo."""
        if not self.stats["tokens_per_second"]:
            return 0
        return sum(self.stats["tokens_per_second"]) / len(self.stats["tokens_per_second"])
    
    def get_stats_summary(self):
        """Obtiene resumen de estadísticas."""
        return {
            "total_messages": self.stats["total_messages"],
            "total_tokens": self.stats["total_tokens"],
            "avg_response_time": self.get_average_response_time(),
            "avg_tokens_per_second": self.get_average_tokens_per_second(),
            "total_users": len(self.stats["messages_by_user"]),
            "chats_saved": self.stats["chats_saved"],
            "chats_loaded": self.stats["chats_loaded"],
            "most_used_command": max(
                self.stats["commands_used"].items(), 
                key=lambda x: x[1]
            )[0] if self.stats["commands_used"] else None,
            "started_at": self.stats["started_at"]
        }
    
    def get_detailed_stats(self):
        """Obtiene estadísticas detalladas para web UI."""
        return self.stats
