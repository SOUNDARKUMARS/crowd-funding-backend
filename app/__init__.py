from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_rL9a5tSIjPqC@ep-white-poetry-a5cjynti-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this for security

    db.init_app(app)
    Migrate(app, db)  # For database migrations
    JWTManager(app)   # For JWT authentication
    CORS(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    return app
