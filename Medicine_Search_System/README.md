# Medicine Search and Information System

A web-based application for searching and viewing comprehensive information about medicines using the 1mg medicine dataset.

## Features

- 🔍 **Smart Search**: Search medicines by name, composition, or therapeutic use
- 💊 **Detailed Information**: View complete information including uses, side effects, and manufacturer details
- 🔄 **Alternative Medicines**: Find alternative medicines with similar composition
- 📊 **Statistics Dashboard**: Explore comprehensive database statistics
- 🏭 **Manufacturer Filtering**: Filter medicines by manufacturer
- ✅ **Status Tracking**: View active and discontinued medicines

## Project Structure

```
Medicine_Search_System/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   └── medicines_sample.csv    # Medicine dataset
├── static/
│   └── css/
│       └── style.css          # CSS styling
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Home page
    ├── search.html            # Search results page
    ├── medicine.html          # Medicine detail page
    ├── stats.html             # Statistics page
    └── error.html             # Error page
```

## Installation

1. **Clone the repository**
   ```bash
   cd Medicine_Search_System
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask application**
   ```bash
   python app.py
   ```
   
   For development with debug mode enabled:
   ```bash
   export FLASK_DEBUG=true  # On Windows: set FLASK_DEBUG=true
   python app.py
   ```

2. **Access the application**
   - Open your web browser and navigate to: `http://localhost:5000`
   - The application will be running on port 5000 by default

**Security Note**: Debug mode is disabled by default for security. Only enable it in development environments.

3. **Using the Application**
   - **Home Page**: Enter search terms to find medicines
   - **Search Page**: View search results with filtering options
   - **Medicine Details**: Click on any medicine to view detailed information
   - **Statistics**: View comprehensive database statistics and top manufacturers

## Dataset

This project uses a sample dataset based on the 1mg medicine dataset structure. The dataset includes:

- Medicine names
- Manufacturers
- Composition/active ingredients
- Medical uses
- Side effects
- Pack sizes
- Availability status (active/discontinued)

**Note**: For production use, you can download the complete dataset from:
[https://www.kaggle.com/datasets/prothomeshmistry/1mg-medicine-dataset](https://www.kaggle.com/datasets/prothomeshmistry/1mg-medicine-dataset)

To use the full dataset:
1. Download the dataset from Kaggle
2. Place the CSV file in the `data/` directory
3. Update the `DATA_PATH` in `app.py` to point to your dataset

## Features in Detail

### Search Functionality
- Search by medicine name, composition, or therapeutic use
- Case-insensitive search
- Real-time filtering

### Filtering Options
- Filter by manufacturer
- Filter by status (active/discontinued/all)
- Combine multiple filters

### Medicine Details
- Complete composition information
- Therapeutic uses
- Side effects (displayed as tags)
- Alternative medicines with similar composition
- Manufacturer information
- Pack size details

### Statistics Dashboard
- Total medicines count
- Number of manufacturers
- Active vs discontinued medicines
- Top 10 manufacturers by medicine count (with visual bars)

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Data Processing**: Pandas (for CSV data handling)
- **Frontend**: HTML5, CSS3
- **Styling**: Custom CSS with gradient designs and responsive layout

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

## Security Notice

⚠️ **Disclaimer**: This application is for educational and informational purposes only. Always consult with a qualified healthcare professional before taking any medication. Do not self-medicate based on this information.

## Future Enhancements

Potential improvements for future versions:
- Integration with the complete 1mg dataset
- User authentication and saved searches
- Medicine comparison feature
- Drug interaction checker
- Pharmacy locator
- Price comparison
- Prescription upload and analysis
- API endpoints for mobile applications

## License

This project is created for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue in the repository.

## Acknowledgments

- Dataset source: 1mg Medicine Dataset on Kaggle
- Built with Flask and Python
- Inspired by the need for accessible medicine information
