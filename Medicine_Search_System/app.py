"""
Medicine Search and Information System
A web application to search and view medicine information using the 1mg medicine dataset
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the medicine dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medicines_sample.csv')
medicines_df = pd.read_csv(DATA_PATH)

# Clean and prepare data
medicines_df['name'] = medicines_df['name'].fillna('Unknown')
medicines_df['manufacturer'] = medicines_df['manufacturer'].fillna('Unknown')
medicines_df['composition'] = medicines_df['composition'].fillna('Unknown')
medicines_df['uses'] = medicines_df['uses'].fillna('Not specified')
medicines_df['side_effects'] = medicines_df['side_effects'].fillna('Not specified')


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


if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Set debug=False or use environment variable for production
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
