"""
Model Detector - Pattern-based model detection based on context.

Detects appropriate models based on available inputs (reference images, media type, etc.)
"""

import re
from models_registry import get_registry, get_models_by_type, get_models_by_detection


class ModelDetector:
    """Smart model detection based on patterns and context."""
    
    # Pattern-based detection rules
    PATTERNS = {
        'text-to-video': r'.*t2v.*|.*text-to-video.*',
        'image-to-video': r'.*i2v.*|.*image-to-video.*',
        'video-to-video': r'.*v2v.*|.*video-to-video.*',
        'editing': r'.*edit.*|.*-edit$',
        'generation': r'.*pro.*|.*standard.*'
    }
    
    def __init__(self, registry=None):
        """
        Initialize the model detector.
        
        Args:
            registry (dict, optional): Model registry. If None, loads from get_registry()
        """
        self.registry = registry if registry else get_registry()
    
    def detect_from_context(self, has_reference_image, media_type='video', owner_comp=None):
        """
        Detect model based on available inputs.
        
        Args:
            has_reference_image (bool): Whether reference image is available
            media_type (str): 'image' or 'video'
            owner_comp: TouchDesigner component (optional, for checking REF_IN1_)
            
        Returns:
            str: Model ID, or None if no match found
        """
        # Filter by media type
        candidates = get_models_by_type(media_type)
        
        # Filter by reference requirement
        if has_reference_image:
            # Filter for models that require reference
            candidates = {k: v for k, v in candidates.items() 
                         if v.get('detection', {}).get('requires_reference', False)}
        else:
            # Filter for models that don't require reference
            candidates = {k: v for k, v in candidates.items() 
                         if not v.get('detection', {}).get('requires_reference', False)}
        
        if not candidates:
            return None
        
        # If owner_comp provided, verify reference check
        if owner_comp:
            for model_id, config in list(candidates.items()):
                detection = config.get('detection', {})
                ref_check = detection.get('reference_check', 'REF_IN1_')
                
                # Check if the reference operator exists and is not empty
                ref_op = owner_comp.op(ref_check)
                if ref_op:
                    width, height = ref_op.width, ref_op.height
                    # 128x128 typically means empty in TouchDesigner
                    is_empty = (width == 128 and height == 128)
                    
                    if has_reference_image and is_empty:
                        # Model requires reference but it's empty
                        candidates.pop(model_id, None)
                    elif not has_reference_image and not is_empty:
                        # Model doesn't require reference but one exists
                        candidates.pop(model_id, None)
        
        # Return best match (prioritize by version, quality, etc.)
        return self._rank_models(candidates)
    
    def _matches_pattern(self, model_id, pattern_key):
        """
        Check if model matches a pattern.
        
        Args:
            model_id (str): Model identifier
            pattern_key (str): Key from PATTERNS dict
            
        Returns:
            bool: True if matches pattern
        """
        pattern = self.PATTERNS.get(pattern_key, '')
        return bool(re.search(pattern, model_id, re.IGNORECASE))
    
    def _filter_by_type(self, media_type):
        """
        Filter models by media type.
        
        Args:
            media_type (str): 'image' or 'video'
            
        Returns:
            dict: Filtered model registry
        """
        return get_models_by_type(media_type)
    
    def _rank_models(self, candidates):
        """
        Prioritize models (e.g., pro > standard, newer versions > older).
        
        Args:
            candidates (dict): Dictionary of model_id -> config
            
        Returns:
            str: Best matching model ID, or first candidate if no ranking possible
        """
        if not candidates:
            return None
        
        # Priority order:
        # 1. Models with 'pro' in name
        # 2. Models with 'turbo' in name
        # 3. Models with version numbers (higher is better)
        # 4. Alphabetically first
        
        def score_model(model_id):
            score = 0
            model_lower = model_id.lower()
            
            # Pro models get highest priority
            if 'pro' in model_lower:
                score += 1000
            
            # Turbo models get high priority
            if 'turbo' in model_lower:
                score += 500
            
            # Extract version numbers (e.g., v2.5 -> 2.5)
            version_match = re.search(r'v?(\d+)\.?(\d*)', model_id)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2)) if version_match.group(2) else 0
                score += major * 100 + minor
            
            return score
        
        # Sort by score (descending), then alphabetically
        sorted_models = sorted(candidates.keys(), key=lambda x: (-score_model(x), x))
        
        return sorted_models[0] if sorted_models else None
    
    def get_model_by_id(self, model_id):
        """
        Get model configuration by ID.
        
        Args:
            model_id (str): Model identifier
            
        Returns:
            dict: Model configuration, or None if not found
        """
        return self.registry.get(model_id)

