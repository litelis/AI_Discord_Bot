import json
import hashlib
from datetime import datetime
from pathlib import Path

class ChatExporter:
    """Exporta e importa chats en múltiples formatos."""
    
    BOT_SIGNATURE = "DISCORD_OLLAMA_BOT_v2.0"
    MAGIC_BYTES = b'\x44\x4F\x42\x32'  # DOB2
    
    def __init__(self):
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def generate_checksum(self, data):
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def export_to_dob(self, chat_history, chat_name, user_id):
        timestamp = datetime.now()
        data = {
            "signature": self.BOT_SIGNATURE,
            "version": "2.0",
            "exported_at": timestamp.isoformat(),
            "chat_name": chat_name,
            "user_id": user_id,
            "messages": chat_history,
            "message_count": len(chat_history)
        }
        data["checksum"] = self.generate_checksum(data)
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        encoded_data = self.MAGIC_BYTES + json_data.encode('utf-8')
        
        filename = f"{chat_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.dob"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(encoded_data)
        return filepath
    
    def export_to_txt(self, chat_history, chat_name, user_id):
        timestamp = datetime.now()
        content = []
        content.append(f"=" * 80)
        content.append(f"Chat: {chat_name}")
        content.append(f"Exportado: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Mensajes: {len(chat_history)}")
        content.append(f"=" * 80)
        content.append("")
        
        for msg in chat_history:
            role = "👤 Usuario" if msg["role"] == "user" else "🤖 Asistente"
            content.append(f"{role}:")
            content.append(msg["content"])
            content.append("-" * 80)
            content.append("")
        
        watermark = f"\n\n{'=' * 80}\n[{self.BOT_SIGNATURE}]\n"
        watermark += f"Checksum: {self.generate_checksum({'messages': chat_history})}\n{'=' * 80}"
        content.append(watermark)
        
        filename = f"{chat_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        return filepath
    
    def import_from_dob(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if not data.startswith(self.MAGIC_BYTES):
                return None, "Archivo no válido (.dob)"
            
            json_data = data[len(self.MAGIC_BYTES):].decode('utf-8')
            chat_data = json.loads(json_data)
            
            if chat_data.get("signature") != self.BOT_SIGNATURE:
                return None, "Firma incorrecta"
            
            stored_checksum = chat_data.pop("checksum")
            if stored_checksum != self.generate_checksum(chat_data):
                return None, "Checksum corrupto"
            
            return {
                "chat_name": chat_data["chat_name"],
                "messages": chat_data["messages"],
                "message_count": chat_data["message_count"]
            }, None
        except Exception as e:
            return None, str(e)

    def import_from_txt(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.BOT_SIGNATURE not in content:
                return None, "No firmado por este bot"
            
            # Simple parser para el TXT
            lines = content.split('\n')
            messages = []
            current_role = None
            current_content = []
            chat_name = "imported_txt"

            for line in lines:
                if line.startswith("Chat:"):
                    chat_name = line.split("Chat:")[1].strip()
                elif line.startswith("👤 Usuario:"):
                    if current_role: messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
                    current_role = "user"
                    current_content = []
                elif line.startswith("🤖 Asistente:"):
                    if current_role: messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})
                    current_role = "assistant"
                    current_content = []
                elif not line.startswith(("=", "-")) and current_role:
                    current_content.append(line)
            
            if current_role: messages.append({"role": current_role, "content": '\n'.join(current_content).strip()})

            return {"chat_name": chat_name, "messages": messages, "message_count": len(messages)}, None
        except Exception as e:
            return None, str(e)