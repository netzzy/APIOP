"""
API Request Handler - Unified handler for different AIMLAPI endpoint patterns.

Handles standard and provider-specific endpoints, immediate and polling responses.
"""

import aiohttp
import json
import base64
import asyncio
import time


class APIRequestHandler:
    """Unified handler for different AIMLAPI endpoint patterns."""
    
    BASE_URL = 'https://api.aimlapi.com'
    
    def __init__(self, api_key, logger=None):
        """
        Initialize the API request handler.
        
        Args:
            api_key (str): AIMLAPI API key
            logger: Logger instance (optional)
        """
        self.api_key = api_key
        self.logger = logger if logger else print
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def build_url(self, model_config):
        """
        Build the correct URL based on endpoint type.
        
        Args:
            model_config (dict): Model configuration from registry
            
        Returns:
            str: Full API URL
        """
        endpoint = model_config['endpoint']
        endpoint_type = model_config.get('endpoint_type', 'standard')
        
        if endpoint_type == 'provider':
            # Provider-specific endpoint (already full path)
            return f"{self.BASE_URL}{endpoint}"
        else:
            # Standard endpoint
            return f"{self.BASE_URL}{endpoint}"
    
    async def create_generation_task(self, model_config, payload):
        """
        Create a generation task (POST request).
        
        Args:
            model_config (dict): Model configuration from registry
            payload (dict): Request payload
            
        Returns:
            dict: Response data, or None if failed
        """
        url = self.build_url(model_config)
        
        # Some models need 'model' in payload, others don't
        if 'model' not in payload and 'model' in model_config.get('parameters', {}):
            # Add model ID to payload if not present
            payload['model'] = model_config.get('id', list(model_config.keys())[0] if isinstance(model_config, dict) else None)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    # Accept both 200 (OK) and 201 (Created) as success
                    if response.status in [200, 201]:
                        response_data = await response.json()
                        return response_data
                    else:
                        error_text = await response.text()
                        payload_str = json.dumps(payload, indent=2)
                        error_msg = f"Error creating generation task: HTTP {response.status}\nRequest Payload: {payload_str}\nResponse: {error_text}"
                        if hasattr(self.logger, 'log'):
                            self.logger.log(error_msg, level='ERROR')
                        else:
                            self.logger(error_msg)
                        return None
        except Exception as e:
            payload_str = json.dumps(payload, indent=2)
            error_msg = f"Unexpected error creating generation task: {e}\nRequest Payload: {payload_str}"
            if hasattr(self.logger, 'log'):
                self.logger.log(error_msg, level='ERROR')
            else:
                self.logger(error_msg)
            return None
    
    async def poll_generation_result(self, model_config, generation_id):
        """
        Poll for generation result (GET request).
        
        Args:
            model_config (dict): Model configuration from registry
            generation_id (str): Generation ID from task creation
            
        Returns:
            dict: Response data with status and result, or None if failed/timed out
        """
        endpoint = model_config.get('poll_endpoint', model_config['endpoint'])
        poll_config = {**model_config, 'endpoint': endpoint}
        url = self.build_url(poll_config)
        
        timeout = model_config.get('poll_timeout', 1000)
        poll_interval = model_config.get('poll_interval', 10)
        start_time = time.time()
        
        # Determine poll method (GET by default)
        poll_method = model_config.get('poll_method', 'GET')
        
        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        error_msg = f"Generation timeout after {timeout} seconds"
                        if hasattr(self.logger, 'log'):
                            self.logger.log(error_msg, level='ERROR')
                        else:
                            self.logger(error_msg)
                        return None
                    
                    # Poll for result
                    params = {'generation_id': generation_id}
                    
                    if poll_method == 'GET':
                        async with session.get(url, headers=self.headers, params=params) as response:
                            if response.status == 200:
                                response_data = await response.json()
                                status = response_data.get('status', '')
                                
                                if hasattr(self.logger, 'log'):
                                    self.logger.log(f"Generation status: {status}", level='INFO')
                                
                                if status == 'completed':
                                    return response_data
                                elif status in ['waiting', 'active', 'queued', 'generating']:
                                    # Continue polling
                                    await asyncio.sleep(poll_interval)
                                else:
                                    # Error or unknown status
                                    error_msg = f"Generation failed with status: {status}. Response: {json.dumps(response_data, indent=2)}"
                                    if hasattr(self.logger, 'log'):
                                        self.logger.log(error_msg, level='ERROR')
                                    else:
                                        self.logger(error_msg)
                                    return None
                            else:
                                error_text = await response.text()
                                error_msg = f"Error polling generation result: HTTP {response.status}\nResponse: {error_text}"
                                if hasattr(self.logger, 'log'):
                                    self.logger.log(error_msg, level='ERROR')
                                else:
                                    self.logger(error_msg)
                                return None
                    else:
                        # POST method for polling (if needed)
                        async with session.post(url, headers=self.headers, json=params) as response:
                            if response.status == 200:
                                response_data = await response.json()
                                status = response_data.get('status', '')
                                
                                if status == 'completed':
                                    return response_data
                                elif status in ['waiting', 'active', 'queued', 'generating']:
                                    await asyncio.sleep(poll_interval)
                                else:
                                    error_msg = f"Generation failed with status: {status}"
                                    if hasattr(self.logger, 'log'):
                                        self.logger.log(error_msg, level='ERROR')
                                    return None
                            else:
                                error_text = await response.text()
                                error_msg = f"Error polling: HTTP {response.status}"
                                if hasattr(self.logger, 'log'):
                                    self.logger.log(error_msg, level='ERROR')
                                return None
        except Exception as e:
            error_msg = f"Unexpected error polling generation result: {e}"
            if hasattr(self.logger, 'log'):
                self.logger.log(error_msg, level='ERROR')
            else:
                self.logger(error_msg)
            return None
    
    async def download_media(self, media_url, filepath):
        """
        Download media (image or video) from URL and save to file.
        
        Args:
            media_url (str): URL to download from
            filepath (str): Path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status == 200:
                        media_bytes = await response.read()
                        
                        # Save the media file
                        with open(filepath, 'wb') as f:
                            f.write(media_bytes)
                        
                        if hasattr(self.logger, 'log'):
                            self.logger.log(f"Media saved successfully to: {filepath}", level='INFO')
                        return True
                    else:
                        error_msg = f"Error downloading media: HTTP {response.status}"
                        if hasattr(self.logger, 'log'):
                            self.logger.log(error_msg, level='ERROR')
                        else:
                            self.logger(error_msg)
                        return False
        except Exception as e:
            error_msg = f"Unexpected error downloading media: {e}"
            if hasattr(self.logger, 'log'):
                self.logger.log(error_msg, level='ERROR')
            else:
                self.logger(error_msg)
            return False
    
    def extract_media_url(self, response_data, media_type='image'):
        """
        Extract media URL from API response.
        
        Args:
            response_data (dict): API response data
            media_type (str): 'image' or 'video'
            
        Returns:
            str: Media URL, or None if not found
        """
        if media_type == 'image':
            # Handle image response formats
            if 'data' in response_data and len(response_data['data']) > 0:
                image_data = response_data['data'][0]
                if 'url' in image_data:
                    return image_data['url']
                elif 'b64_json' in image_data:
                    # Return base64 data as-is (caller will handle)
                    return image_data['b64_json']
        elif media_type == 'video':
            # Handle video response formats
            video_data = response_data.get('video')
            if video_data and 'url' in video_data:
                return video_data['url']
        
        return None
    
    def extract_generation_id(self, response_data):
        """
        Extract generation ID from task creation response.
        
        Args:
            response_data (dict): API response data
            
        Returns:
            str: Generation ID, or None if not found
        """
        # Try different possible keys
        generation_id = response_data.get('id') or response_data.get('generation_id')
        return generation_id

