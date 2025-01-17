# app/__init__.py
import os
from flask import Flask
from flask_socketio import SocketIO
from .database import engine
from .models import Base
from .routes import bp as main_bp  # Import the blueprint from routes.py

def create_app():
    # Create the Flask app with explicit template and static folder locations
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Register the blueprint for routes
    app.register_blueprint(main_bp)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    return app, socketio
