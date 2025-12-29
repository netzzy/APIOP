from MediaGenBase import MediaGenBase
from model_detector import ModelDetector
from api_request_handler import APIRequestHandler
from models_registry import get_registry
import json


class VideoGen(MediaGenBase):

    def __init__(self, ownerComp):
        # Initialize parent class first (with media_type='video')
        super().__init__(ownerComp, media_type='video')
        
        self.logger.log('VideoGen initialized', level='INFO')
        
        # Initialize model detector and registry
        self.registry = get_registry()
        self.model_detector = ModelDetector(self.registry)
        
        # Setup custom parameters
        self.setup_parameters()

    def setup_parameters(self):
        """Create custom parameters for video generation settings."""
        # Create Active parameter (first, bool type)
        self.create_parameter('Active', 'bool', page='Config',
                            label='Active',
                            default=False,
                            help_text='Indicates if video generation is in progress',
                            order=0)
        
        # Create Aspect Ratio parameter (menu based on video API docs)
        aspect_ratio_options = ['16:9', '9:16', '1:1']
        self.create_parameter('Aspectratio', 'menu', page='Config',
                            label='Aspect Ratio',
                            menu_items=aspect_ratio_options,
                            default='16:9',
                            help_text='Video aspect ratio (default: 16:9)')
        
        # Create Duration parameter (menu based on API docs)
        duration_options = ['5', '10']
        self.create_parameter('Duration', 'menu', page='Config',
                            label='Duration',
                            menu_items=duration_options,
                            default='5',
                            help_text='Video duration in seconds (default: 5)')
        
        # Create CFG Scale parameter
        self.create_parameter('Cfgscale', 'float', page='Config',
                            label='CFG Scale',
                            default=0.9,
                            norm_min=0.0,
                            norm_max=1.0,
                            help_text='Classifier Free Guidance scale (0-1, default: 0.9)')
        
        # Create Generate pulse button
        self.create_parameter('Generate', 'pulse', page='Config',
                            label='Generate Video',
                            help_text='Generate video using current settings')
        
        # Create Stop Generation pulse button
        self.create_parameter('Stopgeneration', 'pulse', page='Config',
                            label='Stop Generation',
                            help_text='Stop all active video generation tasks')
        
        # Create Clear Files pulse button
        self.create_parameter('Clearfiles', 'pulse', page='Config',
                            label='Clear Files',
                            help_text='Clear all entries from SAVED_FILES table')

    def _detect_model(self):
        """
        Detect which model to use based on first frame image availability.
        Uses registry-based detection.
        
        Returns:
            str: Model ID from registry
        """
        has_reference = self._check_ref_in1_exists()
        model_id = self.model_detector.detect_from_context(
            has_reference_image=has_reference,
            media_type='video',
            owner_comp=self.ownerComp
        )
        
        # Fallback to default models if detection fails
        if not model_id:
            if has_reference:
                return 'klingai/v2.5-turbo/pro/image-to-video'
            else:
                return 'klingai/v2.5-turbo/pro/text-to-video'
        
        return model_id
    
    def _get_first_frame_image(self):
        """
        Get and encode the first frame image from REF_IN1 operator.
        Uses base class method for encoding.
        
        Returns:
            str: Base64-encoded image data URI, or None if not found
        """
        # Check if REF_IN1 exists and is not empty
        if not self._check_ref_in1_exists():
            return None
        
        # Get the non-resized version
        ref_image = self.ownerComp.op('REF_IN1')
        if not ref_image:
            return None
        
        # Use base class method to encode
        data_uri = self._encode_image_to_base64(ref_image)
        if data_uri:
            self.logger.log("Collected first frame image from REF_IN1", level='INFO')
        
        return data_uri


    
    async def _generate_video_async(self, prompt, model, output_dir, duration, aspect_ratio, cfg_scale, first_frame_image=None):
        """
        Main async method to generate a video from the AIMLAPI.
        Uses API request handler for unified request handling with polling.
        
        Args:
            prompt (str): The text prompt for video generation
            model (str): The model to use
            output_dir (str): Directory to save the generated video
            duration (int): Video duration in seconds
            aspect_ratio (str): Video aspect ratio
            cfg_scale (float): CFG scale
            first_frame_image (str, optional): Base64-encoded image data URI for image-to-video
            
        Returns:
            str: Path to the saved video file, or None if failed
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
                'duration': int(duration),
                'aspect_ratio': aspect_ratio,
                'cfg_scale': float(cfg_scale)
            }
            
            # Add image_url if provided (for image-to-video)
            if first_frame_image:
                payload['image_url'] = first_frame_image
            
            # Truncate prompt for logging (don't log whole prompt)
            prompt_preview = prompt[:50] + '...' if len(prompt) > 50 else prompt
            self.logger.log(f"Creating video task with prompt: '{prompt_preview}'", level='INFO')
            self.logger.log(f"Using model: {model}", level='INFO')
            
            # Step 1: Create video generation task
            response_data = await api_handler.create_generation_task(model_config, payload)
            
            if not response_data:
                return None
            
            # Extract generation ID
            generation_id = api_handler.extract_generation_id(response_data)
            if not generation_id:
                error_msg = "No generation ID in response: " + json.dumps(response_data, indent=2)
                self.logger.log(error_msg, level='ERROR')
                return None
            
            self.logger.log(f"Video task created with ID: {generation_id}", level='INFO')
            
            # Step 2: Poll for video result
            poll_response = await api_handler.poll_generation_result(model_config, generation_id)
            
            if not poll_response:
                return None
            
            # Extract video URL from poll response
            video_url = api_handler.extract_media_url(poll_response, media_type='video')
            if not video_url:
                error_msg = "No video URL in completed response: " + json.dumps(poll_response, indent=2)
                self.logger.log(error_msg, level='ERROR')
                return None
            
            # Step 3: Download and save the video
            # Generate filename and filepath using prompt and node name
            filepath, filename = self._generate_filename(prompt, output_dir, file_extension='.mp4')
            
            # Download video
            success = await api_handler.download_media(video_url, filepath)
            if success:
                self._add_to_saved_files_table(filepath, prompt)
                return filepath
            else:
                return None
                        
        except Exception as e:
            error_msg = f"Unexpected error during video generation: {e}"
            self.logger.log(error_msg, level='ERROR')
            return None

    def Generate(self, prompt=None, output_dir=None, aspect_ratio=None, duration=None, cfg_scale=None, completion_callback=None):
        """
        Generate a video using the AIMLAPI asynchronously.
        Can be called from the pulse button (no args) or programmatically (with args).
        Automatically detects model based on first frame image availability.
        
        Args:
            prompt (str, optional): Text prompt. If None, uses op("PROMPT").text from the PROMPT operator
            output_dir (str, optional): Output directory. If None, uses op.AOP.par.Outputdir (global setting)
            aspect_ratio (str, optional): Aspect ratio. If None, uses self.ownerComp.par.Aspectratio
            duration (int, optional): Video duration in seconds. If None, uses self.ownerComp.par.Duration
            cfg_scale (float, optional): CFG scale. If None, uses self.ownerComp.par.Cfgscale
            completion_callback (callable, optional): Callback function that receives the task object
            
        Returns:
            int: Task ID for tracking the async operation
        """
        # Use parameters from component if not provided
        if prompt is None:
            # Get prompt from PROMPT operator (uses base class method)
            prompt = self._get_prompt_from_operator()
        
        # Auto-detect model based on first frame image
        model = self._detect_model()
        
        # Get first frame image if available
        first_frame_image = self._get_first_frame_image()
        
        # Get output directory from global AOP parameter
        if output_dir is None:
            output_dir = op.AOP.par.Outputdir.eval()
        aspect_ratio = aspect_ratio if aspect_ratio is not None else self.ownerComp.par.Aspectratio.eval()
        duration = duration if duration is not None else int(self.ownerComp.par.Duration.eval())
        cfg_scale = cfg_scale if cfg_scale is not None else float(self.ownerComp.par.Cfgscale.eval())
        
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
        coro = self._generate_video_async(prompt, model, output_dir, duration, aspect_ratio, cfg_scale, first_frame_image)
        
        # Run it through the async manager
        task_id = self.tdAsyncIO.ext.AsyncIOManager.Run(
            coro,
            description=f"Generate Video: {prompt[:50]}...",
            info={'prompt': prompt[:50] + '...' if len(prompt) > 50 else prompt, 'model': model, 'output_dir': output_dir},
            completion_callback=on_completion
        )
        
        return task_id
    
        
        
