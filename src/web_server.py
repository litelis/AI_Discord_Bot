from flask import Flask, render_template, jsonify
from flask_cors import CORS
import threading
import json
from pathlib import Path

# Importar gestor de estadísticas
from stats import StatsManager

app = Flask(__name__, 
            template_folder='../web/templates',
            static_folder='../web/static')
CORS(app)

# Instancia global de stats
stats_manager = None

def set_stats_manager(manager):
    """Establece el gestor de estadísticas."""
    global stats_manager
    stats_manager = manager

@app.route('/')
def index():
    """Página principal."""
    return render_template('dashboard.html')

@app.route('/api/stats/summary')
def get_stats_summary():
    """API: Resumen de estadísticas."""
    if stats_manager:
        return jsonify(stats_manager.get_stats_summary())
    return jsonify({"error": "Stats no disponibles"}), 500

@app.route('/api/stats/detailed')
def get_detailed_stats():
    """API: Estadísticas detalladas."""
    if stats_manager:
        return jsonify(stats_manager.get_detailed_stats())
    return jsonify({"error": "Stats no disponibles"}), 500

@app.route('/api/stats/charts')
def get_chart_data():
    """API: Datos para gráficos."""
    if not stats_manager:
        return jsonify({"error": "Stats no disponibles"}), 500
    
    stats = stats_manager.get_detailed_stats()
    
    # Preparar datos para Chart.js
    chart_data = {
        "response_times": {
            "labels": [f"Msg {i+1}" for i in range(len(stats["response_times"][-50:]))],
            "data": stats["response_times"][-50:]  # Últimos 50
        },
        "tokens_per_second": {
            "labels": [f"Msg {i+1}" for i in range(len(stats["tokens_per_second"][-50:]))],
            "data": stats["tokens_per_second"][-50:]
        },
        "messages_by_user": {
            "labels": [f"Usuario {i+1}" for i in range(len(stats["messages_by_user"]))],
            "data": [u["count"] for u in stats["messages_by_user"].values()]
        },
        "commands_usage": {
            "labels": list(stats["commands_used"].keys()),
            "data": list(stats["commands_used"].values())
        }
    }
    
    return jsonify(chart_data)

def run_server(port=5000):
    """Inicia el servidor Flask."""
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def start_web_server(stats_mgr, port=5000):
    """Inicia el servidor web en un thread separado."""
    set_stats_manager(stats_mgr)
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    return thread
