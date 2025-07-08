from flask import Flask
from flask_pymongo import PyMongo
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()


def create_app():
    # Get root path of project
    base_dir = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        template_folder=str(base_dir / 'templates')  # Explicit template path
    )

    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/github_events')

    try:
        mongo.init_app(app)
        mongo.db.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        raise

    # Register blueprints
    from .webhook import routes as webhook_routes
    app.register_blueprint(webhook_routes.bp)

    return app