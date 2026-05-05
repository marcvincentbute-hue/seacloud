from .auth_routes import auth_bp
from .admin_routes import admin_bp 
from .operator_routes import operator_bp
from .customer_routes import customer_bp
from .forgot_routes import forgot_bp
from .page_routes import page_bp
from .weather_routes import weather_bp
from .notification_routes import notification_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)  
    app.register_blueprint(operator_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(forgot_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(notification_bp)