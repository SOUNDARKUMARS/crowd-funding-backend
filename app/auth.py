from flask import Blueprint, request 
from .models import User
from datetime import timedelta
from .import db
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login_user():
    username = request.json.get('username')
    email = request.json.get('email')
    img = request.json.get('img_url')
    password = request.json.get('password')
    google_login = request.json.get('google_login', False)

    if google_login:
        if email is None or img is None:
            return {"err": "missing params"}, 400
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, profile_img_url=img)
            db.session.add(user)
            db.session.commit()
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))
        return {"access_token": access_token, "message": "Login successful via Google"}, 200
    else:
        if username is None or email is None or password is None:
            return {"err": "missing params"}, 400
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))
            return {"access_token": access_token, "message": "Login successful"}, 200
        else:
            return {"err": "Invalid credentials or user does not exist"}, 401

@auth.route('/signup', methods=['POST'])
def signup_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if username is None or email is None or password is None:
        return {"err": "missing params", "code": "missing_params"}, 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"err": "user already exists", "code": "user_already_exists"}, 400

    new_user = User(username=username, email=email, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
        user_id = new_user.id  
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(days=30))
        return {"message": "user created successfully", "access_token": access_token}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"user creation failed. {e}"}, 500
