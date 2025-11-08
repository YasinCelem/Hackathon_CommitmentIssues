from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    from src.FrontEnd.routes import bp as frontend_bp
    app.register_blueprint(frontend_bp)
    
    from src.FrontEnd.nav import NAV
    
    @app.context_processor
    def inject_nav():
        return {"nav": NAV}
    
    return app

