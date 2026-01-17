import json
import hashlib
from datetime import datetime
from pathlib import Path
import base64

class ChatExporter:
    """Exporta e importa chats en múltiples formatos."""
    
    # Firma única del bot (marca de agua)
    BOT_SIGNATURE = "DISCORD_OLLAMA_BOT_v2.0"
    MAGIC_BYTES = b'\x44\x4F\x42\x32'  # DOB2 (Discord Ollama Bot v2)
    
    def __init__(self):
        self.exports_dir = Path("../exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def generate_checksum(self, data):
        """Genera checksum para verificar integridad."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def export_to_dob(self, chat_history, chat_name, user_id):
        """Exporta a formato propietario .dob (Discord Ollama Bot)."""
        timestamp = datetime.now()
        
        # Estructura del archivo
        data = {
            "signature": self.BOT_SIGNATURE,
            "version": "2.0",
            "exported_at": timestamp.isoformat(),
            "chat_name": chat_name,
            "user_id": user_id,
            "messages": chat_history,
            "message_count": len(chat_history)
        }
        
        # Añadir checksum
        data["checksum"] = self.generate_checksum(data)
        
        # Convertir a JSON y añadir magic bytes
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        encoded_data = self.MAGIC_BYTES + json_data.encode('utf-8')
        
        # Guardar archivo
        filename = f"{chat_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.dob"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(encoded_data)
        
        return filepath
    
    def export_to_txt(self, chat_history, chat_name, user_id):
        """Exporta a formato TXT con marca de agua."""
        timestamp = datetime.now()
        
        # Crear contenido
        content = []
        content.append(f"=" * 80)
        content.append(f"Chat: {chat_name}")
        content.append(f"Exportado: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Mensajes: {len(chat_history)}")
        content.append(f"=" * 80)
        content.append("")
        
        # Añadir mensajes
        for msg in chat_history:
            role = "👤 Usuario" if msg["role"] == "user" else "🤖 Asistente"
            content.append(f"{role}:")
            content.append(msg["content"])
            content.append("-" * 80)
            content.append("")
        
        # Marca de agua al final
        watermark = f"\n\n{'=' * 80}\n"
        watermark += f"[{self.BOT_SIGNATURE}]\n"
        watermark += f"Checksum: {self.generate_checksum({'messages': chat_history})}\n"
        watermark += f"{'=' * 80}"
        content.append(watermark)
        
        # Guardar
        filename = f"{chat_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        return filepath
    
    def export_to_pdf(self, chat_history, chat_name, user_id):
        """Exporta a formato PDF con marca de agua."""
        # Primero crear TXT y luego indicar que se puede convertir
        txt_path = self.export_to_txt(chat_history, chat_name, user_id)
        
        # Nota: Para PDF real necesitaríamos librerías como reportlab
        # Por ahora retornamos el TXT y sugerimos conversión
        return txt_path, "txt"  # Indica que es TXT temporalmente
    
    def import_from_dob(self, filepath):
        """Importa desde formato .dob."""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Verificar magic bytes
            if not data.startswith(self.MAGIC_BYTES):
                return None, "Archivo no válido: no es un archivo .dob genuino"
            
            # Decodificar JSON
            json_data = data[len(self.MAGIC_BYTES):].decode('utf-8')
            chat_data = json.loads(json_data)
            
            # Verificar firma
            if chat_data.get("signature") != self.BOT_SIGNATURE:
                return None, "Archivo no válido: firma incorrecta"
            
            # Verificar checksum
            stored_checksum = chat_data.pop("checksum")
            calculated_checksum = self.generate_checksum(chat_data)
            
            if stored_checksum != calculated_checksum:
                return None, "Archivo corrupto: checksum no coincide"
            
            # Retornar datos
            return {
                "chat_name": chat_data["chat_name"],
                "messages": chat_data["messages"],
                "exported_at": chat_data["exported_at"],
                "message_count": chat_data["message_count"]
            }, None
            
        except Exception as e:
            return None, f"Error al importar: {str(e)}"
    
    def import_from_txt(self, filepath):
        """Importa desde formato TXT con verificación."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar marca de agua
            if self.BOT_SIGNATURE not in content:
                return None, "Archivo no válido: no fue generado por este bot"
            
            # Extraer checksum
            lines = content.split('\n')
            checksum_line = [l for l in lines if l.startswith("Checksum:")]
            if not checksum_line:
                return None, "Archivo no válido: falta checksum"
            
            stored_checksum = checksum_line[0].split("Checksum:")[1].strip()
            
            # Parsear mensajes
            messages = []
            current_role = None
            current_content = []
            
            for line in lines:
                if line.startswith("👤 Usuario:"):
                    if current_role and current_content:
                        messages.append({
                            "role": current_role,
                            "content": '\n'.join(current_content).strip()
                        })
                    current_role = "user"
                    current_content = []
                elif line.startswith("🤖 Asistente:"):
                    if current_role and current_content:
                        messages.append({
                            "role": current_role,
                            "content": '\n'.join(current_content).strip()
                        })
                    current_role = "assistant"
                    current_content = []
                elif line.startswith("-" * 80) or line.startswith("=" * 80):
                    continue
                elif line.strip() and current_role:
                    current_content.append(line)
            
            # Añadir último mensaje
            if current_role and current_content:
                messages.append({
                    "role": current_role,
                    "content": '\n'.join(current_content).strip()
                })
            
            # Verificar checksum
            calculated_checksum = self.generate_checksum({"messages": messages})
            if stored_checksum != calculated_checksum:
                return None, "Archivo modificado: checksum no coincide"
            
            # Extraer nombre del chat
            chat_name_line = [l for l in lines if l.startswith("Chat:")]
            chat_name = chat_name_line[0].split("Chat:")[1].strip() if chat_name_line else "imported_chat"
            
            return {
                "chat_name": chat_name,
                "messages": messages,
                "message_count": len(messages)
            }, None
            
        except Exception as e:
            return None, f"Error al importar: {str(e)}"
