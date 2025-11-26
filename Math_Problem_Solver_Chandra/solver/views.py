from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from PIL import Image
import io
import json
import time
from datetime import datetime
from .math_solver import get_solver


def index(request):
    """Serve the main web interface"""
    return render(request, 'solver/index.html')


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    solver = get_solver()
    return JsonResponse({
        'status': 'healthy',
        'model_loaded': solver.model is not None,
        'ocr_available': solver.ocr_reader is not None,
        'device': solver.device,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["POST"])
def solve_problem(request):
    """Solve a math problem from text"""
    try:
        data = json.loads(request.body)
        problem_text = data.get('problem_text', '')
        
        if not problem_text:
            return JsonResponse({'error': 'No problem text provided'}, status=400)
        
        solver = get_solver()
        start_time = time.time()
        
        solution = solver.solve_math_problem(problem_text)
        processing_time = time.time() - start_time
        
        return JsonResponse({
            'original_problem': problem_text,
            'extracted_text': None,
            'solution': solution,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'model_used': solver.model_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def process_image(request):
    """Process an image: extract text and solve math problem"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        # Read image file
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process the image
        solver = get_solver()
        result = solver.process_image(image)
        result['timestamp'] = datetime.now().isoformat()
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
