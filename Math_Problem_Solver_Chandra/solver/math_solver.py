"""
Math Problem Solver using Hugging Face Chandra Model
Real-time image capture, OCR text extraction, and math problem solving
Supports complex mathematical expressions including trigonometry, logarithms, and more
"""

import os
import re
import math
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image

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
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None


# Configuration
MODEL_ID = os.getenv("MODEL_ID", "datalab-to/chandra")
if TRANSFORMERS_AVAILABLE and torch is not None:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
else:
    DEVICE = "cpu"


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
        """Fallback mathematical expression solver with support for complex problems"""
        try:
            # First, try to solve complex problems (quadratic, systems, etc.)
            complex_result = self._solve_complex_problem(problem_text)
            if complex_result:
                return complex_result
            
            # Clean and extract mathematical expression
            expr = self._clean_expression(problem_text)
            
            if not expr:
                return f"Could not parse mathematical expression from: {problem_text}"
            
            # Safe evaluation of mathematical expressions
            result = self._safe_eval(expr)
            
            if result is not None:
                # Format result nicely
                if isinstance(result, float):
                    if result == int(result):
                        formatted_result = int(result)
                    else:
                        formatted_result = round(result, 10)
                else:
                    formatted_result = result
                return f"Expression: {expr}\nResult: {formatted_result}"
            else:
                return f"Could not evaluate: {expr}"
                
        except Exception as e:
            return f"Error solving problem: {str(e)}"
    
    def _clean_expression(self, text: str) -> str:
        """Clean and extract mathematical expression from text"""
        # Store original for complex function detection
        original_text = text.lower().strip()
        text = original_text
        
        # Remove common question words
        text = re.sub(r'\b(what|is|solve|calculate|find|the|answer|to|of|equals?|value|evaluate)\b', '', text)
        
        # Replace common math words with symbols/functions
        word_replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiplied by': '*',
            'divided by': '/',
            'over': '/',
            'squared': '**2',
            'cubed': '**3',
            'power': '**',
            'raised to': '**',
            'to the power of': '**',
            'modulo': '%',
            'mod': '%',
            'factorial': '!',
        }
        
        for word, symbol in word_replacements.items():
            text = text.replace(word, symbol)
        
        # Replace mathematical function words with function names
        function_replacements = {
            'square root': 'sqrt',
            'squareroot': 'sqrt',
            'sq root': 'sqrt',
            'cube root': 'cbrt',
            'cuberoot': 'cbrt',
            'natural log': 'ln',
            'natural logarithm': 'ln',
            'logarithm': 'log',
            'absolute value': 'abs',
            'absolute': 'abs',
            'sine': 'sin',
            'cosine': 'cos',
            'tangent': 'tan',
            'arc sine': 'asin',
            'arc cosine': 'acos',
            'arc tangent': 'atan',
            'hyperbolic sine': 'sinh',
            'hyperbolic cosine': 'cosh',
            'hyperbolic tangent': 'tanh',
            'ceiling': 'ceil',
            'floor': 'floor',
            'round': 'round',
        }
        
        for word, func in function_replacements.items():
            text = text.replace(word, func)
        
        # Convert ^ to ** 
        text = text.replace('^', '**')
        
        # Replace 'x' between numbers as multiplication (but not in function names)
        text = re.sub(r'(\d)\s*x\s*(\d)', r'\1*\2', text)
        
        # Keep valid math characters including function names
        # Allow: digits, operators, parentheses, dots, spaces, and letters for function names
        text = re.sub(r'[^0-9+\-*/().%!\s*a-z]', '', text)
        
        # Clean up spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _safe_eval(self, expr: str) -> Optional[float]:
        """Safely evaluate a mathematical expression with support for complex math functions"""
        try:
            # Validate expression - allow alphanumeric, operators, parentheses, dots, spaces
            if not re.match(r'^[0-9+\-*/().%!\s*a-zA-Z_]+$', expr):
                return None
            
            # Handle factorial notation (n!)
            def factorial_replace(match):
                num = int(match.group(1))
                return str(math.factorial(num))
            
            expr = re.sub(r'(\d+)!', factorial_replace, expr)
            
            # Define safe mathematical functions
            safe_functions = {
                # Basic math
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                
                # Powers and roots
                'sqrt': math.sqrt,
                'cbrt': lambda x: x ** (1/3) if x >= 0 else -((-x) ** (1/3)),
                'pow': pow,
                'exp': math.exp,
                
                # Logarithms
                'log': math.log10,
                'log10': math.log10,
                'log2': math.log2,
                'ln': math.log,
                
                # Trigonometric functions (radians)
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'atan2': math.atan2,
                
                # Hyperbolic functions
                'sinh': math.sinh,
                'cosh': math.cosh,
                'tanh': math.tanh,
                'asinh': math.asinh,
                'acosh': math.acosh,
                'atanh': math.atanh,
                
                # Rounding
                'ceil': math.ceil,
                'floor': math.floor,
                'trunc': math.trunc,
                
                # Trigonometric with degrees
                'sind': lambda x: math.sin(math.radians(x)),
                'cosd': lambda x: math.cos(math.radians(x)),
                'tand': lambda x: math.tan(math.radians(x)),
                
                # Conversion
                'radians': math.radians,
                'degrees': math.degrees,
                
                # Other
                'factorial': math.factorial,
                'gcd': math.gcd,
                'lcm': lambda a, b: abs(a * b) // math.gcd(a, b) if a and b else 0,
            }
            
            # Define safe constants
            safe_constants = {
                'pi': math.pi,
                'e': math.e,
                'tau': math.tau,
                'inf': math.inf,
            }
            
            # Create restricted namespace
            allowed_names = {"__builtins__": {}}
            allowed_names.update(safe_functions)
            allowed_names.update(safe_constants)
            
            result = eval(expr, allowed_names, {})
            
            if isinstance(result, (int, float, complex)):
                return result
            return None
            
        except Exception:
            return None
    
    def _solve_complex_problem(self, problem_text: str) -> str:
        """Solve complex mathematical problems with step-by-step solutions"""
        problem_text = problem_text.lower().strip()
        
        # Check for specific problem types
        
        # Quadratic equation: ax² + bx + c = 0
        quadratic_match = re.search(r'(\-?\d*)\s*x\s*[\^²2]+\s*([+\-])\s*(\d*)\s*x\s*([+\-])\s*(\d+)\s*=\s*0', problem_text)
        if quadratic_match:
            return self._solve_quadratic(quadratic_match)
        
        # System of equations detection
        if 'system' in problem_text or ('equation' in problem_text and 'and' in problem_text):
            return self._solve_system_hint(problem_text)
        
        # Derivative/calculus hints
        if 'derivative' in problem_text or 'differentiate' in problem_text:
            return self._calculus_hint(problem_text, 'derivative')
        
        if 'integral' in problem_text or 'integrate' in problem_text:
            return self._calculus_hint(problem_text, 'integral')
        
        # Percentage problems
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:of)\s*(\d+(?:\.\d+)?)', problem_text)
        if percent_match:
            percent = float(percent_match.group(1))
            value = float(percent_match.group(2))
            result = (percent / 100) * value
            return f"Calculation: {percent}% of {value}\nFormula: ({percent}/100) × {value}\nResult: {result}"
        
        # Ratio problems
        ratio_match = re.search(r'ratio.*?(\d+)\s*(?::|to)\s*(\d+)', problem_text)
        if ratio_match:
            a, b = int(ratio_match.group(1)), int(ratio_match.group(2))
            gcd = math.gcd(a, b)
            return f"Ratio: {a}:{b}\nSimplified: {a//gcd}:{b//gcd}\nAs fraction: {a}/{b} = {a/b:.4f}"
        
        # Fall back to expression evaluation
        return None
    
    def _solve_quadratic(self, match) -> str:
        """Solve quadratic equation ax² + bx + c = 0"""
        a_str = match.group(1) or '1'
        a = int(a_str) if a_str not in ['', '-'] else (1 if a_str == '' else -1)
        
        sign1 = match.group(2)
        b_str = match.group(3) or '1'
        b = int(b_str) if b_str else 1
        b = b if sign1 == '+' else -b
        
        sign2 = match.group(4)
        c = int(match.group(5))
        c = c if sign2 == '+' else -c
        
        discriminant = b**2 - 4*a*c
        
        solution = f"Quadratic Equation: {a}x² + {b}x + {c} = 0\n\n"
        solution += f"Step 1: Identify coefficients\n  a = {a}, b = {b}, c = {c}\n\n"
        solution += f"Step 2: Calculate discriminant (Δ = b² - 4ac)\n  Δ = {b}² - 4({a})({c}) = {discriminant}\n\n"
        
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            solution += f"Step 3: Two real roots (Δ > 0)\n"
            solution += f"  x₁ = (-b + √Δ) / 2a = {x1:.4f}\n"
            solution += f"  x₂ = (-b - √Δ) / 2a = {x2:.4f}"
        elif discriminant == 0:
            x = -b / (2*a)
            solution += f"Step 3: One real root (Δ = 0)\n"
            solution += f"  x = -b / 2a = {x:.4f}"
        else:
            real = -b / (2*a)
            imag = math.sqrt(-discriminant) / (2*a)
            solution += f"Step 3: Two complex roots (Δ < 0)\n"
            solution += f"  x₁ = {real:.4f} + {imag:.4f}i\n"
            solution += f"  x₂ = {real:.4f} - {imag:.4f}i"
        
        return solution
    
    def _solve_system_hint(self, problem_text: str) -> str:
        """Provide hints for solving system of equations"""
        return """System of Equations Solver:

Methods available:
1. Substitution Method: Solve one equation for a variable, substitute into the other
2. Elimination Method: Add/subtract equations to eliminate a variable
3. Matrix Method: Use Cramer's rule or matrix inversion

Example: 
  2x + 3y = 7
  x - y = 1

Using substitution: x = y + 1
  2(y+1) + 3y = 7
  5y + 2 = 7
  y = 1, x = 2

Please provide the specific equations for a complete solution."""
    
    def _calculus_hint(self, problem_text: str, calc_type: str) -> str:
        """Provide calculus hints and rules"""
        if calc_type == 'derivative':
            return """Derivative Rules:

1. Power Rule: d/dx(xⁿ) = nxⁿ⁻¹
2. Product Rule: d/dx(fg) = f'g + fg'
3. Quotient Rule: d/dx(f/g) = (f'g - fg')/g²
4. Chain Rule: d/dx(f(g(x))) = f'(g(x)) · g'(x)

Common Derivatives:
• d/dx(sin x) = cos x
• d/dx(cos x) = -sin x
• d/dx(eˣ) = eˣ
• d/dx(ln x) = 1/x

Please provide the specific function for a complete derivative."""
        else:
            return """Integration Rules:

1. Power Rule: ∫xⁿ dx = xⁿ⁺¹/(n+1) + C
2. Sum Rule: ∫(f + g) dx = ∫f dx + ∫g dx
3. Constant Multiple: ∫cf dx = c∫f dx

Common Integrals:
• ∫sin x dx = -cos x + C
• ∫cos x dx = sin x + C
• ∫eˣ dx = eˣ + C
• ∫1/x dx = ln|x| + C

Please provide the specific function for a complete integral."""
    
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
        }


# Global solver instance
_solver_instance = None

def get_solver():
    """Get or create solver instance"""
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = MathProblemSolver()
    return _solver_instance
