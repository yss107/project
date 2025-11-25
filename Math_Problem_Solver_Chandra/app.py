#!/usr/bin/env python3
"""
Math Problem Solver using Hugging Face Chandra Model
Real-time image capture, OCR text extraction, and math problem solving
"""

import os
import io
import re
import base64
from typing import Optional, Dict, Any
from datetime import datetime

import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Try to import transformers for HuggingFace model
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None


# ============================================================================
# Configuration
# ============================================================================

MODEL_ID = os.getenv("MODEL_ID", "datalab-to/chandra")
if TRANSFORMERS_AVAILABLE and torch is not None:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
else:
    DEVICE = "cpu"


# ============================================================================
# Pydantic Models
# ============================================================================

class MathProblemRequest(BaseModel):
    """Request model for math problem solving"""
    problem_text: str = Field(..., description="The math problem text to solve")


class MathProblemResponse(BaseModel):
    """Response model for math problem solving"""
    original_problem: str
    extracted_text: Optional[str] = None
    solution: str
    processing_time: float
    timestamp: str
    model_used: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    ocr_available: bool
    device: str
    timestamp: str


class ImageProcessResponse(BaseModel):
    """Response for image processing"""
    extracted_text: str
    solution: str
    processing_time: float
    timestamp: str


# ============================================================================
# Math Solver Class
# ============================================================================

class MathProblemSolver:
    """
    Math Problem Solver using Hugging Face Chandra model
    Supports OCR text extraction and LLM-based math problem solving
    """
    
    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self.device = DEVICE
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self.ocr_reader = None
        self._setup_ocr()
        self._setup_model()
    
    def _setup_ocr(self):
        """Initialize OCR engine"""
        if EASYOCR_AVAILABLE:
            try:
                # Initialize EasyOCR with English
                self.ocr_reader = easyocr.Reader(['en'], gpu=self.device == 'cuda')
                print("✅ EasyOCR initialized successfully")
            except Exception as e:
                print(f"⚠️ EasyOCR initialization failed: {e}")
                self.ocr_reader = None
        elif PYTESSERACT_AVAILABLE:
            print("✅ PyTesseract available for OCR")
        else:
            print("⚠️ No OCR library available. Install easyocr or pytesseract")
    
    def _setup_model(self):
        """Initialize the Hugging Face model"""
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️ Transformers library not available")
            return
        
        try:
            print(f"🔄 Loading model: {self.model_id}")
            
            # Try to load the model - if it fails, use a fallback approach
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                    device_map='auto' if self.device == 'cuda' else None,
                    trust_remote_code=True
                )
                print(f"✅ Model loaded on {self.device}")
            except Exception as e:
                print(f"⚠️ Could not load model from HuggingFace: {e}")
                print("📝 Using mathematical expression parser as fallback")
                self.model = None
                self.tokenizer = None
                
        except Exception as e:
            print(f"❌ Model initialization failed: {e}")
            self.model = None
            self.tokenizer = None
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        if self.ocr_reader:
            # Use EasyOCR
            img_array = np.array(image)
            results = self.ocr_reader.readtext(img_array)
            text = ' '.join([result[1] for result in results])
            return text.strip()
        elif PYTESSERACT_AVAILABLE:
            # Use PyTesseract
            text = pytesseract.image_to_string(image)
            return text.strip()
        else:
            raise ValueError("No OCR engine available")
    
    def solve_math_problem(self, problem_text: str) -> str:
        """Solve a math problem using the loaded model or fallback parser"""
        if not problem_text or not problem_text.strip():
            return "No problem text provided"
        
        # Clean the input
        problem_text = problem_text.strip()
        
        # If model is available, use it
        if self.model and self.tokenizer:
            try:
                # Create a math-solving prompt
                prompt = f"""Solve the following math problem step by step:

Problem: {problem_text}

Solution:"""
                
                inputs = self.tokenizer(prompt, return_tensors="pt")
                if self.device == 'cuda':
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=512,
                        temperature=0.1,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Extract only the solution part
                if "Solution:" in response:
                    solution = response.split("Solution:")[-1].strip()
                else:
                    solution = response[len(prompt):].strip()
                
                return solution if solution else "Could not generate solution"
                
            except Exception as e:
                print(f"Model inference error: {e}")
                return self._fallback_solve(problem_text)
        else:
            return self._fallback_solve(problem_text)
    
    def _fallback_solve(self, problem_text: str) -> str:
        """Fallback mathematical expression solver"""
        try:
            # Clean and extract mathematical expression
            expr = self._clean_expression(problem_text)
            
            if not expr:
                return f"Could not parse mathematical expression from: {problem_text}"
            
            # Safe evaluation of mathematical expressions
            result = self._safe_eval(expr)
            
            if result is not None:
                return f"Expression: {expr}\nResult: {result}"
            else:
                return f"Could not evaluate: {expr}"
                
        except Exception as e:
            return f"Error solving problem: {str(e)}"
    
    def _clean_expression(self, text: str) -> str:
        """Clean and extract mathematical expression from text"""
        # Remove common words
        text = text.lower()
        text = re.sub(r'\b(what|is|solve|calculate|find|the|answer|to|of|equals?)\b', '', text)
        
        # Replace common math words with symbols
        replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiplied by': '*',
            'divided by': '/',
            'over': '/',
            'squared': '**2',
            'cubed': '**3',
            'power': '**',
            'x': '*',  # Common multiplication symbol
        }
        
        for word, symbol in replacements.items():
            text = text.replace(word, symbol)
        
        # Keep only valid math characters
        text = re.sub(r'[^0-9+\-*/().^**\s]', '', text)
        text = text.replace('^', '**')  # Convert ^ to **
        
        # Clean up spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _safe_eval(self, expr: str) -> Optional[float]:
        """Safely evaluate a mathematical expression"""
        try:
            # Only allow safe characters
            if not re.match(r'^[0-9+\-*/().** ]+$', expr):
                return None
            
            # Use Python's eval with restricted globals
            allowed_names = {"__builtins__": {}}
            result = eval(expr, allowed_names, {})
            
            if isinstance(result, (int, float, complex)):
                return result
            return None
            
        except Exception:
            return None
    
    def process_image(self, image: Image.Image) -> Dict[str, Any]:
        """Process image: extract text and solve math problem"""
        import time
        start_time = time.time()
        
        # Extract text from image
        extracted_text = self.extract_text_from_image(image)
        
        # Solve the math problem
        solution = self.solve_math_problem(extracted_text)
        
        processing_time = time.time() - start_time
        
        return {
            "extracted_text": extracted_text,
            "solution": solution,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Math Problem Solver API",
    description="Real-time math problem solver using Hugging Face Chandra model with OCR",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global solver instance
solver: Optional[MathProblemSolver] = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the solver on startup"""
    global solver
    print("🚀 Initializing Math Problem Solver...")
    solver = MathProblemSolver()
    print("✅ API ready!")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Math Problem Solver - Real-time OCR</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.98);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            
            h1 {
                color: #2d3748;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-align: center;
            }
            
            .subtitle {
                text-align: center;
                color: #718096;
                margin-bottom: 30px;
            }
            
            .section {
                margin: 25px 0;
                padding: 25px;
                background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                border: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            h2 {
                color: #4a5568;
                font-size: 1.4em;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .camera-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }
            
            #video {
                width: 100%;
                max-width: 640px;
                height: auto;
                border-radius: 10px;
                background: #000;
                border: 3px solid #667eea;
            }
            
            #canvas {
                display: none;
            }
            
            #capturedImage {
                width: 100%;
                max-width: 640px;
                height: auto;
                border-radius: 10px;
                border: 3px solid #48bb78;
                display: none;
            }
            
            .button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 28px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                margin: 8px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            .button:disabled {
                background: linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%);
                cursor: not-allowed;
                transform: none;
            }
            
            .button.success {
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            }
            
            .button.danger {
                background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
            }
            
            .output {
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                min-height: 100px;
                border-left: 5px solid #667eea;
            }
            
            .extracted-text {
                font-size: 18px;
                color: #2d3748;
                margin: 10px 0;
                padding: 15px;
                background: #fff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
            
            .solution {
                font-size: 20px;
                color: #2d3748;
                margin: 10px 0;
                padding: 20px;
                background: linear-gradient(135deg, #e6fffa 0%, #c6f6d5 100%);
                border-radius: 8px;
                border: 2px solid #38a169;
                font-weight: 600;
            }
            
            .status {
                padding: 10px 15px;
                border-radius: 8px;
                margin: 10px 0;
                font-weight: 500;
            }
            
            .status.success {
                background: #c6f6d5;
                color: #276749;
            }
            
            .status.error {
                background: #fed7d7;
                color: #c53030;
            }
            
            .status.processing {
                background: #bee3f8;
                color: #2b6cb0;
            }
            
            .file-upload {
                width: 100%;
                padding: 30px;
                border: 2px dashed #667eea;
                border-radius: 10px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(102, 126, 234, 0.05);
            }
            
            .file-upload:hover {
                border-color: #764ba2;
                background: rgba(118, 75, 162, 0.08);
            }
            
            .file-upload input {
                display: none;
            }
            
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                min-height: 100px;
                resize: vertical;
                font-family: inherit;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .tabs {
                display: flex;
                border-bottom: 2px solid #e2e8f0;
                margin-bottom: 20px;
            }
            
            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 16px;
                font-weight: 600;
                color: #718096;
                border-bottom: 3px solid transparent;
                margin-bottom: -2px;
                transition: all 0.3s ease;
            }
            
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .info-box {
                background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
                padding: 15px 20px;
                border-radius: 10px;
                margin: 15px 0;
                border-left: 4px solid #3182ce;
            }
            
            .info-box p {
                margin: 5px 0;
                color: #2c5282;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 20px;
                }
                
                h1 {
                    font-size: 1.8em;
                }
                
                .button {
                    width: 100%;
                    margin: 5px 0;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧮 Math Problem Solver</h1>
            <p class="subtitle">Powered by Hugging Face Chandra Model with Real-time OCR</p>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('camera')">📷 Camera</button>
                <button class="tab" onclick="switchTab('upload')">📁 Upload Image</button>
                <button class="tab" onclick="switchTab('text')">✏️ Type Problem</button>
            </div>
            
            <!-- Camera Tab -->
            <div id="cameraTab" class="tab-content active">
                <div class="section">
                    <h2>📷 Real-time Camera Capture</h2>
                    <div class="camera-container">
                        <video id="video" autoplay playsinline></video>
                        <canvas id="canvas"></canvas>
                        <img id="capturedImage" alt="Captured image">
                        
                        <div>
                            <button class="button" id="startCamera" onclick="startCamera()">🎥 Start Camera</button>
                            <button class="button success" id="captureBtn" onclick="captureImage()" disabled>📸 Capture & Solve</button>
                            <button class="button danger" id="stopCamera" onclick="stopCamera()" disabled>⏹️ Stop Camera</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Upload Tab -->
            <div id="uploadTab" class="tab-content">
                <div class="section">
                    <h2>📁 Upload Image</h2>
                    <label class="file-upload">
                        <input type="file" id="imageFile" accept="image/*" onchange="handleFileUpload()">
                        <p>📷 Click to upload or drag and drop</p>
                        <p style="color: #718096; font-size: 14px;">Supports: JPG, PNG, GIF, BMP</p>
                    </label>
                    <img id="uploadedImage" style="display: none; max-width: 100%; margin-top: 15px; border-radius: 10px;">
                </div>
            </div>
            
            <!-- Text Tab -->
            <div id="textTab" class="tab-content">
                <div class="section">
                    <h2>✏️ Type Math Problem</h2>
                    <textarea id="problemText" placeholder="Enter your math problem here...&#10;Examples:&#10;- 2 + 2&#10;- 15 * 7 - 23&#10;- What is 144 divided by 12?&#10;- Calculate 25 squared"></textarea>
                    <button class="button" onclick="solveTextProblem()">🧮 Solve Problem</button>
                </div>
            </div>
            
            <!-- Results Section -->
            <div class="section">
                <h2>📊 Results</h2>
                <div id="status"></div>
                
                <div id="results" style="display: none;">
                    <div class="output">
                        <h3 style="color: #667eea; margin-bottom: 10px;">📝 Extracted Text:</h3>
                        <div id="extractedText" class="extracted-text"></div>
                    </div>
                    
                    <div class="output">
                        <h3 style="color: #38a169; margin-bottom: 10px;">✅ Solution:</h3>
                        <div id="solution" class="solution"></div>
                    </div>
                    
                    <p style="color: #718096; font-size: 14px; margin-top: 10px;">
                        ⏱️ Processing time: <span id="processingTime">-</span>
                    </p>
                </div>
            </div>
            
            <!-- Info Box -->
            <div class="info-box">
                <p><strong>📌 Tips for best results:</strong></p>
                <p>• Write math problems clearly with good lighting</p>
                <p>• Use clear handwriting or printed text</p>
                <p>• Keep the camera steady while capturing</p>
                <p>• Supported operations: +, -, *, /, ^, parentheses</p>
            </div>
        </div>
        
        <script>
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let capturedImage = document.getElementById('capturedImage');
            let stream = null;
            
            function switchTab(tab) {
                // Update tab buttons
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
                
                // Update tab content
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById(tab + 'Tab').classList.add('active');
            }
            
            async function startCamera() {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { facingMode: 'environment', width: 1280, height: 720 } 
                    });
                    video.srcObject = stream;
                    video.style.display = 'block';
                    capturedImage.style.display = 'none';
                    
                    document.getElementById('startCamera').disabled = true;
                    document.getElementById('captureBtn').disabled = false;
                    document.getElementById('stopCamera').disabled = false;
                    
                    showStatus('Camera started successfully!', 'success');
                } catch (error) {
                    console.error('Error accessing camera:', error);
                    showStatus('Error accessing camera. Please check permissions.', 'error');
                }
            }
            
            function stopCamera() {
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                    stream = null;
                    video.srcObject = null;
                }
                
                document.getElementById('startCamera').disabled = false;
                document.getElementById('captureBtn').disabled = true;
                document.getElementById('stopCamera').disabled = true;
                
                showStatus('Camera stopped.', 'success');
            }
            
            async function captureImage() {
                // Set canvas size to video size
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                // Draw video frame to canvas
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);
                
                // Get image data
                const imageData = canvas.toDataURL('image/png');
                
                // Show captured image
                capturedImage.src = imageData;
                capturedImage.style.display = 'block';
                video.style.display = 'none';
                
                // Send to API
                await processBase64Image(imageData);
                
                // Reset for next capture
                setTimeout(() => {
                    video.style.display = 'block';
                    capturedImage.style.display = 'none';
                }, 3000);
            }
            
            async function handleFileUpload() {
                const fileInput = document.getElementById('imageFile');
                const file = fileInput.files[0];
                
                if (!file) return;
                
                // Show preview
                const reader = new FileReader();
                reader.onload = async (e) => {
                    const uploadedImage = document.getElementById('uploadedImage');
                    uploadedImage.src = e.target.result;
                    uploadedImage.style.display = 'block';
                    
                    await processBase64Image(e.target.result);
                };
                reader.readAsDataURL(file);
            }
            
            async function processBase64Image(imageData) {
                showStatus('<div class="loading"></div> Processing image...', 'processing');
                
                try {
                    // Convert base64 to blob
                    const base64Data = imageData.split(',')[1];
                    const blob = base64ToBlob(base64Data, 'image/png');
                    
                    // Create form data
                    const formData = new FormData();
                    formData.append('file', blob, 'captured.png');
                    
                    // Send to API
                    const response = await fetch('/process-image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error('Server error');
                    }
                    
                    const data = await response.json();
                    displayResults(data);
                    
                } catch (error) {
                    console.error('Error processing image:', error);
                    showStatus('Error processing image. Please try again.', 'error');
                }
            }
            
            async function solveTextProblem() {
                const problemText = document.getElementById('problemText').value.trim();
                
                if (!problemText) {
                    showStatus('Please enter a math problem.', 'error');
                    return;
                }
                
                showStatus('<div class="loading"></div> Solving problem...', 'processing');
                
                try {
                    const response = await fetch('/solve', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ problem_text: problemText })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Server error');
                    }
                    
                    const data = await response.json();
                    displayResults({
                        extracted_text: data.original_problem,
                        solution: data.solution,
                        processing_time: data.processing_time
                    });
                    
                } catch (error) {
                    console.error('Error solving problem:', error);
                    showStatus('Error solving problem. Please try again.', 'error');
                }
            }
            
            function displayResults(data) {
                document.getElementById('results').style.display = 'block';
                document.getElementById('extractedText').textContent = data.extracted_text || 'No text extracted';
                document.getElementById('solution').textContent = data.solution || 'No solution';
                document.getElementById('processingTime').textContent = data.processing_time.toFixed(3) + 's';
                
                showStatus('Problem solved successfully!', 'success');
            }
            
            function showStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function base64ToBlob(base64, mimeType) {
                const byteCharacters = atob(base64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: mimeType });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if solver else "initializing",
        model_loaded=solver.model is not None if solver else False,
        ocr_available=solver.ocr_reader is not None if solver else False,
        device=DEVICE,
        timestamp=datetime.now().isoformat()
    )


@app.post("/solve", response_model=MathProblemResponse)
async def solve_problem(request: MathProblemRequest):
    """Solve a math problem from text"""
    if not solver:
        raise HTTPException(status_code=503, detail="Solver not initialized")
    
    import time
    start_time = time.time()
    
    solution = solver.solve_math_problem(request.problem_text)
    
    processing_time = time.time() - start_time
    
    return MathProblemResponse(
        original_problem=request.problem_text,
        extracted_text=None,
        solution=solution,
        processing_time=processing_time,
        timestamp=datetime.now().isoformat(),
        model_used=MODEL_ID
    )


@app.post("/process-image", response_model=ImageProcessResponse)
async def process_image(file: UploadFile = File(...)):
    """Process an image: extract text and solve math problem"""
    if not solver:
        raise HTTPException(status_code=503, detail="Solver not initialized")
    
    try:
        # Read image file
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process the image
        result = solver.process_image(image)
        
        return ImageProcessResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main
# ============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server"""
    print(f"\n{'='*80}")
    print(f"🧮 Starting Math Problem Solver API Server")
    print(f"{'='*80}\n")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🌐 Web UI: http://{host}:{port}")
    print(f"\n{'='*80}\n")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
