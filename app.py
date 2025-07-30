import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "galaxy-of-consequence-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "galaxy-jwt-secret")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for this system
jwt = JWTManager(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///galaxy.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
CORS(app)

# Swagger UI setup
SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Star Wars RPG HUD API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Import routes after app creation to avoid circular imports
with app.app_context():
    import models
    from routes import canvas, nemotron, faction, quest, session, force
    
    # Register blueprints
    app.register_blueprint(canvas.bp)
    app.register_blueprint(nemotron.bp)
    app.register_blueprint(faction.bp)
    app.register_blueprint(quest.bp)
    app.register_blueprint(session.bp)
    app.register_blueprint(force.bp)
    
    # Create all database tables
    db.create_all()
    
    # Initialize sample data
    models.init_sample_data()

@app.route('/openapi.yaml')
def get_openapi_spec():
    """Serve the OpenAPI specification"""
    from flask import send_file
    return send_file('openapi.yaml', mimetype='text/yaml')

@app.route('/')
def index():
    """Home page with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Galaxy of Consequence API</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <h1 class="card-title">🌌 Galaxy of Consequence</h1>
                            <p class="card-text">Star Wars RPG API with NVIDIA Nemotron Integration</p>
                            <div class="mt-4">
                                <a href="/docs" class="btn btn-primary me-2">API Documentation</a>
                                <a href="/openapi.yaml" class="btn btn-secondary">OpenAPI Spec</a>
                            </div>
                            <div class="mt-4">
                                <small class="text-muted">
                                    Authentication: Bearer Abracadabra<br>
                                    Version: 1.1.2
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
