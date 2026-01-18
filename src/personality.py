#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Sistema de Personalidades
Gestión de diferentes personalidades del bot
"""

import json
from pathlib import Path
from typing import Dict


class PersonalityManager:
    """Gestor de personalidades del bot"""
    
    # Definición de personalidades
    PERSONALITIES = {
        "profesional": {
            "name": "🎓 Profesional",
            "description": "Formal, preciso y estructurado",
            "system_prompt": """Eres un asistente profesional y eficiente. Tu comunicación es:
- Formal y respetuosa
- Precisa y concisa
- Estructurada y organizada
- Enfocada en la eficiencia
- Sin emojis excesivos
- Respuestas claras y directas

Mantienes un tono profesional en todo momento, proporcionando información precisa y bien organizada."""
        },
        
        "amigo": {
            "name": "😊 Amigo",
            "description": "Casual, cercano y conversacional",
            "system_prompt": """Eres un amigo cercano y de confianza. Tu comunicación es:
- Casual y relajada
- Cercana y empática
- Conversacional y natural
- Usa emojis apropiadamente 😊
- Expresiones coloquiales
- Tono cálido y acogedor

Hablas como un buen amigo, siendo comprensivo, divertido cuando es apropiado, y siempre disponible para charlar."""
        },
        
        "mentor": {
            "name": "👨‍🏫 Mentor",
            "description": "Educativo, paciente y detallado",
            "system_prompt": """Eres un mentor educativo y paciente. Tu comunicación es:
- Explicativa y detallada
- Paciente y comprensiva
- Fomenta el aprendizaje
- Usa ejemplos claros
- Pregunta para verificar comprensión
- Celebra el progreso

Enseñas de manera efectiva, asegurándote de que se comprende cada concepto antes de avanzar. Fomentas el pensamiento crítico."""
        },
        
        "entusiasta": {
            "name": "🎉 Entusiasta",
            "description": "Energético, positivo y motivador",
            "system_prompt": """Eres un asistente entusiasta y motivador. Tu comunicación es:
- Energética y positiva
- Motivadora e inspiradora
- Celebra cada logro 🎉
- Usa exclamaciones apropiadamente
- Lenguaje optimista
- Fomenta la acción

Transmites energía positiva y motivación en cada interacción, haciendo que todo parezca posible y emocionante."""
        }
    }
    
    DEFAULT_PERSONALITY = "amigo"
    
    def __init__(self, data_file: str = "data/personalities.json"):
        """
        Inicializa el gestor de personalidades
        
        Args:
            data_file: Archivo donde guardar las preferencias de usuarios
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        
        # Cargar preferencias guardadas
        self.user_personalities = self._load_preferences()
    
    def _load_preferences(self) -> Dict[int, str]:
        """
        Carga las preferencias de personalidad de los usuarios
        
        Returns:
            Diccionario con user_id -> personality
        """
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convertir keys a int
                    return {int(k): v for k, v in data.items()}
            except Exception:
                return {}
        return {}
    
    def _save_preferences(self):
        """Guarda las preferencias de personalidad"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                # Convertir keys a str para JSON
                data = {str(k): v for k, v in self.user_personalities.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando preferencias: {e}")
    
    def get_personality(self, user_id: int) -> str:
        """
        Obtiene la personalidad configurada para un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Nombre de la personalidad
        """
        return self.user_personalities.get(user_id, self.DEFAULT_PERSONALITY)
    
    def set_personality(self, user_id: int, personality: str) -> bool:
        """
        Establece la personalidad para un usuario
        
        Args:
            user_id: ID del usuario
            personality: Nombre de la personalidad
            
        Returns:
            True si se estableció correctamente, False si la personalidad no existe
        """
        if personality not in self.PERSONALITIES:
            return False
        
        self.user_personalities[user_id] = personality
        self._save_preferences()
        return True
    
    def get_system_prompt(self, personality: str) -> str:
        """
        Obtiene el system prompt de una personalidad
        
        Args:
            personality: Nombre de la personalidad
            
        Returns:
            System prompt de la personalidad
        """
        if personality not in self.PERSONALITIES:
            personality = self.DEFAULT_PERSONALITY
        
        return self.PERSONALITIES[personality]["system_prompt"]
    
    def get_personality_info(self, personality: str) -> dict:
        """
        Obtiene información completa de una personalidad
        
        Args:
            personality: Nombre de la personalidad
            
        Returns:
            Diccionario con información de la personalidad
        """
        if personality not in self.PERSONALITIES:
            return None
        
        return self.PERSONALITIES[personality]
    
    def list_personalities(self) -> dict:
        """
        Lista todas las personalidades disponibles
        
        Returns:
            Diccionario con todas las personalidades
        """
        return self.PERSONALITIES.copy()
    
    def get_user_stats(self) -> dict:
        """
        Obtiene estadísticas de uso de personalidades
        
        Returns:
            Diccionario con conteo por personalidad
        """
        stats = {p: 0 for p in self.PERSONALITIES.keys()}
        
        for personality in self.user_personalities.values():
            if personality in stats:
                stats[personality] += 1
        
        stats["total_users"] = len(self.user_personalities)
        stats["default_users"] = len([
            p for p in self.user_personalities.values() 
            if p == self.DEFAULT_PERSONALITY
        ])
        
        return stats
    
    def reset_user(self, user_id: int):
        """
        Resetea la personalidad de un usuario al default
        
        Args:
            user_id: ID del usuario
        """
        if user_id in self.user_personalities:
            del self.user_personalities[user_id]
            self._save_preferences()
    
    def get_personality_description(self, personality: str) -> str:
        """
        Obtiene una descripción amigable de la personalidad
        
        Args:
            personality: Nombre de la personalidad
            
        Returns:
            Descripción de la personalidad
        """
        info = self.get_personality_info(personality)
        if info:
            return f"{info['name']}: {info['description']}"
        return "Personalidad desconocida"


# Ejemplo de uso
if __name__ == "__main__":
    manager = PersonalityManager()
    
    print("🎭 Sistema de Personalidades")
    print("="*60)
    
    # Listar personalidades disponibles
    print("\n📋 Personalidades disponibles:")
    for key, info in manager.list_personalities().items():
        print(f"\n{info['name']}")
        print(f"   Clave: {key}")
        print(f"   Descripción: {info['description']}")
    
    # Test de usuario
    test_user_id = 123456789
    
    # Obtener personalidad por defecto
    print(f"\n👤 Usuario {test_user_id}:")
    current = manager.get_personality(test_user_id)
    print(f"   Personalidad actual: {current}")
    
    # Cambiar personalidad
    manager.set_personality(test_user_id, "mentor")
    current = manager.get_personality(test_user_id)
    print(f"   Nueva personalidad: {current}")
    
    # Obtener system prompt
    prompt = manager.get_system_prompt(current)
    print(f"\n📝 System prompt ({current}):")
    print(prompt[:200] + "...")
    
    # Estadísticas
    print("\n📊 Estadísticas:")
    stats = manager.get_user_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Test completado")