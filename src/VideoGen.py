from AopUtil import AopUtil
import aiohttp
import json
import os
import base64
import re
import tempfile
import asyncio
import time
from datetime import datetime


class VideoGen(AopUtil):

    def __init__(self, ownerComp):
        # Initialize parent class first
        super().__init__(ownerComp)
        
        self.ownerComp = ownerComp 
        self.logger = op('Logger').ext.Logger if op('Logger') else print # Basic fallback logging
        self.logger.log('VideoGen initialized', level='INFO')
        
        self.tdAsyncIO = self.ownerComp.op('TDAsyncIO')
        
        # Setup custom parameters
        self.setup_parameters()
        
        # API configuration
        self.api_url = 'https://api.aimlapi.com/v2/video/generations'

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
        
        Returns:
            str: 'klingai/v2.5-turbo/pro/image-to-video' if first frame found, 
                 'klingai/v2.5-turbo/pro/text-to-video' otherwise
        """
        ref_in1_resized = self.ownerComp.op('REF_IN1_')
        if ref_in1_resized:
            width, height = ref_in1_resized.width, ref_in1_resized.height
            if width != 128 or height != 128:
                return 'klingai/v2.5-turbo/pro/image-to-video'
        return 'klingai/v2.5-turbo/pro/text-to-video'
    
    def _get_first_frame_image(self):
        """
        Get and encode the first frame image from REF_IN1 operator.
        
        Returns:
            str: Base64-encoded image data URI, or None if not found
        """
        # Check the resized version first
        ref_resized = self.ownerComp.op('REF_IN1_')
        if not ref_resized:
            return None
        
        # Check if it's not empty (128x128 means empty)
        if ref_resized.width == 128 and ref_resized.height == 128:
            return None
        
        # Get the non-resized version
        ref_image = self.ownerComp.op('REF_IN1')
        if not ref_image:
            return None
        
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
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            self.logger.log("Collected first frame image from REF_IN1", level='INFO')
            return data_uri
            
        except Exception as e:
            self.logger.log(f"Error processing first frame image: {e}", level='ERROR')
            # Clean up temp file on error
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            return None

    def _generate_filename(self, prompt, output_dir):
        """
        Generate filename and filepath using prompt words and node name subfolder.
        
        Args:
            prompt (str): The text prompt
            output_dir (str): Base output directory
            
        Returns:
            tuple: (filepath, filename) - Full path and filename
        """
        # Get first couple of words from prompt (sanitize for filename)
        words = prompt.split()[:3]  # First 3 words
        prompt_snippet = '_'.join(words).lower()
        # Remove invalid filename characters
        prompt_snippet = re.sub(r'[^\w\s-]', '', prompt_snippet)
        prompt_snippet = re.sub(r'[-\s]+', '_', prompt_snippet)
        
        # Create subfolder with node name
        node_name = self.ownerComp.name
        subfolder = os.path.join(output_dir, node_name)
        os.makedirs(subfolder, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prompt_snippet}_{timestamp}.mp4"
        filepath = os.path.join(subfolder, filename)
        
        return filepath, filename
    
    def Clearfiles(self):
        """Pulse callback for Clear Files button - clears SAVED_FILES table and adds empty row."""
        try:
            saved_files_table = self.ownerComp.op('SAVED_FILES')
            if saved_files_table:
                # Clear all rows from the table
                saved_files_table.clear()
                
                # Add one empty row
                saved_files_table.appendRow(['../empty.png', ''])
                
                # Set Scroll cursor to 0
                scroll_op = self.ownerComp.op('Scroll')
                if scroll_op:
                    scroll_op.par.Cursor = 0
                    self.logger.log("Set Scroll cursor to 0", level='INFO')
                
                self.logger.log("Cleared SAVED_FILES table and added empty row", level='INFO')
                
                # Clear logs like Logger.clearlog pulse
                logger_op = op('Logger')
                if logger_op and hasattr(logger_op.ext.Logger, 'Clearlog'):
                    logger_op.ext.Logger.Clearlog()
            else:
                self.logger.log("SAVED_FILES table operator not found", level='WARNING')
        except Exception as e:
            self.logger.log(f"Error clearing SAVED_FILES table: {e}", level='ERROR')
    
    def _add_to_saved_files_table(self, filepath, prompt):
        """
        Add a row to the SAVED_FILES table with filename and prompt.
        
        Args:
            filepath (str): Full path to the generated video file
            prompt (str): The prompt used to generate the video
        """
        try:
            saved_files_table = self.ownerComp.op('SAVED_FILES')
            if saved_files_table:
                # Get just the filename from the full path
                filename = os.path.basename(filepath)
                
                # Ensure table has headers if it's empty
                if saved_files_table.numRows == 0:
                    saved_files_table.appendRow(['filename', 'prompt'])
                
                # Insert new row with filename and prompt
                saved_files_table.appendRow([filename, prompt])
                self.logger.log(f"Added to SAVED_FILES table: {filename}", level='INFO')
                
                # Set Scroll cursor to the last row (newly added row)
                scroll_op = self.ownerComp.op('Scroll')
                if scroll_op:
                    last_row_index = saved_files_table.numRows - 1
                    scroll_op.par.Cursor = last_row_index
                    self.logger.log(f"Set Scroll cursor to row {last_row_index}", level='INFO')
            else:
                self.logger.log("SAVED_FILES table operator not found", level='WARNING')
        except Exception as e:
            self.logger.log(f"Error adding to SAVED_FILES table: {e}", level='ERROR')

    async def _create_video_task_async(self, prompt, model, duration, aspect_ratio, cfg_scale, image_url=None):
        """
        Create a video generation task on the server.
        
        Args:
            prompt (str): The text prompt for video generation
            model (str): The model to use
            duration (int): Video duration in seconds (5 or 10)
            aspect_ratio (str): Video aspect ratio
            cfg_scale (float): CFG scale (0-1)
            image_url (str, optional): Base64-encoded image data URI for image-to-video
            
        Returns:
            str: Generation ID, or None if failed
        """
        try:
            # Get API key from AOP
            api_key = op.AOP.Getkey('aimlapi')
            
            # Define the payload
            payload = {
                'model': model,
                'prompt': prompt,
                'duration': int(duration),
                'aspect_ratio': aspect_ratio,
                'cfg_scale': float(cfg_scale)
            }
            
            # Add image_url if provided (for image-to-video)
            if image_url:
                payload['image_url'] = image_url
            
            # Set the headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Truncate prompt for logging (don't log whole prompt)
            prompt_preview = prompt[:50] + '...' if len(prompt) > 50 else prompt
            self.logger.log(f"Creating video task with prompt: '{prompt_preview}'", level='INFO')
            self.logger.log(f"Using model: {model}", level='INFO')
            
            # Make the async POST request
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    # Accept both 200 (OK) and 201 (Created) as success
                    if response.status in [200, 201]:
                        response_data = await response.json()
                        generation_id = response_data.get('id')
                        if generation_id:
                            self.logger.log(f"Video task created with ID: {generation_id}", level='INFO')
                            return generation_id
                        else:
                            error_msg = "No generation ID in response: " + json.dumps(response_data, indent=2)
                            self.logger.log(error_msg, level='ERROR')
                            return None
                    else:
                        error_text = await response.text()
                        error_msg = f"Error creating video task: HTTP {response.status}\nResponse: {error_text}"
                        self.logger.log(error_msg, level='ERROR')
                        return None
                        
        except Exception as e:
            error_msg = f"Unexpected error creating video task: {e}"
            self.logger.log(error_msg, level='ERROR')
            return None
    
    async def _poll_video_result_async(self, generation_id):
        """
        Poll the server for video generation result.
        
        Args:
            generation_id (str): The generation ID from task creation
            
        Returns:
            str: Video URL when completed, or None if failed/timed out
        """
        try:
            # Get API key from AOP
            api_key = op.AOP.Getkey('aimlapi')
            
            # Set the headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            timeout = 1000  # seconds as per API docs
            start_time = time.time()
            poll_interval = 10  # seconds
            
            async with aiohttp.ClientSession() as session:
                while True:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        self.logger.log(f"Video generation timeout after {timeout} seconds", level='ERROR')
                        return None
                    
                    # Poll for result
                    params = {'generation_id': generation_id}
                    async with session.get(self.api_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            status = response_data.get('status', '')
                            
                            self.logger.log(f"Video generation status: {status}", level='INFO')
                            
                            if status == 'completed':
                                video_data = response_data.get('video')
                                if video_data and 'url' in video_data:
                                    video_url = video_data['url']
                                    self.logger.log(f"Video generation completed: {video_url}", level='INFO')
                                    return video_url
                                else:
                                    error_msg = "No video URL in completed response: " + json.dumps(response_data, indent=2)
                                    self.logger.log(error_msg, level='ERROR')
                                    return None
                            elif status in ['waiting', 'active', 'queued', 'generating']:
                                # Continue polling
                                await asyncio.sleep(poll_interval)
                            else:
                                # Error or unknown status
                                error_msg = f"Video generation failed with status: {status}. Response: {json.dumps(response_data, indent=2)}"
                                self.logger.log(error_msg, level='ERROR')
                                return None
                        else:
                            error_text = await response.text()
                            error_msg = f"Error polling video result: HTTP {response.status}\nResponse: {error_text}"
                            self.logger.log(error_msg, level='ERROR')
                            return None
                            
        except Exception as e:
            error_msg = f"Unexpected error polling video result: {e}"
            self.logger.log(error_msg, level='ERROR')
            return None
    
    async def _generate_video_async(self, prompt, model, output_dir, duration, aspect_ratio, cfg_scale, first_frame_image=None):
        """
        Main async method to generate a video from the AIMLAPI.
        Orchestrates the two-step process: create task, then poll for result.
        
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
            # Step 1: Create video generation task
            generation_id = await self._create_video_task_async(
                prompt, model, duration, aspect_ratio, cfg_scale, first_frame_image
            )
            
            if not generation_id:
                return None
            
            # Step 2: Poll for video result
            video_url = await self._poll_video_result_async(generation_id)
            
            if not video_url:
                return None
            
            # Step 3: Download and save the video
            # Generate filename and filepath using prompt and node name
            filepath, filename = self._generate_filename(prompt, output_dir)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as video_response:
                    if video_response.status == 200:
                        video_bytes = await video_response.read()
                        
                        # Save the video
                        with open(filepath, 'wb') as f:
                            f.write(video_bytes)
                        self.logger.log(f"Video saved successfully to: {filepath}", level='INFO')
                        
                        # Add to SAVED_FILES table
                        self._add_to_saved_files_table(filepath, prompt)
                        
                        return filepath
                    else:
                        error_msg = f"Error downloading video: {video_response.status}"
                        self.logger.log(error_msg, level='ERROR')
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
            # Get prompt from PROMPT operator (text DAT)
            prompt_op = self.ownerComp.op('PROMPT')
            if prompt_op:
                prompt = prompt_op.text
            else:
                error_msg = "PROMPT operator not found. Please provide a prompt argument or create a PROMPT operator."
                self.logger.log(error_msg, level='ERROR')
                raise ValueError(error_msg)
        
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
    
    def Stopgeneration(self):
        """Pulse callback for Stop Generation button - cancels all active generation tasks."""
        try:
            # Cancel all active tasks
            self.tdAsyncIO.ext.AsyncIOManager.Cancelactive()
            
            # Update Active status to False
            self.ownerComp.par.Active = False
            
            self.logger.log("Stopped all active video generation tasks", level='INFO')
        except Exception as e:
            self.logger.log(f"Error stopping generation tasks: {e}", level='ERROR')
    
    def _update_active_status(self):
        """Update the Active parameter based on whether there are active tasks."""
        active_tasks_count = self.tdAsyncIO.ext.AsyncIOManager.GetActiveTasksCount()
        self.ownerComp.par.Active = active_tasks_count > 0
        
        
