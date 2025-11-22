from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from .models import SatelliteImage, RemoteSensingAnalysis
from .utils import load_dataset_info


def index(request):
    """Home page view"""
    context = {
        'total_images': SatelliteImage.objects.count(),
        'total_analyses': RemoteSensingAnalysis.objects.count(),
        'recent_images': SatelliteImage.objects.all()[:5],
    }
    return render(request, 'sensing/index.html', context)


class SatelliteImageListView(ListView):
    """List view for satellite images"""
    model = SatelliteImage
    template_name = 'sensing/image_list.html'
    context_object_name = 'images'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by dataset split
        split = self.request.GET.get('split')
        if split:
            queryset = queryset.filter(dataset_split=split)
        
        # Filter by grid cell
        grid_cell = self.request.GET.get('grid_cell')
        if grid_cell:
            queryset = queryset.filter(grid_cell=grid_cell)
        
        return queryset


class SatelliteImageDetailView(DetailView):
    """Detail view for a single satellite image"""
    model = SatelliteImage
    template_name = 'sensing/image_detail.html'
    context_object_name = 'image'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['analyses'] = self.object.analyses.all()
        return context


def dataset_info(request):
    """View to display dataset information"""
    try:
        info = load_dataset_info()
        context = {
            'dataset_info': info,
        }
    except Exception as e:
        messages.error(request, f"Error loading dataset info: {str(e)}")
        context = {}
    
    return render(request, 'sensing/dataset_info.html', context)


def about(request):
    """About page view"""
    return render(request, 'sensing/about.html')
