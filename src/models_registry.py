"""
Models Registry - Centralized configuration for AIMLAPI image and video models.

This registry contains model configurations including endpoints, parameters,
and detection rules. Models can be added via Python dict or JSON file.
"""

# Import parameter templates for reuse
from parameter_templates import (
    IMAGE_ASPECT_RATIO_GOOGLE,
    IMAGE_RESOLUTION_GOOGLE,
    VIDEO_DURATION_STANDARD,
    VIDEO_ASPECT_RATIO_STANDARD,
    CFG_SCALE_STANDARD
)

# Base model registry (Python dict)
MODELS_REGISTRY = {
    'google/nano-banana-pro': {
        'type': 'image',
        'endpoint_type': 'standard',
        'endpoint': '/v1/images/generations',
        'method': 'POST',
        'response_type': 'immediate',
        'parameters': {
            'prompt': {
                'type': 'str',
                'required': True
            },
            'aspect_ratio': IMAGE_ASPECT_RATIO_GOOGLE,
            'resolution': IMAGE_RESOLUTION_GOOGLE,
            'num_images': {
                'type': 'int',
                'default': 1,
                'min': 1,
                'max': 4
            }
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'google/nano-banana-pro-edit': {
        'type': 'image',
        'endpoint_type': 'standard',
        'endpoint': '/v1/images/generations',
        'method': 'POST',
        'response_type': 'immediate',
        'parameters': {
            'prompt': {
                'type': 'str',
                'required': True
            },
            'image_urls': {
                'type': 'list',
                'required': True,
                'max_items': 14
            },
            'aspect_ratio': IMAGE_ASPECT_RATIO_GOOGLE,
            'resolution': IMAGE_RESOLUTION_GOOGLE,
            'num_images': {
                'type': 'int',
                'default': 1,
                'min': 1,
                'max': 4
            }
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'klingai/v2.5-turbo/pro/text-to-video': {
        'type': 'video',
        'endpoint_type': 'standard',
        'endpoint': '/v2/video/generations',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/video/generations',
        'poll_method': 'GET',
        'poll_interval': 10,
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'klingai/v2.5-turbo/pro/text-to-video',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'klingai/v2.5-turbo/pro/image-to-video': {
        'type': 'video',
        'endpoint_type': 'standard',
        'endpoint': '/v2/video/generations',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/video/generations',
        'poll_method': 'GET',
        'poll_interval': 10,
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'klingai/v2.5-turbo/pro/image-to-video',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'image_url': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    }
}

def get_model_config(model_id):
    """
    Get configuration for a specific model.
    
    Args:
        model_id (str): Model identifier (e.g., 'google/nano-banana-pro')
        
    Returns:
        dict: Model configuration, or None if not found
    """
    return MODELS_REGISTRY.get(model_id)

def get_models_by_type(media_type):
    """
    Get all models of a specific type.
    
    Args:
        media_type (str): 'image' or 'video'
        
    Returns:
        dict: Dictionary of model_id -> config for matching models
    """
    return {k: v for k, v in MODELS_REGISTRY.items() if v.get('type') == media_type}

def get_models_by_detection(requires_reference):
    """
    Get all models that require (or don't require) reference images.
    
    Args:
        requires_reference (bool): True for models requiring reference, False otherwise
        
    Returns:
        dict: Dictionary of model_id -> config for matching models
    """
    result = {}
    for model_id, config in MODELS_REGISTRY.items():
        detection = config.get('detection', {})
        if detection.get('requires_reference') == requires_reference:
            result[model_id] = config
    return result

def load_registry_from_json(json_path='models_registry.json'):
    """
    Load model configurations from JSON file and merge with existing registry.
    
    Args:
        json_path (str): Path to JSON file (relative to src/ directory)
        
    Returns:
        dict: Merged registry
    """
    import json
    import os
    
    # Try to find the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)
    
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r') as f:
                json_registry = json.load(f)
            
            # Merge with existing registry (JSON takes precedence)
            merged = MODELS_REGISTRY.copy()
            merged.update(json_registry)
            return merged
        except Exception as e:
            print(f"Error loading JSON registry: {e}")
            return MODELS_REGISTRY
    else:
        # Return existing registry if JSON doesn't exist
        return MODELS_REGISTRY

def get_registry():
    """
    Get the complete model registry, loading from JSON if available.
    
    Returns:
        dict: Complete model registry
    """
    return load_registry_from_json()

