from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False, unique=True)
    profile_img_url = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaigns = db.relationship('Campaign', backref='creator', lazy=True)
    contributions = db.relationship('Contribution', backref='contributor', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)

    campaigns = db.relationship('Campaign', backref='category', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goal_amount = db.Column(db.Float, nullable=False)
    collected_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    img_url = db.Column(db.String(120))
    campaign_images = db.Column(db.JSON)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    contributions = db.relationship('Contribution', backref='campaign', lazy=True)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contributed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount_required = db.Column(db.Float, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contribution_id = db.Column(db.Integer, db.ForeignKey('contribution.id'), nullable=False)
    transaction_status = db.Column(db.String(50), nullable=False)  # e.g., 'Pending', 'Completed', 'Failed'
    transaction_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
