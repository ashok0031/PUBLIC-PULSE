import os
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
env_paths = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), '.env')),
    '.env'
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded .env from: {env_path}")
        break
else:
    print("⚠️  Warning: No .env file found")

# Verify key environment variables are loaded
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY not found in environment")
from flask import Flask, jsonify
from app.database import db, init_db
from flask_migrate import Migrate
from app.models import *
from app.routes import register_routes
import logging
from flask_cors import CORS
from flask_mail import Mail
from app.celery_app import make_celery

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    migrate = Migrate(app, db)
    
    # Initialize Celery
    celery = make_celery(app)
    app.celery = celery
    
    # Register routes
    register_routes(app)

    # Enable CORS with specific configuration
    CORS(app, 
         resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Logging setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

    # Handle favicon.ico requests
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    # Handle .well-known requests (optional, for Chrome DevTools)
    @app.route('/.well-known/<path:anything>')
    def well_known(anything):
        return '', 204

    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    mail.init_app(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db.engine else 'disconnected',
            'celery': 'available' if celery else 'unavailable'
        })
    
    # Background task status endpoint
    @app.route('/api/background/status')
    def background_status():
        try:
            from app.services.search_index import SearchIndexService
            search_service = SearchIndexService()
            search_stats = search_service.get_index_stats()
            
            return jsonify({
                'search_index': search_stats,
                'celery_workers': 'running' if celery else 'stopped'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app 