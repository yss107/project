# 🧮 Math Problem Solver with Real-time OCR

A web-based math problem solver that uses the [Hugging Face Chandra Model](https://huggingface.co/datalab-to/chandra) for solving mathematical problems. Features real-time camera capture, OCR text extraction, and AI-powered problem solving.

## ✨ Features

- **📷 Real-time Camera Capture**: Use your device camera to capture math problems
- **📁 Image Upload**: Upload images containing math problems
- **✏️ Text Input**: Type math problems directly
- **🔍 OCR Text Extraction**: Automatic text extraction using EasyOCR or Tesseract
- **🤖 AI-Powered Solutions**: Uses the Hugging Face Chandra model for solving problems
- **🌐 Web Interface**: Beautiful, responsive web UI
- **📱 Mobile Friendly**: Works on desktop and mobile devices
- **⚡ Real-time Processing**: Fast, real-time problem solving

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Web Browser                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │
│  │ Camera   │  │ Upload   │  │ Text Input   │       │
│  │ Capture  │  │ Image    │  │              │       │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘       │
│       │             │               │                │
│       └─────────────┴───────────────┘                │
│                     │                                 │
└─────────────────────┼─────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌──────────────────────────────────────────────────────┐
│                  FastAPI Server                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Math Problem Solver                 │ │
│  │  ┌───────────┐     ┌───────────────────────┐   │ │
│  │  │  EasyOCR  │ ──▶ │  HuggingFace Chandra  │   │ │
│  │  │ Tesseract │     │     Model / Fallback   │   │ │
│  │  └───────────┘     └───────────────────────┘   │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Camera access (for real-time capture)

### Installation

1. **Clone the repository**:
   ```bash
   cd Math_Problem_Solver_Chandra
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install OCR dependencies** (choose one):
   
   **Option A - EasyOCR (Recommended)**:
   ```bash
   pip install easyocr
   ```
   
   **Option B - Tesseract**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   
   pip install pytesseract
   ```

### Running the Application

```bash
python app.py
```

The server will start at `http://localhost:8000`

### Using the Web Interface

1. Open `http://localhost:8000` in your browser
2. Choose one of the input methods:
   - **Camera**: Click "Start Camera", capture the math problem, and click "Capture & Solve"
   - **Upload**: Upload an image containing a math problem
   - **Text**: Type the math problem directly
3. View the extracted text and solution

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/solve` | POST | Solve text-based math problem |
| `/process-image` | POST | Process image and solve math problem |
| `/docs` | GET | Interactive API documentation (Swagger) |

### Examples

**Solve a text problem**:
```bash
curl -X POST "http://localhost:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{"problem_text": "What is 25 * 4 + 10?"}'
```

**Process an image**:
```bash
curl -X POST "http://localhost:8000/process-image" \
  -F "file=@math_problem.png"
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_ID` | `datalab-to/chandra` | Hugging Face model ID |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

### Example `.env` file

```env
MODEL_ID=datalab-to/chandra
HOST=0.0.0.0
PORT=8000
```

## 📊 Supported Math Operations

### Basic Operations
- **Arithmetic**: `+`, `-`, `*`, `/`, `%` (modulo)
- **Exponents**: `^`, `**`, `squared`, `cubed`
- **Factorial**: `!` (e.g., `5!` = 120)
- **Parentheses**: `(`, `)`

### Mathematical Functions
- **Roots**: `sqrt()`, `cbrt()` (cube root)
- **Trigonometry**: `sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()`
- **Hyperbolic**: `sinh()`, `cosh()`, `tanh()`, `asinh()`, `acosh()`, `atanh()`
- **Logarithms**: `log()` (base 10), `ln()` (natural), `log2()`
- **Other**: `abs()`, `ceil()`, `floor()`, `round()`, `exp()`

### Constants
- `pi` (π = 3.14159...)
- `e` (Euler's number = 2.71828...)
- `tau` (τ = 2π)

### Complex Problems
- **Quadratic Equations**: `ax² + bx + c = 0` (with step-by-step solutions)
- **Percentages**: `25% of 200`
- **Ratios**: `ratio 3:4`

### Example Problems

```
# Basic
2 + 2
15 * 7 - 23
5! + 3!

# Functions
sqrt(144) + 5^2
sin(pi/2) + cos(0)
log(100) * ln(e)

# Complex
x^2 - 5x + 6 = 0
25% of 200
```

## 🖼️ Screenshots

### Web Interface
The application features a modern, responsive web interface with:
- Tab-based navigation (Camera, Upload, Text)
- Real-time camera preview
- Beautiful gradient design
- Mobile-friendly layout
- Support for complex mathematical expressions

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **ML/AI**: Hugging Face Transformers, PyTorch
- **OCR**: EasyOCR, Tesseract
- **Frontend**: HTML5, CSS3, JavaScript
- **Camera**: WebRTC (getUserMedia API)

## 📝 Project Structure

```
Math_Problem_Solver_Chandra/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .env.example        # Environment variables example
└── Dockerfile          # Docker container (optional)
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t math-solver .

# Run the container
docker run -p 8000:8000 math-solver
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided for educational purposes.

## 👨‍💻 Author

**Yash Kumar**
- LinkedIn: [yash-kumar09](https://www.linkedin.com/in/yash-kumar09/)
- GitHub: [yss107](https://github.com/yss107)
- Portfolio: [yss107.github.io](https://yss107.github.io)

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for the Chandra model
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for OCR capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

---

Made with ❤️ by Yash Kumar | © 2025
