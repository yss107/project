from django.db import models
from django.utils import timezone


class SatelliteImage(models.Model):
    """Model for storing satellite image metadata from Major-TOM/Core-AlphaEarth-Embeddings"""
    
    # Image identifiers
    image_id = models.CharField(max_length=255, unique=True, help_text="Unique identifier for the image")
    grid_cell = models.CharField(max_length=50, blank=True, null=True, help_text="Grid cell location")
    
    # Temporal information
    timestamp = models.DateTimeField(help_text="Timestamp of the image capture")
    
    # Spatial information
    latitude = models.FloatField(blank=True, null=True, help_text="Latitude coordinate")
    longitude = models.FloatField(blank=True, null=True, help_text="Longitude coordinate")
    
    # Image properties
    cloud_cover = models.FloatField(blank=True, null=True, help_text="Cloud cover percentage")
    spatial_resolution = models.FloatField(blank=True, null=True, help_text="Spatial resolution in meters")
    
    # Dataset metadata
    dataset_split = models.CharField(max_length=20, choices=[
        ('train', 'Training'),
        ('validation', 'Validation'),
        ('test', 'Test'),
    ], default='train')
    
    # Embeddings (stored as comma-separated values)
    embedding_vector = models.TextField(blank=True, null=True, help_text="Embedding vector as comma-separated values")
    
    # Administrative fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['image_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['grid_cell']),
        ]
    
    def __str__(self):
        return f"{self.image_id} - {self.timestamp}"


class RemoteSensingAnalysis(models.Model):
    """Model for storing analysis results of satellite images"""
    
    satellite_image = models.ForeignKey(
        SatelliteImage, 
        on_delete=models.CASCADE,
        related_name='analyses'
    )
    
    # Analysis type
    analysis_type = models.CharField(max_length=100, help_text="Type of analysis performed")
    
    # Analysis results
    result_data = models.JSONField(help_text="Analysis results in JSON format")
    confidence_score = models.FloatField(blank=True, null=True, help_text="Confidence score of the analysis")
    
    # Administrative fields
    performed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the analysis")
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name_plural = "Remote Sensing Analyses"
    
    def __str__(self):
        return f"{self.analysis_type} - {self.satellite_image.image_id}"
