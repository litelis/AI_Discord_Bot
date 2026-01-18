#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Sistema de Estadísticas
Tracking y análisis de interacciones del bot
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class StatsManager:
    """Gestor de estadísticas del bot"""
    
    def __init__(self, data_file: str = "data/stats.json"):
        """
        Inicializa el gestor de estadísticas
        
        Args:
            data_file: Archivo donde guardar las estadísticas
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        
        # Cargar estadísticas existentes
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """
        Carga las estadísticas desde el archivo
        
        Returns:
            Diccionario con las estadísticas
        """
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._create_default_stats()
        return self._create_default_stats()
    
    def _create_default_stats(self) -> Dict:
        """
        Crea estructura de estadísticas por defecto
        
        Returns:
            Diccionario con estructura vacía
        """
        return {
            "global": {
                "total_messages": 0,
                "total_tokens": 0,
                "total_response_time": 0,
                "start_date": datetime.now().isoformat(),
                "last_interaction": None
            },
            "users": {},
            "hourly": {str(i): 0 for i in range(24)},
            "commands": {}
        }
    
    def _save_stats(self):
        """Guarda las estadísticas en el archivo"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando estadísticas: {e}")
    
    def add_interaction(self, user_id: int, tokens_used: int, response_time: float):
        """
        Registra una interacción
        
        Args:
            user_id: ID del usuario
            tokens_used: Tokens utilizados en la respuesta
            response_time: Tiempo de respuesta en segundos
        """
        user_id_str = str(user_id)
        now = datetime.now()
        
        # Estadísticas globales
        self.stats["global"]["total_messages"] += 1
        self.stats["global"]["total_tokens"] += tokens_used
        self.stats["global"]["total_response_time"] += response_time
        self.stats["global"]["last_interaction"] = now.isoformat()
        
        # Estadísticas por usuario
        if user_id_str not in self.stats["users"]:
            self.stats["users"][user_id_str] = {
                "total_messages": 0,
                "total_tokens": 0,
                "total_response_time": 0,
                "first_interaction": now.isoformat(),
                "last_interaction": now.isoformat(),
                "interactions": []
            }
        
        user_stats = self.stats["users"][user_id_str]
        user_stats["total_messages"] += 1
        user_stats["total_tokens"] += tokens_used
        user_stats["total_response_time"] += response_time
        user_stats["last_interaction"] = now.isoformat()
        
        # Guardar interacción detallada (últimas 100)
        user_stats["interactions"].append({
            "timestamp": now.isoformat(),
            "tokens": tokens_used,
            "response_time": response_time
        })
        
        # Limitar a últimas 100 interacciones
        if len(user_stats["interactions"]) > 100:
            user_stats["interactions"] = user_stats["interactions"][-100:]
        
        # Estadísticas por hora
        hour = str(now.hour)
        self.stats["hourly"][hour] = self.stats["hourly"].get(hour, 0) + 1
        
        # Guardar cambios
        self._save_stats()
    
    def add_command(self, command: str):
        """
        Registra el uso de un comando
        
        Args:
            command: Nombre del comando ejecutado
        """
        if command not in self.stats["commands"]:
            self.stats["commands"][command] = 0
        
        self.stats["commands"][command] += 1
        self._save_stats()
    
    def get_global_stats(self) -> Dict:
        """
        Obtiene estadísticas globales
        
        Returns:
            Diccionario con estadísticas globales
        """
        global_stats = self.stats["global"].copy()
        
        # Calcular promedios
        total_messages = global_stats["total_messages"]
        if total_messages > 0:
            global_stats["avg_tokens"] = global_stats["total_tokens"] / total_messages
            global_stats["avg_response_time"] = global_stats["total_response_time"] / total_messages
        else:
            global_stats["avg_tokens"] = 0
            global_stats["avg_response_time"] = 0
        
        # Añadir cantidad de usuarios únicos
        global_stats["unique_users"] = len(self.stats["users"])
        
        # Calcular uptime
        if global_stats["start_date"]:
            start = datetime.fromisoformat(global_stats["start_date"])
            uptime = datetime.now() - start
            global_stats["uptime_days"] = uptime.days
            global_stats["uptime_hours"] = uptime.total_seconds() / 3600
        
        return global_stats
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """
        Obtiene estadísticas de un usuario específico
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con estadísticas del usuario o None
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.stats["users"]:
            return None
        
        user_stats = self.stats["users"][user_id_str].copy()
        
        # Calcular promedios
        total_messages = user_stats["total_messages"]
        if total_messages > 0:
            user_stats["avg_tokens"] = user_stats["total_tokens"] / total_messages
            user_stats["avg_response_time"] = user_stats["total_response_time"] / total_messages
        else:
            user_stats["avg_tokens"] = 0
            user_stats["avg_response_time"] = 0
        
        # Calcular actividad reciente (últimos 7 días)
        if user_stats["interactions"]:
            week_ago = datetime.now() - timedelta(days=7)
            recent = [
                i for i in user_stats["interactions"]
                if datetime.fromisoformat(i["timestamp"]) > week_ago
            ]
            user_stats["recent_activity"] = len(recent)
        else:
            user_stats["recent_activity"] = 0
        
        return user_stats
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene los usuarios más activos
        
        Args:
            limit: Cantidad de usuarios a retornar
            
        Returns:
            Lista de usuarios ordenados por actividad
        """
        users = []
        
        for user_id, stats in self.stats["users"].items():
            users.append({
                "user_id": int(user_id),
                "total_messages": stats["total_messages"],
                "total_tokens": stats["total_tokens"],
                "avg_response_time": (
                    stats["total_response_time"] / stats["total_messages"]
                    if stats["total_messages"] > 0 else 0
                )
            })
        
        # Ordenar por mensajes totales
        users.sort(key=lambda x: x["total_messages"], reverse=True)
        
        return users[:limit]
    
    def get_hourly_distribution(self) -> Dict[int, int]:
        """
        Obtiene la distribución de actividad por hora
        
        Returns:
            Diccionario con hora -> cantidad de mensajes
        """
        return {int(k): v for k, v in self.stats["hourly"].items()}
    
    def get_command_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de uso de comandos
        
        Returns:
            Diccionario con comando -> cantidad de usos
        """
        return self.stats["commands"].copy()
    
    def get_top_commands(self, limit: int = 10) -> List[tuple]:
        """
        Obtiene los comandos más usados
        
        Args:
            limit: Cantidad de comandos a retornar
            
        Returns:
            Lista de tuplas (comando, usos) ordenada
        """
        commands = sorted(
            self.stats["commands"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return commands[:limit]
    
    def get_user_activity_timeline(self, user_id: int, days: int = 30) -> Dict:
        """
        Obtiene timeline de actividad de un usuario
        
        Args:
            user_id: ID del usuario
            days: Días hacia atrás a analizar
            
        Returns:
            Diccionario con fecha -> cantidad de interacciones
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.stats["users"]:
            return {}
        
        interactions = self.stats["users"][user_id_str]["interactions"]
        cutoff = datetime.now() - timedelta(days=days)
        
        timeline = defaultdict(int)
        
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction["timestamp"])
            if timestamp > cutoff:
                date_key = timestamp.strftime("%Y-%m-%d")
                timeline[date_key] += 1
        
        return dict(timeline)
    
    def reset_user_stats(self, user_id: int):
        """
        Resetea las estadísticas de un usuario
        
        Args:
            user_id: ID del usuario
        """
        user_id_str = str(user_id)
        if user_id_str in self.stats["users"]:
            del self.stats["users"][user_id_str]
            self._save_stats()
    
    def export_stats(self, filepath: str = None) -> str:
        """
        Exporta las estadísticas a un archivo JSON
        
        Args:
            filepath: Ruta del archivo (opcional)
            
        Returns:
            Ruta del archivo exportado
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"exports/stats_export_{timestamp}.json"
        
        Path(filepath).parent.mkdir(exist_ok=True)
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "bot_stats": self.stats
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_summary_report(self) -> str:
        """
        Genera un reporte resumen en texto
        
        Returns:
            String con el reporte formateado
        """
        global_stats = self.get_global_stats()
        
        report = []
        report.append("="*60)
        report.append("📊 REPORTE DE ESTADÍSTICAS DEL BOT")
        report.append("="*60)
        report.append("")
        
        # Estadísticas globales
        report.append("📈 ESTADÍSTICAS GLOBALES")
        report.append(f"   Total de mensajes: {global_stats['total_messages']:,}")
        report.append(f"   Total de tokens: {global_stats['total_tokens']:,}")
        report.append(f"   Usuarios únicos: {global_stats['unique_users']}")
        report.append(f"   Tiempo promedio: {global_stats['avg_response_time']:.2f}s")
        
        if global_stats.get('uptime_days'):
            report.append(f"   Uptime: {global_stats['uptime_days']} días")
        
        report.append("")
        
        # Top usuarios
        report.append("👥 TOP 5 USUARIOS MÁS ACTIVOS")
        top_users = self.get_top_users(5)
        for i, user in enumerate(top_users, 1):
            report.append(f"   {i}. Usuario {user['user_id']}")
            report.append(f"      Mensajes: {user['total_messages']}")
            report.append(f"      Tokens: {user['total_tokens']:,}")
        
        report.append("")
        
        # Comandos más usados
        report.append("🎮 COMANDOS MÁS USADOS")
        top_commands = self.get_top_commands(5)
        for i, (command, uses) in enumerate(top_commands, 1):
            report.append(f"   {i}. /{command}: {uses} usos")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)


# Ejemplo de uso
if __name__ == "__main__":
    stats = StatsManager()
    
    print("📊 Sistema de Estadísticas")
    print("="*60)
    
    # Simular algunas interacciones
    print("\n🧪 Simulando interacciones...")
    test_users = [111, 222, 333]
    
    for _ in range(50):
        import random
        user_id = random.choice(test_users)
        tokens = random.randint(50, 500)
        response_time = random.uniform(0.5, 3.0)
        
        stats.add_interaction(user_id, tokens, response_time)
    
    # Simular comandos
    commands = ["newchat", "personality", "stats", "export"]
    for _ in range(20):
        stats.add_command(random.choice(commands))
    
    print("✅ Interacciones simuladas")
    
    # Mostrar estadísticas globales
    print("\n📈 Estadísticas Globales:")
    global_stats = stats.get_global_stats()
    for key, value in global_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Mostrar top usuarios
    print("\n👥 Top Usuarios:")
    for user in stats.get_top_users(3):
        print(f"   Usuario {user['user_id']}: {user['total_messages']} mensajes")
    
    # Distribución por hora
    print("\n🕐 Distribución Horaria:")
    hourly = stats.get_hourly_distribution()
    current_hour = datetime.now().hour
    for hour in range(current_hour - 5, current_hour + 1):
        h = hour % 24
        print(f"   {h:02d}:00 - {hourly.get(h, 0)} mensajes")
    
    # Comandos más usados
    print("\n🎮 Comandos más usados:")
    for cmd, uses in stats.get_top_commands(5):
        print(f"   /{cmd}: {uses} usos")
    
    # Generar reporte
    print("\n" + stats.generate_summary_report())
    
    # Exportar estadísticas
    export_path = stats.export_stats()
    print(f"\n💾 Estadísticas exportadas a: {export_path}")
    
    print("\n✅ Test completado")