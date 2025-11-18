"""
Medicine Search and Information System
A web application to search and view medicine information using the 1mg medicine dataset
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename

# Import configuration and models
from config import Config
from models import db, User, SavedSearch, Comparison, Prescription

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
from auth import auth_bp
from api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Load the medicine dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medicines_sample.csv')
medicines_df = pd.read_csv(DATA_PATH)

# Clean and prepare data
medicines_df['name'] = medicines_df['name'].fillna('Unknown')
medicines_df['manufacturer'] = medicines_df['manufacturer'].fillna('Unknown')
medicines_df['composition'] = medicines_df['composition'].fillna('Unknown')
medicines_df['uses'] = medicines_df['uses'].fillna('Not specified')
medicines_df['side_effects'] = medicines_df['side_effects'].fillna('Not specified')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Home page with search functionality"""
    return render_template('index.html')


@app.route('/search')
def search():
    """Search for medicines based on query"""
    query = request.args.get('q', '').strip().lower()
    manufacturer_filter = request.args.get('manufacturer', '').strip()
    discontinued_filter = request.args.get('discontinued', 'all')
    
    if not query and not manufacturer_filter:
        return render_template('search.html', medicines=[], query='')
    
    # Filter medicines
    filtered_df = medicines_df.copy()
    
    if query:
        # Search in name, composition, and uses
        mask = (
            filtered_df['name'].str.lower().str.contains(query, na=False) |
            filtered_df['composition'].str.lower().str.contains(query, na=False) |
            filtered_df['uses'].str.lower().str.contains(query, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if manufacturer_filter:
        filtered_df = filtered_df[
            filtered_df['manufacturer'].str.lower().str.contains(manufacturer_filter.lower(), na=False)
        ]
    
    if discontinued_filter == 'active':
        filtered_df = filtered_df[filtered_df['is_discontinued'] == 'No']
    elif discontinued_filter == 'discontinued':
        filtered_df = filtered_df[filtered_df['is_discontinued'] == 'Yes']
    
    # Convert to list of dictionaries
    medicines = filtered_df.to_dict('records')
    
    return render_template('search.html', medicines=medicines, query=query)


@app.route('/medicine/<int:index>')
def medicine_detail(index):
    """View detailed information about a specific medicine"""
    if index < 0 or index >= len(medicines_df):
        return render_template('error.html', message='Medicine not found'), 404
    
    medicine = medicines_df.iloc[index].to_dict()
    
    # Find alternatives based on similar composition
    alternatives = find_alternatives(medicine, index)
    
    return render_template('medicine.html', medicine=medicine, alternatives=alternatives, index=index)


def find_alternatives(medicine, current_index):
    """Find alternative medicines with similar composition"""
    alternatives = []
    
    # Extract main active ingredient from composition
    composition = str(medicine.get('composition', '')).lower()
    
    # Search for medicines with similar composition
    for idx, row in medicines_df.iterrows():
        if idx != current_index:
            if any(word in str(row['composition']).lower() for word in composition.split() if len(word) > 3):
                alternatives.append({
                    'index': idx,
                    'name': row['name'],
                    'manufacturer': row['manufacturer'],
                    'composition': row['composition'],
                    'pack_size_label': row['pack_size_label']
                })
                if len(alternatives) >= 5:  # Limit to 5 alternatives
                    break
    
    return alternatives


@app.route('/manufacturers')
def get_manufacturers():
    """Get list of all manufacturers"""
    manufacturers = sorted(medicines_df['manufacturer'].unique().tolist())
    return jsonify(manufacturers)


@app.route('/stats')
def stats():
    """Display statistics about the medicine database"""
    total_medicines = len(medicines_df)
    total_manufacturers = medicines_df['manufacturer'].nunique()
    discontinued_count = len(medicines_df[medicines_df['is_discontinued'] == 'Yes'])
    active_count = len(medicines_df[medicines_df['is_discontinued'] == 'No'])
    
    # Top manufacturers
    top_manufacturers = medicines_df['manufacturer'].value_counts().head(10).to_dict()
    
    stats_data = {
        'total_medicines': total_medicines,
        'total_manufacturers': total_manufacturers,
        'discontinued_count': discontinued_count,
        'active_count': active_count,
        'top_manufacturers': top_manufacturers
    }
    
    return render_template('stats.html', stats=stats_data)


@app.route('/saved-searches')
@login_required
def saved_searches():
    """View user's saved searches"""
    searches = SavedSearch.query.filter_by(user_id=current_user.id).order_by(SavedSearch.created_at.desc()).all()
    return render_template('saved_searches.html', searches=searches)


@app.route('/save-search', methods=['POST'])
@login_required
def save_search():
    """Save a search for the current user"""
    query = request.form.get('query', '').strip()
    filters = json.dumps({
        'manufacturer': request.form.get('manufacturer', ''),
        'discontinued': request.form.get('discontinued', 'all')
    })
    
    if query:
        saved_search = SavedSearch(
            user_id=current_user.id,
            query=query,
            filters=filters
        )
        db.session.add(saved_search)
        db.session.commit()
        flash('Search saved successfully!', 'success')
    
    return redirect(url_for('search', q=query))


@app.route('/delete-saved-search/<int:search_id>', methods=['POST'])
@login_required
def delete_saved_search(search_id):
    """Delete a saved search"""
    saved_search = SavedSearch.query.filter_by(id=search_id, user_id=current_user.id).first()
    
    if saved_search:
        db.session.delete(saved_search)
        db.session.commit()
        flash('Saved search deleted', 'success')
    
    return redirect(url_for('saved_searches'))


@app.route('/compare')
def compare():
    """Compare multiple medicines"""
    indices_str = request.args.get('indices', '')
    
    if not indices_str:
        return render_template('compare.html', medicines=[])
    
    try:
        indices = [int(i) for i in indices_str.split(',') if i.strip()]
        medicines = []
        
        for idx in indices:
            if 0 <= idx < len(medicines_df):
                medicines.append(medicines_df.iloc[idx].to_dict())
        
        return render_template('compare.html', medicines=medicines, indices=indices)
    except ValueError:
        flash('Invalid medicine indices', 'error')
        return redirect(url_for('search'))


@app.route('/save-comparison', methods=['POST'])
@login_required
def save_comparison():
    """Save a medicine comparison"""
    indices = request.form.get('indices', '')
    title = request.form.get('title', 'Untitled Comparison')
    
    if indices:
        comparison = Comparison(
            user_id=current_user.id,
            medicine_indices=indices,
            title=title
        )
        db.session.add(comparison)
        db.session.commit()
        flash('Comparison saved successfully!', 'success')
    
    return redirect(url_for('comparisons'))


@app.route('/comparisons')
@login_required
def comparisons():
    """View user's saved comparisons"""
    user_comparisons = Comparison.query.filter_by(user_id=current_user.id).order_by(Comparison.created_at.desc()).all()
    return render_template('comparisons.html', comparisons=user_comparisons)


@app.route('/interactions')
def interactions():
    """Drug interaction checker"""
    indices_str = request.args.get('indices', '')
    
    if not indices_str:
        return render_template('interactions.html', medicines=[], interactions=[])
    
    try:
        indices = [int(i) for i in indices_str.split(',') if i.strip()]
        medicines = []
        
        for idx in indices:
            if 0 <= idx < len(medicines_df):
                medicines.append({
                    'index': idx,
                    'data': medicines_df.iloc[idx].to_dict()
                })
        
        # Check for interactions
        from api import check_drug_interactions
        interactions = check_drug_interactions([m['data'] for m in medicines])
        
        return render_template('interactions.html', medicines=medicines, interactions=interactions, indices=indices)
    except ValueError:
        flash('Invalid medicine indices', 'error')
        return redirect(url_for('search'))


@app.route('/prescription-upload', methods=['GET', 'POST'])
def prescription_upload():
    """Upload and analyze prescription"""
    if request.method == 'POST':
        if 'prescription' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['prescription']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Basic extraction (simplified - in production, use OCR)
            extracted_medicines = extract_medicines_from_prescription(filepath)
            
            # Save prescription record
            prescription = Prescription(
                user_id=current_user.id if current_user.is_authenticated else None,
                filename=filename,
                filepath=filepath,
                extracted_medicines=json.dumps(extracted_medicines)
            )
            db.session.add(prescription)
            db.session.commit()
            
            flash('Prescription uploaded successfully!', 'success')
            return render_template('prescription_result.html', 
                                 medicines=extracted_medicines,
                                 prescription_id=prescription.id)
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF', 'error')
            return redirect(request.url)
    
    return render_template('prescription_upload.html')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def extract_medicines_from_prescription(filepath):
    """
    Extract medicine names from prescription
    This is a simplified implementation - in production, use OCR and NLP
    """
    # For demo purposes, search for common medicine names in the database
    # In production, implement proper OCR using tools like Tesseract
    
    # Return sample extracted medicines
    sample_medicines = []
    for idx, row in medicines_df.head(3).iterrows():
        sample_medicines.append({
            'name': row['name'],
            'index': idx,
            'confidence': 'high'
        })
    
    return sample_medicines


if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Debug mode should only be enabled in development
    # Set debug=False or use environment variable for production
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
