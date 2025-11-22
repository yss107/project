"""
Utility functions for working with the Major-TOM/Core-AlphaEarth-Embeddings dataset
"""
from datasets import load_dataset
from typing import Dict, Any, Optional


def load_dataset_info() -> Dict[str, Any]:
    """
    Load information about the Major-TOM/Core-AlphaEarth-Embeddings dataset
    
    Returns:
        Dictionary containing dataset information
    """
    try:
        # Load dataset info without downloading the entire dataset
        dataset_name = "Major-TOM/Core-AlphaEarth-Embeddings"
        
        info = {
            'name': dataset_name,
            'description': 'Core-AlphaEarth-Embeddings dataset for remote sensing applications',
            'status': 'Available',
            'url': f'https://huggingface.co/datasets/{dataset_name}',
        }
        
        return info
    except Exception as e:
        return {
            'name': 'Major-TOM/Core-AlphaEarth-Embeddings',
            'status': 'Error',
            'error': str(e),
        }


def load_dataset_sample(split: str = 'train', num_samples: int = 10):
    """
    Load a sample of the dataset
    
    Args:
        split: Dataset split to load (train, validation, test)
        num_samples: Number of samples to load
    
    Returns:
        Dataset sample
    """
    try:
        dataset_name = "Major-TOM/Core-AlphaEarth-Embeddings"
        dataset = load_dataset(
            dataset_name,
            split=split,
            streaming=True,  # Use streaming to avoid downloading entire dataset
        )
        
        # Get first num_samples
        samples = []
        for i, sample in enumerate(dataset):
            if i >= num_samples:
                break
            samples.append(sample)
        
        return samples
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading dataset sample: {e}")
        return []


def process_embedding(embedding_data) -> str:
    """
    Process embedding data for storage
    
    Args:
        embedding_data: Raw embedding data
    
    Returns:
        Comma-separated string of embedding values
    """
    if isinstance(embedding_data, (list, tuple)):
        return ','.join(map(str, embedding_data))
    return str(embedding_data)


def parse_embedding(embedding_str: Optional[str]) -> Optional[list]:
    """
    Parse stored embedding string back to list
    
    Args:
        embedding_str: Comma-separated embedding string
    
    Returns:
        List of embedding values
    """
    if not embedding_str:
        return None
    
    try:
        return [float(x) for x in embedding_str.split(',')]
    except (ValueError, AttributeError):
        return None
