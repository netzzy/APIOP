from AopUtil import AopUtil
import aiohttp
import json
import os
import base64
import re
from datetime import datetime


class ImageGen(AopUtil):

    def __init__(self, ownerComp):
        # Initialize parent class first
        super().__init__(ownerComp)
        
        self.ownerComp = ownerComp 
        self.logger = op('Logger').ext.Logger if op('Logger') else print # Basic fallback logging
        self.logger.log('ImageGen initialized', level='INFO')
        
        self.tdAsyncIO = self.ownerComp.op('TDAsyncIO')
        
        # Setup custom parameters
        self.setup_parameters()
        
        # API configuration
        self.api_url = 'https://api.aimlapi.com/v1/images/generations'

    def setup_parameters(self):
        """Create custom parameters for model and image generation settings."""
        # Create Active parameter (first, bool type)
        self.create_parameter('Active', 'bool', page='Config',
                            label='Active',
                            default=False,
                            help_text='Indicates if image generation is in progress',
                            order=0)
        
        # Create Model parameter with default value
        self.create_parameter('Model', 'str', page='Config',
                            label='Model',
                            default='google/nano-banana-pro',
                            help_text='AI model to use for image generation')
        
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
        filename = f"{prompt_snippet}_{timestamp}.png"
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
            else:
                self.logger.log("SAVED_FILES table operator not found", level='WARNING')
        except Exception as e:
            self.logger.log(f"Error clearing SAVED_FILES table: {e}", level='ERROR')
    
    def _add_to_saved_files_table(self, filepath, prompt):
        """
        Add a row to the SAVED_FILES table with filename and prompt.
        
        Args:
            filepath (str): Full path to the generated image file
            prompt (str): The prompt used to generate the image
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

    async def _generate_image_async(self, prompt, model, output_dir, aspect_ratio, resolution):
        """
        Async method to generate an image from the AIMLAPI.
        
        Args:
            prompt (str): The text prompt for image generation
            model (str): The model to use
            output_dir (str): Directory to save the generated image
            aspect_ratio (str): Image aspect ratio
            resolution (str): Image resolution
            
        Returns:
            str: Path to the saved image file, or None if failed
        """
        try:
            # Get API key from AOP
            api_key = op.AOP.Getkey('aimlapi')
            
            # Define the payload
            payload = {
                'model': model,
                'prompt': prompt,
                'aspect_ratio': aspect_ratio,
                'resolution': resolution,
                'num_images': 1
            }
            
            # Set the headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            self.logger.log(f"Generating image with prompt: '{prompt}'", level='INFO')
            self.logger.log(f"Using model: {model}", level='INFO')
            
            # Make the async POST request
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    # Check if the request was successful
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Handle different response formats
                        if 'data' in response_data and len(response_data['data']) > 0:
                            image_data = response_data['data'][0]
                            
                            # Generate filename and filepath using prompt and node name
                            filepath, filename = self._generate_filename(prompt, output_dir)
                            
                            # Check if response contains a URL or base64 data
                            if 'url' in image_data:
                                # Download image from URL
                                image_url = image_data['url']
                                self.logger.log(f"Downloading image from URL: {image_url}", level='INFO')
                                
                                async with session.get(image_url) as img_response:
                                    if img_response.status == 200:
                                        image_bytes = await img_response.read()
                                        
                                        # Save the image
                                        with open(filepath, 'wb') as f:
                                            f.write(image_bytes)
                                        self.logger.log(f"Image saved successfully to: {filepath}", level='INFO')
                                        
                                        # Add to SAVED_FILES table
                                        self._add_to_saved_files_table(filepath, prompt)
                                        
                                        return filepath
                                    else:
                                        error_msg = f"Error downloading image: {img_response.status}"
                                        self.logger.log(error_msg, level='ERROR')
                                        return None
                                        
                            elif 'b64_json' in image_data:
                                # Handle base64 encoded image
                                image_data_b64 = image_data['b64_json']
                                image_bytes = base64.b64decode(image_data_b64)
                                
                                # Save the image
                                with open(filepath, 'wb') as f:
                                    f.write(image_bytes)
                                self.logger.log(f"Image saved successfully to: {filepath}", level='INFO')
                                
                                # Add to SAVED_FILES table
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
                    else:
                        error_text = await response.text()
                        error_msg = f"Error: HTTP {response.status}\nResponse: {error_text}"
                        self.logger.log(error_msg, level='ERROR')
                        return None
                        
        except Exception as e:
            error_msg = f"Unexpected error during image generation: {e}"
            self.logger.log(error_msg, level='ERROR')
            return None

    def Generate(self, prompt=None, model=None, output_dir=None, aspect_ratio=None, resolution=None, completion_callback=None):
        """
        Generate an image using the AIMLAPI asynchronously.
        Can be called from the pulse button (no args) or programmatically (with args).
        
        Args:
            prompt (str, optional): Text prompt. If None, uses op("PROMPT").text from the PROMPT operator
            model (str, optional): Model name. If None, uses self.ownerComp.par.Model
            output_dir (str, optional): Output directory. If None, uses op.AOP.par.Outputdir (global setting)
            aspect_ratio (str, optional): Aspect ratio. If None, uses self.ownerComp.par.Aspectratio
            resolution (str, optional): Resolution. If None, uses self.ownerComp.par.Resolution
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
        
        model = model if model is not None else self.ownerComp.par.Model.eval()
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
        coro = self._generate_image_async(prompt, model, output_dir, aspect_ratio, resolution)
        
        # Run it through the async manager
        task_id = self.tdAsyncIO.ext.AsyncIOManager.Run(
            coro,
            description=f"Generate Image: {prompt[:50]}...",
            info={'prompt': prompt, 'model': model, 'output_dir': output_dir},
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
            
            self.logger.log("Stopped all active image generation tasks", level='INFO')
        except Exception as e:
            self.logger.log(f"Error stopping generation tasks: {e}", level='ERROR')
    
    def _update_active_status(self):
        """Update the Active parameter based on whether there are active tasks."""
        active_tasks_count = self.tdAsyncIO.ext.AsyncIOManager.GetActiveTasksCount()
        self.ownerComp.par.Active = active_tasks_count > 0
        
        
