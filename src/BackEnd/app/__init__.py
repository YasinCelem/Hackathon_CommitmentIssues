from flask import Flask, redirect
from flasgger import Swagger
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    from .routes.data_routes import data_bp
    from .routes.user_routes import user_bp
    from .routes.doc_routes import docs_bp
    app.register_blueprint(data_bp, url_prefix="/api/data")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(docs_bp, url_prefix="/api/docs")

    app.config["SWAGGER"] = {"title": "Financial API", "uiversion": 3}
    Swagger(app)

    @app.get("/")
    def home():
        return redirect("/apidocs")

    @app.get("/health")
    def health():
        """Health check
        ---
        tags: [Meta]
        responses:
          200:
            description: OK
        """
        return {"status": "ok"}

    return app
