#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Export/Import de Chats
Sistema de exportación e importación con verificación de integridad
"""

import json
import hashlib
import struct
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class ChatExporter:
    """Gestor de exportación e importación de chats"""
    
    # Magic bytes para formato DOB
    MAGIC_BYTES = b'DOB1'
    WATERMARK = "Discord Ollama Bot - Exported Chat"
    
    def __init__(self, export_dir: str = "exports"):
        """
        Inicializa el exportador
        
        Args:
            export_dir: Directorio donde guardar las exportaciones
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def _calculate_checksum(self, data: bytes) -> str:
        """
        Calcula el checksum MD5 de los datos
        
        Args:
            data: Datos a calcular checksum
            
        Returns:
            Checksum en hexadecimal
        """
        return hashlib.md5(data).hexdigest()
    
    def _generate_filename(self, user_id: int, extension: str) -> Path:
        """
        Genera un nombre de archivo único
        
        Args:
            user_id: ID del usuario
            extension: Extensión del archivo (.dob o .txt)
            
        Returns:
            Path del archivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{user_id}_{timestamp}{extension}"
        return self.export_dir / filename
    
    def export_dob(self, user_id: int, conversation: List[Dict]) -> Path:
        """
        Exporta el chat en formato DOB (binario propietario)
        
        Formato DOB:
        - Magic bytes (4 bytes): 'DOB1'
        - Timestamp (8 bytes): Unix timestamp
        - User ID (8 bytes): ID del usuario
        - Watermark length (4 bytes): Longitud de marca de agua
        - Watermark (variable): Marca de agua
        - Data length (4 bytes): Longitud de datos JSON
        - Data (variable): Conversación en JSON
        - Checksum (32 bytes): MD5 de todo lo anterior
        
        Args:
            user_id: ID del usuario
            conversation: Lista de mensajes
            
        Returns:
            Path del archivo exportado
        """
        filepath = self._generate_filename(user_id, ".dob")
        
        # Preparar datos
        timestamp = int(datetime.now().timestamp())
        watermark_bytes = self.WATERMARK.encode('utf-8')
        data_json = json.dumps(conversation, ensure_ascii=False, indent=2).encode('utf-8')
        
        # Construir archivo
        with open(filepath, 'wb') as f:
            # Header
            f.write(self.MAGIC_BYTES)  # Magic bytes
            f.write(struct.pack('Q', timestamp))  # Timestamp (unsigned long long)
            f.write(struct.pack('Q', user_id))  # User ID (unsigned long long)
            
            # Watermark
            f.write(struct.pack('I', len(watermark_bytes)))  # Watermark length (unsigned int)
            f.write(watermark_bytes)
            
            # Data
            f.write(struct.pack('I', len(data_json)))  # Data length (unsigned int)
            f.write(data_json)
            
            # Calcular checksum de todo menos el checksum mismo
            f.seek(0)
            file_data = f.read()
            checksum = self._calculate_checksum(file_data).encode('ascii')
            
            # Escribir checksum
            f.write(checksum)
        
        return filepath
    
    def export_txt(self, user_id: int, conversation: List[Dict]) -> Path:
        """
        Exporta el chat en formato TXT legible
        
        Args:
            user_id: ID del usuario
            conversation: Lista de mensajes
            
        Returns:
            Path del archivo exportado
        """
        filepath = self._generate_filename(user_id, ".txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("="*70 + "\n")
            f.write("🤖 Bot de Discord con Ollama - Historial Exportado\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Usuario ID: {user_id}\n")
            f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de mensajes: {len(conversation)}\n")
            f.write("\n" + "="*70 + "\n\n")
            
            # Mensajes
            for i, msg in enumerate(conversation, 1):
                timestamp = msg.get('timestamp', 'N/A')
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                # Formato amigable del rol
                role_display = {
                    'user': '👤 Usuario',
                    'assistant': '🤖 Asistente'
                }.get(role, role)
                
                f.write(f"[{i}] {role_display}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write("-"*70 + "\n")
                f.write(f"{content}\n")
                f.write("\n" + "="*70 + "\n\n")
            
            # Footer con checksum
            file_content = f.getvalue() if hasattr(f, 'getvalue') else ""
            
            # Leer todo el archivo para calcular checksum
            with open(filepath, 'r', encoding='utf-8') as rf:
                file_content = rf.read()
            
            checksum = self._calculate_checksum(file_content.encode('utf-8'))
            
            f.write("\n" + "-"*70 + "\n")
            f.write(f"Checksum MD5: {checksum}\n")
            f.write("Este archivo ha sido exportado desde Discord Ollama Bot\n")
            f.write("-"*70 + "\n")
        
        return filepath
    
    def import_dob(self, filepath: str) -> Optional[List[Dict]]:
        """
        Importa un chat en formato DOB
        
        Args:
            filepath: Ruta del archivo a importar
            
        Returns:
            Lista de mensajes o None si hay error
        """
        try:
            with open(filepath, 'rb') as f:
                # Verificar magic bytes
                magic = f.read(4)
                if magic != self.MAGIC_BYTES:
                    print("❌ Archivo inválido: magic bytes incorrectos")
                    return None
                
                # Leer timestamp y user_id
                timestamp = struct.unpack('Q', f.read(8))[0]
                user_id = struct.unpack('Q', f.read(8))[0]
                
                # Leer watermark
                watermark_len = struct.unpack('I', f.read(4))[0]
                watermark = f.read(watermark_len).decode('utf-8')
                
                if watermark != self.WATERMARK:
                    print("⚠️ Advertencia: Watermark no coincide")
                
                # Leer datos
                data_len = struct.unpack('I', f.read(4))[0]
                data_json = f.read(data_len)
                
                # Leer checksum
                stored_checksum = f.read(32).decode('ascii')
                
                # Verificar checksum
                f.seek(0)
                file_data = f.read(f.tell() - 32)  # Todo excepto el checksum
                calculated_checksum = self._calculate_checksum(file_data)
                
                if stored_checksum != calculated_checksum:
                    print("❌ Error: Checksum no coincide (archivo corrupto)")
                    return None
                
                # Parsear JSON
                conversation = json.loads(data_json.decode('utf-8'))
                
                print(f"✅ Archivo DOB importado correctamente")
                print(f"   User ID: {user_id}")
                print(f"   Timestamp: {datetime.fromtimestamp(timestamp)}")
                print(f"   Mensajes: {len(conversation)}")
                
                return conversation
                
        except Exception as e:
            print(f"❌ Error importando DOB: {e}")
            return None
    
    def import_txt(self, filepath: str) -> Optional[List[Dict]]:
        """
        Importa un chat en formato TXT
        
        Args:
            filepath: Ruta del archivo a importar
            
        Returns:
            Lista de mensajes o None si hay error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar checksum si existe
            if "Checksum MD5:" in content:
                parts = content.split("Checksum MD5:")
                main_content = parts[0]
                checksum_line = parts[1].split('\n')[0].strip()
                
                calculated = self._calculate_checksum(main_content.encode('utf-8'))
                
                if calculated != checksum_line:
                    print("⚠️ Advertencia: Checksum no coincide")
            
            # Parsear mensajes (formato simple)
            conversation = []
            lines = content.split('\n')
            
            current_msg = None
            in_content = False
            
            for line in lines:
                if line.startswith('[') and (']' in line):
                    # Nuevo mensaje
                    if current_msg and current_msg.get('content'):
                        conversation.append(current_msg)
                    
                    current_msg = {'content': ''}
                    
                    if '👤 Usuario' in line:
                        current_msg['role'] = 'user'
                    elif '🤖 Asistente' in line:
                        current_msg['role'] = 'assistant'
                    
                    in_content = False
                    
                elif line.startswith('Timestamp:') and current_msg:
                    timestamp = line.replace('Timestamp:', '').strip()
                    current_msg['timestamp'] = timestamp
                    
                elif line.startswith('-'*70) and current_msg:
                    in_content = True
                    
                elif in_content and not line.startswith('='):
                    if line.strip():
                        current_msg['content'] += line + '\n'
            
            # Añadir último mensaje
            if current_msg and current_msg.get('content'):
                conversation.append(current_msg)
            
            # Limpiar contenidos
            for msg in conversation:
                msg['content'] = msg['content'].strip()
            
            if conversation:
                print(f"✅ Archivo TXT importado correctamente")
                print(f"   Mensajes: {len(conversation)}")
                return conversation
            else:
                print("⚠️ No se encontraron mensajes en el archivo")
                return None
                
        except Exception as e:
            print(f"❌ Error importando TXT: {e}")
            return None
    
    def import_chat(self, filepath: str) -> Optional[List[Dict]]:
        """
        Importa un chat detectando automáticamente el formato
        
        Args:
            filepath: Ruta del archivo a importar
            
        Returns:
            Lista de mensajes o None si hay error
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            print("❌ Archivo no existe")
            return None
        
        extension = filepath.suffix.lower()
        
        if extension == '.dob':
            return self.import_dob(str(filepath))
        elif extension == '.txt':
            return self.import_txt(str(filepath))
        else:
            print(f"❌ Formato no soportado: {extension}")
            return None
    
    def list_exports(self) -> List[Path]:
        """
        Lista todos los archivos exportados
        
        Returns:
            Lista de rutas de archivos
        """
        exports = []
        exports.extend(self.export_dir.glob('*.dob'))
        exports.extend(self.export_dir.glob('*.txt'))
        return sorted(exports, key=lambda x: x.stat().st_mtime, reverse=True)


# Ejemplo de uso
if __name__ == "__main__":
    exporter = ChatExporter()
    
    # Conversación de ejemplo
    test_conversation = [
        {
            "role": "user",
            "content": "Hola, ¿cómo estás?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "content": "Necesito ayuda con Python",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": "¡Por supuesto! Estaré encantado de ayudarte con Python. ¿Qué necesitas específicamente?",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    test_user_id = 123456789
    
    print("🧪 Test de Export/Import")
    print("="*60)
    
    # Test export DOB
    print("\n📦 Exportando a formato DOB...")
    dob_file = exporter.export_dob(test_user_id, test_conversation)
    print(f"✅ Exportado: {dob_file}")
    print(f"   Tamaño: {dob_file.stat().st_size} bytes")
    
    # Test export TXT
    print("\n📄 Exportando a formato TXT...")
    txt_file = exporter.export_txt(test_user_id, test_conversation)
    print(f"✅ Exportado: {txt_file}")
    print(f"   Tamaño: {txt_file.stat().st_size} bytes")
    
    # Test import DOB
    print("\n📥 Importando archivo DOB...")
    imported_dob = exporter.import_dob(str(dob_file))
    if imported_dob:
        print(f"   Mensajes importados: {len(imported_dob)}")
    
    # Test import TXT
    print("\n📥 Importando archivo TXT...")
    imported_txt = exporter.import_txt(str(txt_file))
    if imported_txt:
        print(f"   Mensajes importados: {len(imported_txt)}")
    
    # Listar exports
    print("\n📋 Archivos exportados:")
    for export in exporter.list_exports()[:5]:
        print(f"   {export.name}")
    
    print("\n✅ Test completado")