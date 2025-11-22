"""
Management command to create sample satellite image data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from sensing.models import SatelliteImage, RemoteSensingAnalysis
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Creates sample satellite image data for demonstration purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sample images to create (default: 20)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {count} sample satellite images...'))
        
        grid_cells = ['A1B2', 'C3D4', 'E5F6', 'G7H8', 'I9J0', 'K1L2', 'M3N4', 'O5P6']
        splits = ['train', 'validation', 'test']
        analysis_types = [
            'Land Cover Classification',
            'Change Detection',
            'Object Detection',
            'Vegetation Index',
            'Water Body Detection'
        ]
        
        created_count = 0
        base_time = timezone.now() - timedelta(days=365)
        
        for i in range(count):
            # Generate sample data
            image_id = f'IMG_{i+1:05d}_{random.randint(1000, 9999)}'
            grid_cell = random.choice(grid_cells)
            timestamp = base_time + timedelta(days=random.randint(0, 365))
            
            # Random coordinates (sample locations around the world)
            latitude = random.uniform(-60, 60)
            longitude = random.uniform(-180, 180)
            
            cloud_cover = round(random.uniform(0, 100), 2)
            spatial_resolution = random.choice([10.0, 20.0, 30.0])
            dataset_split = random.choice(splits)
            
            # Generate sample embedding (simulated)
            embedding = ','.join([str(round(random.uniform(-1, 1), 4)) for _ in range(128)])
            
            # Create the satellite image
            try:
                image = SatelliteImage.objects.create(
                    image_id=image_id,
                    grid_cell=grid_cell,
                    timestamp=timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    cloud_cover=cloud_cover,
                    spatial_resolution=spatial_resolution,
                    dataset_split=dataset_split,
                    embedding_vector=embedding
                )
                created_count += 1
                
                # Create 0-3 random analyses for some images
                num_analyses = random.randint(0, 3)
                for j in range(num_analyses):
                    analysis_type = random.choice(analysis_types)
                    confidence = round(random.uniform(0.5, 1.0), 2)
                    
                    # Generate sample result data
                    result_data = {
                        'detected_classes': random.randint(1, 10),
                        'accuracy': round(random.uniform(0.7, 0.99), 2),
                        'processing_time': f'{random.uniform(0.5, 5.0):.2f}s'
                    }
                    
                    RemoteSensingAnalysis.objects.create(
                        satellite_image=image,
                        analysis_type=analysis_type,
                        result_data=result_data,
                        confidence_score=confidence,
                        notes=f'Automated {analysis_type.lower()} analysis'
                    )
                
                if (i + 1) % 5 == 0:
                    self.stdout.write(f'  Created {i + 1}/{count} images...')
                    
            except (ValueError, TypeError, KeyError) as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating image {image_id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} satellite images with their analyses!'
            )
        )
        
        # Display summary
        total_images = SatelliteImage.objects.count()
        total_analyses = RemoteSensingAnalysis.objects.count()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Total images in database: {total_images}')
        self.stdout.write(f'  Total analyses in database: {total_analyses}')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                'You can now view the data at http://127.0.0.1:8000/ or manage it via /admin/'
            )
        )
