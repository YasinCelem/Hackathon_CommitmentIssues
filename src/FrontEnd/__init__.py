from flask import Flask, session


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    from src.FrontEnd.routes import bp as frontend_bp
    app.register_blueprint(frontend_bp)
    
    from src.FrontEnd.nav import NAV
    from src.FrontEnd.auth import is_authenticated, get_current_user
    
    @app.context_processor
    def inject_nav():
        return {
            "nav": NAV,
            "is_authenticated": is_authenticated(),
            "current_user": get_current_user()
        }
    
    return app

