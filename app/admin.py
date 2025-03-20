from flask import Blueprint,jsonify,request
from .models import User, Campaign, Category
from datetime import datetime
from .import db
from flask_jwt_extended import jwt_required,get_jwt_identity

admin=Blueprint('admin',__name__)

@admin.route('/')
@jwt_required()
def home():
    return {"message":"hi admin"}

@admin.route('/create-category', methods=['POST'])
# @jwt_required() temp_change temp_removal
def create_category():
    name = request.json.get('name')
    description = request.json.get('description')

    if not name:
        return {"err": "Category name is required"}, 400

    new_category = Category(name=name, description=description)

    try:
        db.session.add(new_category)
        db.session.commit()
        return {"message": f"Category '{name}' created successfully"}, 201
    except Exception as e:
        return {"error": f"Failed to create category: {e}"}, 500

@admin.route('/get-categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": cat.id, "name": cat.name, "description": cat.description} for cat in categories]), 200

@admin.route('/update-category/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return {"err": "Category not found"}, 404

    name = request.json.get('name')
    description = request.json.get('description')

    if name:
        category.name = name
    if description:
        category.description = description

    db.session.commit()
    return {"message": f"Category '{category.name}' updated successfully"}, 200

@admin.route('/delete-category/<int:id>', methods=['DELETE'])
# @jwt_required() temp_change temp_removal
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return {"err": "Category not found"}, 404

    db.session.delete(category)
    db.session.commit()
    return {"message": f"Category '{category.name}' deleted successfully"}, 200

