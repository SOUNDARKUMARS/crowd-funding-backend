from flask import Blueprint, request 
from .models import User
from datetime import timedelta
from .import db
from flask_jwt_extended import create_access_token

auth=Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login_user():
    username=request.json.get('username')
    email=request.json.get('email')
    img=request.json.get('img_url')
    if username is None or email is None or img is None:
        return {"err":"missing params"},400

    # First check if user exists with this email
    existing_user=User.query.filter_by(email=email).first()
    if existing_user:
        access_token=create_access_token(identity=str(existing_user.id), expires_delta=timedelta(days=30))
        return {"access_token":access_token, "message":'Login successful'}
    
    # Create new user
    new_user=User(username=username,email=email,profile_img_url=img)
    try:
        db.session.add(new_user)
        db.session.commit()
        user_id = new_user.id  
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(days=30))
        return {"message": "Account created successfully","access_token": access_token}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Account creation failed. Try again, Not you, it's us. {e}"}, 500
