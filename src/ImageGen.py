from MediaGenBase import MediaGenBase
from model_detector import ModelDetector
from api_request_handler import APIRequestHandler
from models_registry import get_registry
import aiohttp
import json
import base64
import tempfile
import os


class ImageGen(MediaGenBase):

    def __init__(self, ownerComp):
        # Initialize parent class first (with media_type='image')
        super().__init__(ownerComp, media_type='image')
        
        self.logger.log('ImageGen initialized', level='INFO')
        
        # Initialize model detector and registry
        self.registry = get_registry()
        self.model_detector = ModelDetector(self.registry)
        
        # Setup custom parameters
        self.setup_parameters()

    def setup_parameters(self):
        """Create custom parameters for model and image generation settings."""
        # Create Active parameter (first, bool type)
        self.create_parameter('Active', 'bool', page='Config',
                            label='Active',
                            default=False,
                            help_text='Indicates if image generation is in progress',
                            order=0)
        
        # Create Provider parameter (menu with available providers)
        provider_options = ['Kling', 'Google']
        self.create_parameter('Provider', 'menu', page='Config',
                            label='Provider',
                            menu_items=provider_options,
                            default='Google',
                            help_text='Select the AI provider',
                            order=1)
        
        # Create Model parameter (menu, initially empty, populated by Provider callback)
        self.create_parameter('Model', 'menu', page='Config',
                            label='Model',
                            menu_items=[],
                            default='',
                            help_text='Select the model (updates based on provider selection)',
                            order=2)
        
        # Create Aspect Ratio parameter (menu based on API docs)
        aspect_ratio_options = ['21:9', '1:1', '4:3', '3:2', '2:3', '5:4', '4:5', '3:4', '16:9', '9:16']
        self.create_parameter('Aspectratio', 'menu', page='Config',
                            label='Aspect Ratio',
                            menu_items=aspect_ratio_options,
                            default='1:1',
                            help_text='Image aspect ratio (default: 1:1)')
        
        # Create Resolution parameter (menu based on API docs)
        resolution_options = ['1K', '2K', '4K']
        self.create_parameter('Resolution', 'menu', page='Config',
                            label='Resolution',
                            menu_items=resolution_options,
                            default='1K',
                            help_text='Image resolution (default: 1K)')
        
        # Create Generate pulse button
        self.create_parameter('Generate', 'pulse', page='Config',
                            label='Generate Image',
                            help_text='Generate image using current settings')
        
        # Create Stop Generation pulse button
        self.create_parameter('Stopgeneration', 'pulse', page='Config',
                            label='Stop Generation',
                            help_text='Stop all active image generation tasks')
        
        # Create Clear Files pulse button
        self.create_parameter('Clearfiles', 'pulse', page='Config',
                            label='Clear Files',
                            help_text='Clear all entries from SAVED_FILES table')
        
        # Initialize model menu based on default provider
        self.Provider()

    def Provider(self):
        """
        Callback method when Provider parameter changes.
        Updates Model menu items based on selected provider.
        """
        provider = self.ownerComp.par.Provider.eval()
        self._update_model_menu(provider)
    
    def _detect_model(self):
        """
        Get the selected model from the Model parameter.
        
        Returns:
            str: Model ID from parameter, or None if not set
        """
        model_id = self.ownerComp.par.Model.eval()
        if not model_id:
            return None
        return model_id
    
    def _collect_reference_images(self):
        """
        Collect and encode reference images from REF_IN operators.
        Checks REF_IN1_, REF_IN2_, etc. (up to 14 images as per API limit).
        
        Returns:
            list: List of base64-encoded image data URIs, empty if none found
        """
        image_urls = []
        max_images = 14  # API limit
        
        for i in range(1, max_images + 1):
            # Check the resized version first
            ref_resized = self.ownerComp.op(f'REF_IN{i}_')
            if not ref_resized:
                continue
            
            # Check if it's not empty (128x128 means empty)
            if ref_resized.width == 128 and ref_resized.height == 128:
                continue
            
            # Get the non-resized version
            ref_image = self.ownerComp.op(f'REF_IN{i}')
            if not ref_image:
                continue
            
            try:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Save the image from TOP operator
                ref_image.save(temp_path)
                
                # Read and encode to base64
                with open(temp_path, 'rb') as f:
                    image_bytes = f.read()
                    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Format as data URI
                data_uri = f'data:image/png;base64,{encoded_image}'
                image_urls.append(data_uri)
                
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                self.logger.log(f"Collected reference image from REF_IN{i}", level='INFO')
                
            except Exception as e:
                self.logger.log(f"Error processing REF_IN{i}: {e}", level='ERROR')
                # Clean up temp file on error
                try:
                    if 'temp_path' in locals():
                        os.unlink(temp_path)
                except:
                    pass
        
        return image_urls


    async def _generate_image_async(self, prompt, model, output_dir, aspect_ratio, resolution, image_urls=None):
        """
        Async method to generate an image from the AIMLAPI.
        Uses API request handler for unified request handling.
        
        Args:
            prompt (str): The text prompt for image generation
            model (str): The model to use
            output_dir (str): Directory to save the generated image
            aspect_ratio (str): Image aspect ratio
            resolution (str): Image resolution
            image_urls (list, optional): List of base64-encoded image data URIs for editing mode
            
        Returns:
            str: Path to the saved image file, or None if failed
        """
        try:
            # Get API key from AOP
            api_key = op.AOP.Getkey('aimlapi')
            
            # Get model configuration from registry
            model_config = self.registry.get(model)
            if not model_config:
                error_msg = f"Model {model} not found in registry"
                self.logger.log(error_msg, level='ERROR')
                return None
            
            # Initialize API request handler
            api_handler = APIRequestHandler(api_key, self.logger)
            
            # Build payload from model config and parameters
            payload = {
                'model': model,
                'prompt': prompt,
                'aspect_ratio': aspect_ratio,
                'resolution': resolution,
                'num_images': 1
            }
            
            # Add image_urls if provided (for editing mode)
            if image_urls and len(image_urls) > 0:
                payload['image_urls'] = image_urls
                self.logger.log(f"Reference images prepared and included in request payload: {len(image_urls)} image(s) (image_urls)", level='INFO')
            
            # Truncate prompt for logging (don't log whole prompt)
            prompt_preview = prompt[:50] + '...' if len(prompt) > 50 else prompt
            self.logger.log(f"Generating image with prompt: '{prompt_preview}'", level='INFO')
            self.logger.log(f"Using model: {model}", level='INFO')
            
            # Create generation task (immediate response for images)
            response_data = await api_handler.create_generation_task(model_config, payload)
            
            if not response_data:
                return None
            
            # Handle response (immediate for images)
            if 'data' in response_data and len(response_data['data']) > 0:
                image_data = response_data['data'][0]
                
                # Generate filename and filepath using prompt and node name
                filepath, filename = self._generate_filename(prompt, output_dir, file_extension='.png')
                
                # Extract media URL or base64 data
                media_url = api_handler.extract_media_url(response_data, media_type='image')
                
                if media_url:
                    # Check if it's a URL or base64
                    if media_url.startswith('http'):
                        # Download from URL
                        success = await api_handler.download_media(media_url, filepath)
                        if success:
                            self._add_to_saved_files_table(filepath, prompt)
                            return filepath
                        else:
                            return None
                    else:
                        # Base64 encoded
                        image_bytes = base64.b64decode(media_url)
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        self.logger.log(f"Image saved successfully to: {filepath}", level='INFO')
                        self._add_to_saved_files_table(filepath, prompt)
                        return filepath
                else:
                    error_msg = "Unexpected response format. Response data: " + json.dumps(response_data, indent=2)
                    self.logger.log(error_msg, level='ERROR')
                    return None
            else:
                error_msg = "No image data in response. Full response: " + json.dumps(response_data, indent=2)
                self.logger.log(error_msg, level='ERROR')
                return None
                        
        except Exception as e:
            error_msg = f"Unexpected error during image generation: {e}"
            self.logger.log(error_msg, level='ERROR')
            return None

    def Generate(self, prompt=None, output_dir=None, aspect_ratio=None, resolution=None, completion_callback=None):
        """
        Generate an image using the AIMLAPI asynchronously.
        Can be called from the pulse button (no args) or programmatically (with args).
        Uses selected model from Model parameter.
        
        Args:
            prompt (str, optional): Text prompt. If None, uses op("PROMPT").text from the PROMPT operator
            output_dir (str, optional): Output directory. If None, uses op.AOP.par.Outputdir (global setting)
            aspect_ratio (str, optional): Aspect ratio. If None, uses self.ownerComp.par.Aspectratio
            resolution (str, optional): Resolution. If None, uses self.ownerComp.par.Resolution
            completion_callback (callable, optional): Callback function that receives the task object
            
        Returns:
            int: Task ID for tracking the async operation, or None if validation fails
        """
        # Use parameters from component if not provided
        if prompt is None:
            # Get prompt from PROMPT operator (uses base class method)
            prompt = self._get_prompt_from_operator()
        
        # Get selected model from parameter
        model = self._detect_model()
        if not model:
            error_msg = "No model selected. Please select a model from the Model parameter."
            self.logger.log(error_msg, level='ERROR')
            return None
        
        # Check if model supports image parameters
        supports_image, is_required = self._model_supports_image_parameter(model)
        
        # Collect reference images if model supports them (required or optional)
        image_urls = []
        if supports_image:
            image_urls = self._collect_reference_images()
            if is_required and not image_urls:
                error_msg = f"Model {model} requires reference images, but none were found. Please provide reference images in REF_IN operators."
                self.logger.log(error_msg, level='ERROR')
                return None
            elif image_urls:
                self.logger.log(f"Using {len(image_urls)} reference image(s) from REF_IN operators for model {model}", level='INFO')
        
        # Get output directory from global AOP parameter
        if output_dir is None:
            output_dir = op.AOP.par.Outputdir.eval()
        aspect_ratio = aspect_ratio if aspect_ratio is not None else self.ownerComp.par.Aspectratio.eval()
        resolution = resolution if resolution is not None else self.ownerComp.par.Resolution.eval()
        
        # Set Active to True when starting generation
        self.ownerComp.par.Active = True
        
        # Create completion callback that updates Active status
        def on_completion(task):
            # Check if there are any active tasks remaining
            self._update_active_status()
            # Call user's completion callback if provided
            if completion_callback:
                completion_callback(task)
        
        # Create the async coroutine
        coro = self._generate_image_async(prompt, model, output_dir, aspect_ratio, resolution, image_urls if image_urls else None)
        
        # Run it through the async manager
        task_id = self.tdAsyncIO.ext.AsyncIOManager.Run(
            coro,
            description=f"Generate Image: {prompt[:50]}...",
            info={'prompt': prompt[:50] + '...' if len(prompt) > 50 else prompt, 'model': model, 'output_dir': output_dir},
            completion_callback=on_completion
        )
        
        return task_id
    
        
        
