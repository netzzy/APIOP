"""
Parameter Templates - Reusable parameter schema definitions for media generation models.

These templates can be referenced in model configurations to avoid duplication.
"""

# Video parameter templates
VIDEO_DURATION_STANDARD = {
    'type': 'menu',
    'options': ['5', '10'],
    'default': '5',
    'api_type': 'str',  # Most APIs expect string enum values
    'help_text': 'Video duration in seconds (default: 5)'
}

VIDEO_DURATION_MINIMAX = {
    'type': 'menu',
    'options': ['6', '10'],
    'default': '6',
    'api_type': 'str',  # Most APIs expect string enum values
    'help_text': 'Video duration in seconds (default: 6)'
}

VIDEO_DURATION_LTXV = {
    'type': 'menu',
    'options': ['6', '8', '10'],
    'default': '6',
    'api_type': 'int',  # Ltxv API expects integer, not string
    'help_text': 'Video duration in seconds (default: 6)'
}

VIDEO_ASPECT_RATIO_STANDARD = {
    'type': 'menu',
    'options': ['16:9', '9:16', '1:1'],
    'default': '16:9',
    'api_type': 'str',  # API expects string enum values
    'help_text': 'Video aspect ratio (default: 16:9)'
}

# Image parameter templates
IMAGE_ASPECT_RATIO_GOOGLE = {
    'type': 'menu',
    'options': ['21:9', '1:1', '4:3', '3:2', '2:3', '5:4', '4:5', '3:4', '16:9', '9:16'],
    'default': '1:1',
    'help_text': 'Image aspect ratio (default: 1:1)'
}

IMAGE_RESOLUTION_GOOGLE = {
    'type': 'menu',
    'options': ['1K', '2K', '4K'],
    'default': '1K',
    'help_text': 'Image resolution (default: 1K)'
}

# Common parameter templates
CFG_SCALE_STANDARD = {
    'type': 'float',
    'default': 0.9,
    'min': 0.0,
    'max': 1.0,
    'api_type': 'float',  # API expects float
    'help_text': 'Classifier Free Guidance scale (0-1, default: 0.9)'
}

# Dictionary for easy lookup
PARAMETER_TEMPLATES = {
    'video_duration_standard': VIDEO_DURATION_STANDARD,
    'video_duration_minimax': VIDEO_DURATION_MINIMAX,
    'video_duration_ltxv': VIDEO_DURATION_LTXV,
    'video_aspect_ratio_standard': VIDEO_ASPECT_RATIO_STANDARD,
    'image_aspect_ratio_google': IMAGE_ASPECT_RATIO_GOOGLE,
    'image_resolution_google': IMAGE_RESOLUTION_GOOGLE,
    'cfg_scale_standard': CFG_SCALE_STANDARD
}

def get_template(template_name):
    """
    Get a parameter template by name.
    
    Args:
        template_name (str): Name of the template
        
    Returns:
        dict: Template configuration, or None if not found
    """
    return PARAMETER_TEMPLATES.get(template_name)

def resolve_template_reference(param_config):
    """
    Resolve a template reference in a parameter configuration.
    If the config contains 'template' key, replace it with the actual template.
    
    Args:
        param_config (dict): Parameter configuration that may contain 'template' key
        
    Returns:
        dict: Resolved parameter configuration
    """
    if isinstance(param_config, dict) and 'template' in param_config:
        template_name = param_config['template']
        template = get_template(template_name)
        if template:
            # Merge template with any overrides in param_config
            resolved = template.copy()
            resolved.update({k: v for k, v in param_config.items() if k != 'template'})
            return resolved
    return param_config

