from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

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
            try:
                return render_template('dashboard.html')
            except Exception:
                return "Dashboard activo. (Error: No se encuentra web/templates/dashboard.html)"

        @self.app.route('/api/stats/summary')
        def get_stats_summary():
            return jsonify(self.stats_manager.get_stats_summary())

        @self.app.route('/api/chats')
        def get_chats():
            """Lista de chats guardados con metadatos básicos."""
            chats_data = {}
            for user_id, chats in self.saved_chats.items():
                chats_data[user_id] = {}
                for chat_name, history in chats.items():
                    last_msg = history[-1]["content"][:50] + "..." if history else ""
                    chats_data[user_id][chat_name] = {
                        "message_count": len(history),
                        "last_message": last_msg
                    }
            return jsonify(chats_data)

        @self.app.route('/api/chat/<user_id>/<chat_name>')
        def get_specific_chat(user_id, chat_name):
            """Obtiene los mensajes reales de un chat específico."""
            if user_id in self.saved_chats and chat_name in self.saved_chats[user_id]:
                return jsonify({
                    "chat_name": chat_name,
                    "messages": self.saved_chats[user_id][chat_name]
                })
            return jsonify({"error": "Chat no encontrado"}), 404

        @self.app.route('/api/config', methods=['GET', 'POST'])
        def manage_config():
            if request.method == 'POST':
                data = request.json
                # Aquí puedes añadir lógica para guardar en el .env si lo necesitas
                return jsonify({"status": "success", "message": "Configuración actualizada"})
            
            # Datos de ejemplo basados en tu bot
            return jsonify({
                "model_name": "llama3.2",
                "use_gpu": os.getenv('USE_GPU', 'false').lower() == 'true',
                "authorized_ids": os.getenv('AUTHORIZED_IDS', '').split(',')
            })

    def run(self, host='0.0.0.0', port=5000):
        """Inicia el servidor web."""
        self.app.run(host=host, port=port, debug=False, use_reloader=False)