"""
API routes for mobile applications
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
import jwt
from datetime import datetime, timedelta
from models import db, User, SavedSearch, Comparison, Prescription
from config import Config
import pandas as pd
import os

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Load medicine data (same as main app)
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medicines_sample.csv')
medicines_df = pd.read_csv(DATA_PATH)
medicines_df['name'] = medicines_df['name'].fillna('Unknown')
medicines_df['manufacturer'] = medicines_df['manufacturer'].fillna('Unknown')
medicines_df['composition'] = medicines_df['composition'].fillna('Unknown')
medicines_df['uses'] = medicines_df['uses'].fillna('Not specified')
medicines_df['side_effects'] = medicines_df['side_effects'].fillna('Not specified')


def token_required(f):
    """Decorator to require JWT token for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = db.session.get(User, data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
            
            request.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = db.session.query(User).filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user exists
    if db.session.query(User).filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if db.session.query(User).filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@api_bp.route('/medicines/search', methods=['GET'])
def api_search_medicines():
    """API endpoint to search medicines"""
    query = request.args.get('q', '').strip().lower()
    manufacturer = request.args.get('manufacturer', '').strip()
    discontinued = request.args.get('discontinued', 'all')
    limit = int(request.args.get('limit', 50))
    
    filtered_df = medicines_df.copy()
    
    if query:
        mask = (
            filtered_df['name'].str.lower().str.contains(query, na=False) |
            filtered_df['composition'].str.lower().str.contains(query, na=False) |
            filtered_df['uses'].str.lower().str.contains(query, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if manufacturer:
        filtered_df = filtered_df[
            filtered_df['manufacturer'].str.lower().str.contains(manufacturer.lower(), na=False)
        ]
    
    if discontinued == 'active':
        filtered_df = filtered_df[filtered_df['is_discontinued'] == 'No']
    elif discontinued == 'discontinued':
        filtered_df = filtered_df[filtered_df['is_discontinued'] == 'Yes']
    
    # Limit results
    filtered_df = filtered_df.head(limit)
    
    medicines = filtered_df.to_dict('records')
    
    return jsonify({
        'count': len(medicines),
        'medicines': medicines
    }), 200


@api_bp.route('/medicines/<int:index>', methods=['GET'])
def api_get_medicine(index):
    """API endpoint to get medicine details"""
    if index < 0 or index >= len(medicines_df):
        return jsonify({'error': 'Medicine not found'}), 404
    
    medicine = medicines_df.iloc[index].to_dict()
    return jsonify({'medicine': medicine}), 200


@api_bp.route('/saved-searches', methods=['GET', 'POST'])
@token_required
def api_saved_searches():
    """API endpoint to manage saved searches"""
    user = request.current_user
    
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or not data.get('query'):
            return jsonify({'error': 'Query is required'}), 400
        
        saved_search = SavedSearch(
            user_id=user.id,
            query=data['query'],
            filters=data.get('filters', '')
        )
        
        db.session.add(saved_search)
        db.session.commit()
        
        return jsonify({'saved_search': saved_search.to_dict()}), 201
    
    # GET request - return user's saved searches
    searches = db.session.query(SavedSearch).filter_by(user_id=user.id).order_by(SavedSearch.created_at.desc()).all()
    return jsonify({
        'saved_searches': [s.to_dict() for s in searches]
    }), 200


@api_bp.route('/saved-searches/<int:search_id>', methods=['DELETE'])
@token_required
def api_delete_saved_search(search_id):
    """API endpoint to delete a saved search"""
    user = request.current_user
    saved_search = db.session.query(SavedSearch).filter_by(id=search_id, user_id=user.id).first()
    
    if not saved_search:
        return jsonify({'error': 'Saved search not found'}), 404
    
    db.session.delete(saved_search)
    db.session.commit()
    
    return jsonify({'message': 'Saved search deleted'}), 200


@api_bp.route('/comparisons', methods=['GET', 'POST'])
@token_required
def api_comparisons():
    """API endpoint to manage medicine comparisons"""
    user = request.current_user
    
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or not data.get('medicine_indices'):
            return jsonify({'error': 'Medicine indices are required'}), 400
        
        comparison = Comparison(
            user_id=user.id,
            medicine_indices=data['medicine_indices'],
            title=data.get('title', 'Untitled Comparison')
        )
        
        db.session.add(comparison)
        db.session.commit()
        
        return jsonify({'comparison': comparison.to_dict()}), 201
    
    # GET request
    comparisons = db.session.query(Comparison).filter_by(user_id=user.id).order_by(Comparison.created_at.desc()).all()
    return jsonify({
        'comparisons': [c.to_dict() for c in comparisons]
    }), 200


@api_bp.route('/interactions/check', methods=['POST'])
def api_check_interactions():
    """API endpoint to check drug interactions"""
    data = request.get_json()
    
    if not data or not data.get('medicine_indices'):
        return jsonify({'error': 'Medicine indices are required'}), 400
    
    indices = data['medicine_indices']
    
    if not isinstance(indices, list) or len(indices) < 2:
        return jsonify({'error': 'At least 2 medicine indices are required'}), 400
    
    # Get medicines
    medicines = []
    for idx in indices:
        if 0 <= idx < len(medicines_df):
            medicines.append(medicines_df.iloc[idx].to_dict())
    
    if len(medicines) < 2:
        return jsonify({'error': 'Invalid medicine indices'}), 400
    
    # Check for interactions (basic implementation)
    interactions = check_drug_interactions(medicines)
    
    return jsonify({
        'medicines': medicines,
        'interactions': interactions
    }), 200


def check_drug_interactions(medicines):
    """
    Check for potential drug interactions
    This is a simplified implementation - in production, use a proper drug interaction database
    """
    interactions = []
    
    # Extract active ingredients from all medicines
    compositions = []
    for med in medicines:
        comp = str(med.get('composition', '')).lower()
        compositions.append({
            'medicine': med['name'],
            'composition': comp,
            'ingredients': [word.strip() for word in comp.split() if len(word.strip()) > 3]
        })
    
    # Check for common interaction patterns (simplified)
    interaction_rules = {
        'paracetamol': {
            'warning': 'Do not take multiple medicines containing Paracetamol together',
            'severity': 'high'
        },
        'aspirin': {
            'warning': 'Aspirin may interact with blood thinners and NSAIDs',
            'severity': 'medium'
        },
        'ibuprofen': {
            'warning': 'Avoid taking with other NSAIDs or aspirin',
            'severity': 'medium'
        }
    }
    
    # Check if multiple medicines contain the same active ingredient
    for i, comp1 in enumerate(compositions):
        for j, comp2 in enumerate(compositions[i+1:], i+1):
            # Check for common ingredients
            common = set(comp1['ingredients']) & set(comp2['ingredients'])
            
            if common:
                interactions.append({
                    'medicine1': comp1['medicine'],
                    'medicine2': comp2['medicine'],
                    'type': 'duplicate_ingredient',
                    'ingredients': list(common),
                    'warning': 'These medicines contain common active ingredients',
                    'severity': 'high',
                    'recommendation': 'Consult a healthcare professional before taking together'
                })
            
            # Check for known interactions
            for ingredient in comp1['ingredients']:
                if ingredient in interaction_rules:
                    for ingredient2 in comp2['ingredients']:
                        if ingredient != ingredient2:
                            interactions.append({
                                'medicine1': comp1['medicine'],
                                'medicine2': comp2['medicine'],
                                'type': 'known_interaction',
                                'warning': interaction_rules[ingredient]['warning'],
                                'severity': interaction_rules[ingredient]['severity'],
                                'recommendation': 'Consult a healthcare professional'
                            })
    
    if not interactions:
        return [{
            'type': 'no_interactions',
            'message': 'No known interactions detected',
            'severity': 'none',
            'recommendation': 'Always consult a healthcare professional before taking multiple medications'
        }]
    
    return interactions


@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """API endpoint to get database statistics"""
    total_medicines = len(medicines_df)
    total_manufacturers = medicines_df['manufacturer'].nunique()
    discontinued_count = len(medicines_df[medicines_df['is_discontinued'] == 'Yes'])
    active_count = len(medicines_df[medicines_df['is_discontinued'] == 'No'])
    
    return jsonify({
        'total_medicines': total_medicines,
        'total_manufacturers': total_manufacturers,
        'discontinued_count': discontinued_count,
        'active_count': active_count
    }), 200
