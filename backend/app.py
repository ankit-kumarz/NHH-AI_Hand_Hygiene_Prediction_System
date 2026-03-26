"""
Enhanced Flask App with Real-time WebSocket Support
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from models.db import db, init_db
from routes.hygiene import hygiene_bp
from routes.analytics import analytics_bp
from realtime.events import init_socketio
from datetime import datetime


def create_app(config=None):
    """
    Application factory with SocketIO support
    
    Environment variables:
    - DATABASE_URL: PostgreSQL connection string
    - FLASK_ENV: development/production
    - SECRET_KEY: Flask secret key
    """
    app = Flask(__name__)
    
    # Configuration
    if config:
        app.config.update(config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:password@localhost:5432/hand_hygiene'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JSON_SORT_KEYS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    init_db(app)
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # WebSocket
    socketio = init_socketio(app)
    
    # Blueprints
    app.register_blueprint(hygiene_bp)
    app.register_blueprint(analytics_bp)
    
    # Root route
    @app.route('/', methods=['GET'])
    def root():
        """API root endpoint"""
        return jsonify({
            'name': 'Hand Hygiene Compliance Monitoring System',
            'version': '2.0.0',
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'features': ['AI Detection', 'Real-time Monitoring', 'Analytics', 'WebSocket Alerts'],
            'endpoints': {
                'health': '/api/health',
                'log_event': 'POST /api/log',
                'get_logs': 'GET /api/logs',
                'get_stats': 'GET /api/stats',
                'daily_stats': 'GET /api/stats/daily',
                'user_stats': 'GET /api/stats/user/<user_id>',
                'create_user': 'POST /api/users',
                'get_user': 'GET /api/users/<user_id>',
                'analytics_trend': 'GET /api/analytics/trend',
                'analytics_departments': 'GET /api/analytics/departments',
                'analytics_leaderboard': 'GET /api/analytics/leaderboard',
                'analytics_peak_hours': 'GET /api/analytics/peak-hours',
                'analytics_anomalies': 'GET /api/analytics/anomalies',
                'analytics_insights': 'GET /api/analytics/insights',
                'analytics_export': 'GET /api/analytics/export/csv',
                'analytics_dashboard': 'GET /api/analytics/dashboard',
                'websocket': 'WS /socket.io'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    print("🏥 Starting Hand Hygiene Backend Server with Real-time Support...")
    print("📊 Database: PostgreSQL")
    print("🚀 Server: http://localhost:5000")
    print("📡 API: http://localhost:5000/api")
    print("🔌 WebSocket: WS ws://localhost:5000/socket.io")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
