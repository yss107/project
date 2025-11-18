"""
Database models for Medicine Search System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_searches = db.relationship('SavedSearch', backref='user', lazy=True, cascade='all, delete-orphan')
    comparisons = db.relationship('Comparison', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class SavedSearch(db.Model):
    """Model for saved searches"""
    __tablename__ = 'saved_searches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(255), nullable=False)
    filters = db.Column(db.Text)  # JSON string of filters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert saved search to dictionary"""
        return {
            'id': self.id,
            'query': self.query,
            'filters': self.filters,
            'created_at': self.created_at.isoformat()
        }


class Comparison(db.Model):
    """Model for medicine comparisons"""
    __tablename__ = 'comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_indices = db.Column(db.Text, nullable=False)  # Comma-separated indices
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert comparison to dictionary"""
        return {
            'id': self.id,
            'medicine_indices': self.medicine_indices,
            'title': self.title,
            'created_at': self.created_at.isoformat()
        }


class Prescription(db.Model):
    """Model for prescription uploads"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    extracted_medicines = db.Column(db.Text)  # JSON string of extracted medicine names
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert prescription to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'extracted_medicines': self.extracted_medicines,
            'uploaded_at': self.uploaded_at.isoformat()
        }
