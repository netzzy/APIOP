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
    VIDEO_DURATION_MINIMAX,
    VIDEO_DURATION_LTXV,
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
    },
    
    # Kling Image Model
    'klingai/image-o1': {
        'type': 'image',
        'endpoint_type': 'standard',
        'endpoint': '/v2/image/generations',
        'method': 'POST',
        'response_type': 'immediate',
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'klingai/image-o1',
                'required': True
            },
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
    
    # Kling 1.6 Models
    'kling-video/v1.6/standard/text-to-video': {
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
                'default': 'kling-video/v1.6/standard/text-to-video',
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
    
    'kling-video/v1.6/standard/image-to-video': {
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
                'default': 'kling-video/v1.6/standard/image-to-video',
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
    },
    
    'kling-video/v1.6/standard/multi-image-to-video': {
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
                'default': 'kling-video/v1.6/standard/multi-image-to-video',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'image_urls': {
                'type': 'list',
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
    },
    
    'kling-video/v1.6/pro/text-to-video': {
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
                'default': 'kling-video/v1.6/pro/text-to-video',
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
    
    'kling-video/v1.6/pro/image-to-video': {
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
                'default': 'kling-video/v1.6/pro/image-to-video',
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
    },
    
    # Kling 2.1 Master Models
    'klingai/v2.1-master-text-to-video': {
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
                'default': 'klingai/v2.1-master-text-to-video',
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
    
    'klingai/v2.1-master-image-to-video': {
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
                'default': 'klingai/v2.1-master-image-to-video',
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
    },
    
    # Kling 2.6 Pro Models
    'klingai/video-v2-6-pro-text-to-video': {
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
                'default': 'klingai/video-v2-6-pro-text-to-video',
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
    
    'klingai/video-v2-6-pro-image-to-video': {
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
                'default': 'klingai/video-v2-6-pro-image-to-video',
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
    },
    
    # Kling O1 Models
    'klingai/video-o1-image-to-video': {
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
                'default': 'klingai/video-o1-image-to-video',
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
            'last_image_url': {
                'type': 'str',
                'required': False
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'klingai/video-o1-reference-to-video': {
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
                'default': 'klingai/video-o1-reference-to-video',
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
            'image_url_2': {
                'type': 'str',
                'required': False
            },
            'image_url_3': {
                'type': 'str',
                'required': False
            },
            'image_url_4': {
                'type': 'str',
                'required': False
            },
            'image_url_5': {
                'type': 'str',
                'required': False
            },
            'image_url_6': {
                'type': 'str',
                'required': False
            },
            'image_url_7': {
                'type': 'str',
                'required': False
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'klingai/video-o1-video-to-video-edit': {
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
                'default': 'klingai/video-o1-video-to-video-edit',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'video_url': {
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
    },
    
    'klingai/video-o1-video-to-video-reference': {
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
                'default': 'klingai/video-o1-video-to-video-reference',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'video_url': {
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
    },
    
    # Ltxv Models
    # Based on https://docs.aimlapi.com/api-references/video-models/ltxv/ltxv-2
    'ltxv/ltxv-2': {
        'type': 'video',
        'endpoint_type': 'standard',
        'endpoint': '/v2/video/generations',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/video/generations',
        'poll_method': 'GET',
        'poll_interval': 15,  # Docs recommend 15 seconds
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'ltxv/ltxv-2',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_LTXV,  # Ltxv uses duration options: ['6', '8', '10'], api_type: 'int'
            'aspect_ratio': {
                'type': 'menu',
                'options': ['16:9'],  # Only 16:9 supported according to docs
                'default': '16:9',
                'api_type': 'str',  # API expects string
                'help_text': 'Video aspect ratio (only 16:9 supported)'
            },
            'resolution': {
                'type': 'menu',
                'options': ['1080p', '1440p', '2160p'],
                'default': '1080p',
                'api_type': 'str',  # API expects string
                'help_text': 'Video resolution (default: 1080p)'
            },
            'image_url': {
                'type': 'str',
                'api_type': 'str',  # API expects string (URI)
                'required': False
            }
            # Note: cfg_scale not supported by this model
            # Note: fps and generate_audio are not supported by the API (removed due to "Unrecognized keys" error)
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'ltxv/ltxv-2-fast': {
        'type': 'video',
        'endpoint_type': 'standard',
        'endpoint': '/v2/video/generations',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/video/generations',
        'poll_method': 'GET',
        'poll_interval': 15,  # Docs recommend 15 seconds
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'ltxv/ltxv-2-fast',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_LTXV,  # Ltxv uses duration options: ['6', '8', '10'], api_type: 'int'
            'aspect_ratio': {
                'type': 'menu',
                'options': ['16:9'],  # Only 16:9 supported according to docs
                'default': '16:9',
                'api_type': 'str',  # API expects string
                'help_text': 'Video aspect ratio (only 16:9 supported)'
            },
            'resolution': {
                'type': 'menu',
                'options': ['1080p', '1440p', '2160p'],
                'default': '1080p',
                'api_type': 'str',  # API expects string
                'help_text': 'Video resolution (default: 1080p)'
            },
            'image_url': {
                'type': 'str',
                'api_type': 'str',  # API expects string (URI)
                'required': False
            }
            # Note: cfg_scale not supported by this model
            # Note: fps and generate_audio are not supported by the API (removed due to "Unrecognized keys" error)
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    # MiniMax Models
    'minimax/hailuo-02': {
        'type': 'video',
        'endpoint_type': 'provider',
        'endpoint': '/v2/generate/video/minimax/generation',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/generate/video/minimax/generation',
        'poll_method': 'GET',
        'poll_interval': 10,
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'minimax/hailuo-02',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_MINIMAX,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'image_url': {
                'type': 'str',
                'required': False
            }
            # Note: cfg_scale not supported by this model
            # Note: image_url is optional - only include for image-to-video
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'minimax/hailuo-2.3': {
        'type': 'video',
        'endpoint_type': 'provider',
        'endpoint': '/v2/generate/video/minimax/generation',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/generate/video/minimax/generation',
        'poll_method': 'GET',
        'poll_interval': 10,
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'minimax/hailuo-2.3',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_MINIMAX,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'image_url': {
                'type': 'str',
                'required': False
            }
            # Note: cfg_scale not supported by this model
            # Note: image_url is optional - only include for image-to-video
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'minimax/hailuo-2.3-fast': {
        'type': 'video',
        'endpoint_type': 'provider',
        'endpoint': '/v2/generate/video/minimax/generation',
        'method': 'POST',
        'response_type': 'polling',
        'poll_endpoint': '/v2/generate/video/minimax/generation',
        'poll_method': 'GET',
        'poll_interval': 10,
        'poll_timeout': 1000,
        'parameters': {
            'model': {
                'type': 'str',
                'default': 'minimax/hailuo-2.3-fast',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_MINIMAX,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'image_url': {
                'type': 'str',
                'required': False
            }
            # Note: cfg_scale not supported by this model
            # Note: image_url is optional - only include for image-to-video
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    # Alibaba Cloud Models
    'alibaba/wan2.5-t2v-preview': {
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
                'default': 'alibaba/wan2.5-t2v-preview',
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
    
    'alibaba/wan2.5-i2v-preview': {
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
                'default': 'alibaba/wan2.5-i2v-preview',
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
    },
    
    # LumaAI Models
    'luma/ray-2': {
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
                'default': 'luma/ray-2',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD
            # Note: cfg_scale not supported by this model
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'luma/ray-flash-2': {
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
                'default': 'luma/ray-flash-2',
                'required': True
            },
            'prompt': {
                'type': 'str',
                'required': True
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD
            # Note: cfg_scale not supported by this model
        },
        'detection': {
            'requires_reference': False,
            'reference_check': 'REF_IN1_'
        }
    },
    
    # Runway Models
    'gen3a_turbo': {
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
                'default': 'gen3a_turbo',
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
            'tail_image_url': {
                'type': 'str',
                'required': False
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'runway/gen4_turbo': {
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
                'default': 'runway/gen4_turbo',
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
            'tail_image_url': {
                'type': 'str',
                'required': False
            },
            'duration': VIDEO_DURATION_STANDARD,
            'aspect_ratio': VIDEO_ASPECT_RATIO_STANDARD,
            'cfg_scale': CFG_SCALE_STANDARD
        },
        'detection': {
            'requires_reference': True,
            'reference_check': 'REF_IN1_'
        }
    },
    
    'runway/gen4_aleph': {
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
                'default': 'runway/gen4_aleph',
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
    
    'runway/act_two': {
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
                'default': 'runway/act_two',
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

def extract_provider_from_model_id(model_id):
    """
    Extract provider name from model ID based on prefix patterns.
    
    Args:
        model_id (str): Model identifier (e.g., 'klingai/v2.5-turbo/pro/text-to-video')
        
    Returns:
        str: Provider name (e.g., 'Kling', 'Google', etc.)
    """
    if not model_id:
        return None
    
    model_id_lower = model_id.lower()
    
    # Check prefixes in order of specificity
    if model_id_lower.startswith('google/'):
        return 'Google'
    elif model_id_lower.startswith('klingai/') or model_id_lower.startswith('kling-video/'):
        return 'Kling'
    elif model_id_lower.startswith('minimax/'):
        return 'MiniMax'
    elif model_id_lower.startswith('alibaba/'):
        return 'Alibaba Cloud'
    elif model_id_lower.startswith('luma/'):
        return 'LumaAI'
    elif model_id_lower.startswith('runway/') or model_id_lower.startswith('gen'):
        return 'Runway'
    elif model_id_lower.startswith('ltxv/'):
        return 'Ltxv'
    else:
        # Default or unknown provider
        return None

def get_models_by_provider(provider, media_type=None):
    """
    Get all models for a specific provider, optionally filtered by media type.
    
    Args:
        provider (str): Provider name (e.g., 'Kling', 'Google')
        media_type (str, optional): 'image' or 'video' to filter by type
        
    Returns:
        dict: Dictionary of model_id -> config for matching models
    """
    registry = get_registry()
    result = {}
    
    for model_id, config in registry.items():
        model_provider = extract_provider_from_model_id(model_id)
        
        # Check provider match
        if model_provider != provider:
            continue
        
        # Check media type if specified
        if media_type and config.get('type') != media_type:
            continue
        
        result[model_id] = config
    
    return result

