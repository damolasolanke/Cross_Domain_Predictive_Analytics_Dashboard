#!/usr/bin/env python3
"""
Run script for the Cross-Domain Predictive Analytics Dashboard
"""
import sys
import os
from flask import Flask
from flask_socketio import SocketIO

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    print("Starting Cross-Domain Predictive Analytics Dashboard...")
    print("Server running at http://localhost:5000")
    
    # Create a simple Flask app without using the module-level app
    flask_app = Flask(__name__, 
                      template_folder="app/templates",
                      static_folder="app/static")
    
    # Configure the application
    flask_app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    flask_app.config['DEBUG'] = False
    
    # Initialize Socket.IO
    socketio = SocketIO(flask_app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.main.routes import main
    flask_app.register_blueprint(main)
    
    # Register Natural Language Query blueprints
    from app.nlq.routes import nlq_routes
    flask_app.register_blueprint(nlq_routes)
    
    from app.nlq.api import nlq_blueprint
    flask_app.register_blueprint(nlq_blueprint)
    
    # Register API blueprint
    from app.api import api
    flask_app.register_blueprint(api, url_prefix='/api')
    
    # Register analytics blueprint
    from app.main.analytics_controller import analytics
    flask_app.register_blueprint(analytics)
    
    # Register System Integration blueprint
    from app.system_integration import system_integration
    flask_app.register_blueprint(system_integration, url_prefix='/system')
    
    # Register visualization blueprint
    from app.visualizations import visualization_bp
    flask_app.register_blueprint(visualization_bp, url_prefix='/visualization')
    
    # Try to register demo blueprint
    try:
        from app.demo.correlation_demo import correlation_demo
        flask_app.register_blueprint(correlation_demo)
    except ImportError:
        # This is fine if the demo is not available
        pass
    
    # Socket.IO event handlers
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('request_update')
    def handle_request_update(data):
        # When a client requests an update, emit data to that client
        # In a real app, this would fetch real data
        from app.main.routes import dashboard_data_new
        import json
        from flask import jsonify
        
        # Get dashboard data
        response = dashboard_data_new()
        data = json.loads(response.get_data(as_text=True))
        
        # Emit the data as an event
        socketio.emit('dashboard_update', data)
    
    # Run the application with Socket.IO
    socketio.run(flask_app, host='0.0.0.0', port=5000, debug=False)