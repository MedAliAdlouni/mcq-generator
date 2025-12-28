import os
from flask import Flask
from datetime import datetime
from flask_login import current_user
from .db import init_db
from .routes import documents, quizzes, results, ui, auth
from .routes.auth import login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DATABASE_URL=os.getenv("DATABASE_URL"),
        FLASK_ENV=os.getenv("FLASK_ENV")
    )

    print("Initializing the database ...")
    # initiate database
    init_db(app)
    print("the database has been initialized successfully.")

    # authentication
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # blueprints
    print("Initialize auth blueprint ...")
    app.register_blueprint(auth.bp)
    print("auth blueprint successfully initialized! ...")
    # --------------------------------------------------------------------------------------------------------
    print("Initialize documents blueprint ...")
    app.register_blueprint(documents.bp)
    print("documents blueprint successfully initialized! ...")
    # --------------------------------------------------------------------------------------------------------
    print("Initialize quizzes blueprint ...")
    app.register_blueprint(quizzes.bp)
    print("quizzes blueprint successfully initialized! ...")
    # --------------------------------------------------------------------------------------------------------
    print("Initialize results blueprint ...")
    app.register_blueprint(results.bp)
    print("results blueprint successfully initialized! ...")
    # --------------------------------------------------------------------------------------------------------
    print("Initialize ui blueprint ...")
    app.register_blueprint(ui.bp)
    print("ui blueprint successfully initialized! ...")


    @app.context_processor
    def inject_globals():
        return {
            "app_name": "mcq generator",
            "app_tagline": "magic",
            "current_year": datetime.now().year,
            "current_user": current_user
        }

    return app
