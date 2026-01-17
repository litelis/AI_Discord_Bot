import json
from pathlib import Path
import pickle

class PersonalityManager:
    """Gestor de personalidades para el bot."""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.personalities_file = self.data_dir / "personalities.pkl"
        self.personalities = self.load_personalities()
        
        # Personalidades predefinidas
        self.default_personalities = {
            "profesional": {
                "nombre": "Profesional",
                "descripcion": "Asistente formal y profesional",
                "genero": "neutro",
                "edad": "indefinida",
                "tono": "formal",
                "system_prompt": "Eres un asistente profesional y formal. Respondes de manera concisa y precisa. Usas un lenguaje técnico cuando es apropiado."
            },
            "amigo": {
                "nombre": "Amigo Cercano",
                "descripcion": "Como hablar con un amigo de confianza",
                "genero": "neutro",
                "edad": "25",
                "tono": "casual",
                "system_prompt": "Eres un amigo cercano hablando de manera casual. Usas un lenguaje relajado, coloquial y natural. Te expresas como en una conversación entre amigos, sin formalidades innecesarias. Puedes usar emojis ocasionalmente."
            },
            "mentor": {
                "nombre": "Mentor Sabio",
                "descripcion": "Consejero experimentado y paciente",
                "genero": "neutro",
                "edad": "50",
                "tono": "sabio",
                "system_prompt": "Eres un mentor experimentado y paciente. Explicas las cosas de manera clara y pedagógica. Ofreces consejos basados en experiencia y sabiduría."
            },
            "entusiasta": {
                "nombre": "Entusiasta",
                "descripcion": "Lleno de energía y positividad",
                "genero": "neutro",
                "edad": "20",
                "tono": "energético",
                "system_prompt": "Eres una persona muy entusiasta y positiva. Te emociona ayudar y aprender cosas nuevas. Usas exclamaciones, emojis y un lenguaje muy expresivo y animado. ¡Todo es increíble y emocionante!"
            }
        }
    
    def load_personalities(self):
        """Carga personalidades guardadas."""
        if self.personalities_file.exists():
            try:
                with open(self.personalities_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def save_personalities(self):
        """Guarda personalidades."""
        with open(self.personalities_file, 'wb') as f:
            pickle.dump(self.personalities, f)
    
    def get_personality(self, user_id):
        """Obtiene la personalidad activa del usuario."""
        if user_id not in self.personalities:
            # Por defecto usar "amigo"
            self.personalities[user_id] = "amigo"
            self.save_personalities()
        
        persona_id = self.personalities[user_id]
        return self.default_personalities.get(persona_id, self.default_personalities["amigo"])
    
    def set_personality(self, user_id, personality_id):
        """Establece la personalidad del usuario."""
        if personality_id in self.default_personalities:
            self.personalities[user_id] = personality_id
            self.save_personalities()
            return True
        return False
    
    def list_personalities(self):
        """Lista todas las personalidades disponibles."""
        return [
            {
                "id": pid,
                "nombre": p["nombre"],
                "descripcion": p["descripcion"],
                "genero": p["genero"],
                "edad": p["edad"],
                "tono": p["tono"]
            }
            for pid, p in self.default_personalities.items()
        ]
    
    def get_system_prompt(self, user_id):
        """Obtiene el prompt del sistema para el usuario."""
        personality = self.get_personality(user_id)
        return personality["system_prompt"]
