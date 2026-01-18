#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Bot de Discord con Ollama - Servidor Web
Servidor Flask con API REST y dashboard
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
import sys

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from stats import StatsManager
from personality import PersonalityManager
from logger import BotLogger

# Inicializar Flask
app = Flask(
    __name__,
    template_folder='../web/templates',
    static_folder='../web/static'
)
CORS(app)

# Inicializar managers
stats_manager = StatsManager()
personality_manager = PersonalityManager()
logger = BotLogger()

# Configuración
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('dashboard.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Discord Ollama Bot Dashboard"
    })


@app.route('/api/stats')
def get_stats():
    """
    Obtiene estadísticas globales del bot
    
    Returns:
        JSON con estadísticas globales
    """
    try:
        global_stats = stats_manager.get_global_stats()
        
        return jsonify({
            "success": True,
            "data": global_stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/users')
def get_users():
    """
    Obtiene lista de usuarios y sus estadísticas
    
    Returns:
        JSON con lista de usuarios
    """
    try:
        top_users = stats_manager.get_top_users(100)
        
        return jsonify({
            "success": True,
            "count": len(top_users),
            "data": top_users,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/user/<int:user_id>')
def get_user(user_id: int):
    """
    Obtiene estadísticas de un usuario específico
    
    Args:
        user_id: ID del usuario
        
    Returns:
        JSON con estadísticas del usuario
    """
    try:
        user_stats = stats_manager.get_user_stats(user_id)
        
        if user_stats is None:
            return jsonify({
                "success": False,
                "error": "Usuario no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "data": user_stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/hourly')
def get_hourly():
    """
    Obtiene distribución de actividad por hora
    
    Returns:
        JSON con actividad por hora
    """
    try:
        hourly_data = stats_manager.get_hourly_distribution()
        
        # Convertir a formato para gráficos
        hours = list(range(24))
        values = [hourly_data.get(h, 0) for h in hours]
        
        return jsonify({
            "success": True,
            "data": {
                "hours": hours,
                "values": values
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/commands')
def get_commands():
    """
    Obtiene estadísticas de comandos
    
    Returns:
        JSON con uso de comandos
    """
    try:
        commands = stats_manager.get_command_stats()
        top_commands = stats_manager.get_top_commands(10)
        
        return jsonify({
            "success": True,
            "data": {
                "all": commands,
                "top": [{"command": cmd, "uses": uses} for cmd, uses in top_commands]
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/personalities')
def get_personalities():
    """
    Obtiene información sobre personalidades
    
    Returns:
        JSON con personalidades disponibles y estadísticas
    """
    try:
        personalities = personality_manager.list_personalities()
        personality_stats = personality_manager.get_user_stats()
        
        return jsonify({
            "success": True,
            "data": {
                "available": personalities,
                "stats": personality_stats
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/logs/latest')
def get_latest_logs():
    """
    Obtiene los últimos logs del bot
    
    Returns:
        JSON con logs recientes
    """
    try:
        # Obtener últimos errores
        errors = logger.get_latest_errors(10)
        
        # Obtener estadísticas de interacciones
        interaction_stats = logger.get_interaction_stats()
        
        return jsonify({
            "success": True,
            "data": {
                "recent_errors": [error.strip() for error in errors],
                "interaction_stats": interaction_stats
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/summary')
def get_summary():
    """
    Obtiene resumen completo del bot
    
    Returns:
        JSON con resumen completo
    """
    try:
        global_stats = stats_manager.get_global_stats()
        top_users = stats_manager.get_top_users(5)
        top_commands = stats_manager.get_top_commands(5)
        hourly_data = stats_manager.get_hourly_distribution()
        
        return jsonify({
            "success": True,
            "data": {
                "global": global_stats,
                "top_users": top_users,
                "top_commands": [
                    {"command": cmd, "uses": uses} 
                    for cmd, uses in top_commands
                ],
                "hourly_distribution": hourly_data
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/export/stats')
def export_stats():
    """
    Exporta las estadísticas completas
    
    Returns:
        JSON con todas las estadísticas
    """
    try:
        filepath = stats_manager.export_stats()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            "success": True,
            "data": data,
            "exported_file": str(filepath),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Maneja errores 404"""
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado",
        "code": 404
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Maneja errores 500"""
    return jsonify({
        "success": False,
        "error": "Error interno del servidor",
        "code": 500
    }), 500


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Inicia el servidor Flask
    
    Args:
        host: Host donde escuchar
        port: Puerto donde escuchar
        debug: Modo debug
    """
    print("\n" + "="*60)
    print("🌐 Dashboard Web del Bot")
    print("="*60)
    print(f"\n📍 Servidor corriendo en: http://localhost:{port}")
    print(f"📊 Dashboard disponible en: http://localhost:{port}")
    print(f"\n🔌 API Endpoints disponibles:")
    print(f"   • GET  /api/health - Health check")
    print(f"   • GET  /api/stats - Estadísticas globales")
    print(f"   • GET  /api/users - Lista de usuarios")
    print(f"   • GET  /api/user/<id> - Usuario específico")
    print(f"   • GET  /api/hourly - Actividad por hora")
    print(f"   • GET  /api/commands - Estadísticas de comandos")
    print(f"   • GET  /api/personalities - Info de personalidades")
    print(f"   • GET  /api/logs/latest - Logs recientes")
    print(f"   • GET  /api/summary - Resumen completo")
    print(f"   • GET  /api/export/stats - Exportar estadísticas")
    print(f"\n⏹️  Presiona Ctrl+C para detener\n")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")


if __name__ == "__main__":
    run_server(debug=True)