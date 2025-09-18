import os
from flask import Flask, jsonify, session
from functools import wraps

from config import config
from .extensions import db, bcrypt, cors, session as server_session, csrf, migrate

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    # Load CORS origins from config
    cors.init_app(app, origins=app.config['CORS_ORIGINS'].split(','), supports_credentials=True)
    server_session.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # A simple route to get the CSRF token
    @app.route('/api/csrf-token', methods=['GET'])
    def get_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return jsonify({"csrf_token": generate_csrf()})

    # Import and register blueprints
    from .api.routes import api_bp
    from .auth.routes import auth_bp
    from .orders.routes import orders_bp
    from .admin.routes import admin_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @api_login_required
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
