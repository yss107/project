from django.contrib import admin
from .models import SatelliteImage, RemoteSensingAnalysis


@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    list_display = ['image_id', 'timestamp', 'grid_cell', 'cloud_cover', 'dataset_split', 'created_at']
    list_filter = ['dataset_split', 'timestamp']
    search_fields = ['image_id', 'grid_cell']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'timestamp'


@admin.register(RemoteSensingAnalysis)
class RemoteSensingAnalysisAdmin(admin.ModelAdmin):
    list_display = ['satellite_image', 'analysis_type', 'confidence_score', 'performed_at']
    list_filter = ['analysis_type', 'performed_at']
    search_fields = ['satellite_image__image_id', 'analysis_type']
    readonly_fields = ['performed_at']
