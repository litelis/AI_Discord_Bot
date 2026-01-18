from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import json
from pathlib import Path

class WebServer:
    """Servidor web para el panel de administración del bot."""

    def __init__(self, stats_manager, personality_manager, saved_chats, chat_histories):
        self.stats_manager = stats_manager
        self.personality_manager = personality_manager
        self.saved_chats = saved_chats
        self.chat_histories = chat_histories

        # Crear aplicación Flask
        self.app = Flask(__name__,
                        template_folder='../web/templates',
                        static_folder='../web/static')
        CORS(self.app)

        # Configurar rutas
        self.setup_routes()

    def setup_routes(self):
        """Configura las rutas de la aplicación."""

        @self.app.route('/')
        def index():
            """Página principal del dashboard."""
            return render_template('dashboard.html')

        @self.app.route('/api/stats/summary')
        def get_stats_summary():
            """API: Resumen de estadísticas."""
            return jsonify(self.stats_manager.get_stats_summary())

        @self.app.route('/api/stats/detailed')
        def get_detailed_stats():
            """API: Estadísticas detalladas."""
            return jsonify(self.stats_manager.get_detailed_stats())

        @self.app.route('/api/stats/charts')
        def get_chart_data():
            """API: Datos para gráficos."""
            stats = self.stats_manager.get_detailed_stats()

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

        @self.app.route('/api/chats')
        def get_chats():
            """API: Lista de chats guardados."""
            chats_data = {}
            for user_id, chats in self.saved_chats.items():
                chats_data[user_id] = {}
                for chat_name, history in chats.items():
                    chats_data[user_id][chat_name] = {
                        "message_count": len(history),
                        "last_message": history[-1]["content"][:100] + "..." if len(history) > 0 else ""
                    }
            return jsonify(chats_data)

        @self.app.route('/api/personalities')
        def get_personalities():
            """API: Lista de personalidades disponibles."""
            return jsonify(self.personality_manager.list_personalities())

        @self.app.route('/api/chat/<user_id>/<chat_name>')
        def get_chat(user_id, chat_name):
            """API: Obtener un chat específico."""
            if user_id in self.saved_chats and chat_name in self.saved_chats[user_id]:
                return jsonify({
                    "chat_name": chat_name,
                    "messages": self.saved_chats[user_id][chat_name]
                })
            return jsonify({"error": "Chat no encontrado"}), 404

    def run(self, host='0.0.0.0', port=5000):
        """Inicia el servidor web."""
        print(f"🌐 Servidor web iniciado en http://localhost:{port}")
        self.app.run(host=host, port=port, debug=False, use_reloader=False)
