# Medicine Search System - Quick Start Guide

## Overview

The Medicine Search System is a comprehensive web application with the following features:

✅ **User Authentication** - Secure registration and login  
✅ **Medicine Search** - Search by name, composition, or use  
✅ **Medicine Comparison** - Compare multiple medicines side-by-side  
✅ **Drug Interaction Checker** - Check for potential interactions  
✅ **Prescription Upload** - Upload and analyze prescriptions  
✅ **Saved Searches** - Save frequently used searches  
✅ **RESTful API** - Complete API for mobile applications  

## Quick Setup

### 1. Install Dependencies

```bash
cd Medicine_Search_System
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will:
- Automatically create the database
- Start the web server on `http://localhost:5000`

### 3. Access the Application

Open your browser and navigate to: `http://localhost:5000`

## Using the Web Interface

### Basic Search
1. Go to the home page
2. Enter a medicine name (e.g., "paracetamol")
3. Click "Search"
4. Browse results

### Compare Medicines
1. Search for medicines
2. Check the boxes next to medicines you want to compare
3. Click "Compare Selected"
4. View side-by-side comparison

### Check Drug Interactions
1. Search for medicines
2. Check the boxes next to medicines
3. Click "Check Interactions"
4. View interaction analysis and recommendations

### Upload Prescription
1. Click "Upload Prescription" in the navigation
2. Choose an image or PDF file
3. Click "Upload and Analyze"
4. View extracted medicines

### User Account Features
1. Click "Register" to create an account
2. Login with your credentials
3. Access additional features:
   - Save searches for later
   - Save comparison sets
   - View your activity

## Using the API

### Authentication

Register a new user:
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "user@example.com",
    "password": "mypassword"
  }'
```

Login and get token:
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypassword"
  }'
```

### Search Medicines

```bash
curl "http://localhost:5000/api/v1/medicines/search?q=paracetamol"
```

### Check Drug Interactions

```bash
curl -X POST http://localhost:5000/api/v1/interactions/check \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_indices": [0, 1, 2]
  }'
```

### Save a Search (Requires Authentication)

```bash
curl -X POST http://localhost:5000/api/v1/saved-searches \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "paracetamol"
  }'
```

## Testing

Run the automated test suite:

```bash
# Start the Flask app first
python app.py

# In another terminal:
python test_features.py
```

Expected output:
```
============================================================
Medicine Search System - Feature Tests
============================================================
Testing home page...
✓ Home page loads successfully

Testing search API...
✓ Search API works - Found X medicine(s)

... (all tests pass)

============================================================
✓ All tests passed successfully!
============================================================
```

## Complete API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference including:
- All endpoints
- Request/response formats
- Authentication details
- Error codes
- Code examples in multiple languages

## Data Structure

### Medicine Data Fields

- `name`: Medicine name
- `manufacturer`: Manufacturer company
- `composition`: Active ingredients and dosage
- `uses`: Therapeutic uses
- `side_effects`: Common side effects
- `pack_size_label`: Package information
- `is_discontinued`: Active or discontinued status
- `short_composition1/2`: Simplified composition

### Sample Data

The system includes sample medicine data. To use the full 1mg dataset:

1. Download from [Kaggle](https://www.kaggle.com/datasets/prothomeshmistry/1mg-medicine-dataset)
2. Place CSV file in the `data/` directory
3. Update `DATA_PATH` in `app.py` to point to your file

## Configuration

### Environment Variables

Create a `.env` file (optional):

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///medicine_search.db
FLASK_DEBUG=False
```

### Production Deployment

For production deployment:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Security Settings:**
   - Set strong secret keys
   - Disable debug mode
   - Enable HTTPS
   - Set up rate limiting

3. **Database:**
   - Consider PostgreSQL for production
   - Set up regular backups
   - Configure connection pooling

4. **File Storage:**
   - Use cloud storage for prescription uploads
   - Implement proper access controls

## Features in Detail

### Medicine Comparison
- Side-by-side comparison of multiple medicines
- Compare composition, uses, side effects
- Save comparisons for later reference

### Drug Interaction Checker
- Analyzes potential interactions between medicines
- Checks for duplicate active ingredients
- Provides severity levels (high, medium, none)
- Gives recommendations for each interaction

**Note:** This is a basic implementation. For production, integrate with a comprehensive drug interaction database like DrugBank or InteractDB.

### Prescription Upload
- Supports PNG, JPG, JPEG, PDF formats
- Maximum file size: 16MB
- Basic medicine extraction (demo mode)

**Enhancement Opportunity:** Integrate OCR (Tesseract) for actual text extraction from images.

## Troubleshooting

### Database Issues

If you encounter database errors:
```bash
rm medicine_search.db
python app.py
```
This will recreate the database.

### Port Already in Use

If port 5000 is already in use:
```python
# Edit app.py, last line:
app.run(debug=debug_mode, host='0.0.0.0', port=8000)  # Change to 8000
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --force-reinstall
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Passwords:** All passwords are hashed using Werkzeug security
2. **API Tokens:** JWT tokens expire after 24 hours
3. **Sessions:** Web sessions expire after 7 days
4. **File Uploads:** File types and sizes are validated
5. **SQL Injection:** Protected by SQLAlchemy ORM

**For Production:**
- Use environment variables for secrets
- Enable HTTPS/SSL
- Implement rate limiting
- Add CORS configuration for API
- Regular security audits

## Medical Disclaimer

⚠️ **IMPORTANT:** This application is for educational and informational purposes only. 

- Always consult with a qualified healthcare professional before taking any medication
- Do not self-medicate based on information from this application
- Drug interaction checker provides basic analysis only
- Prescription analysis is simplified and not medically verified

## License

This project is for educational purposes.

## Support

For issues, questions, or feature requests:
1. Check the README.md
2. Review API_DOCUMENTATION.md
3. Open an issue on GitHub

## Next Steps

After setup, try:
1. Search for common medicines (e.g., "aspirin", "ibuprofen")
2. Create a user account
3. Compare two or more medicines
4. Check for drug interactions
5. Explore the API endpoints
6. Run the test suite

Enjoy exploring the Medicine Search System! 🎉
