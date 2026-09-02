from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors
from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
from app.routes.customer_routes import customer_bp
from app.routes.sales_routes import sales_bp
from app.routes.payment_routes import payment_bp
from app.routes.balance_routes import balance_bp
from app.routes.report_routes import report_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(balance_bp)
    app.register_blueprint(report_bp)

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ClothBook REST API', 'version': '1.0.0'}

    return app
