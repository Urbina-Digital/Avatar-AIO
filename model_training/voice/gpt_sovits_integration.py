"""
GPT-SoVITS Integration Module for the AI Avatar Platform.

This module integrates GPT-SoVITS voice models with the platform's voice synthesis system.
"""

import os
import json
import logging
import subprocess
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gpt_sovits_integration')

class GPTSoVITSIntegration:
    """
    Integration for GPT-SoVITS voice models.
    
    This class handles the integration of user-trained GPT-SoVITS voice models
    with the AI Avatar Platform's voice synthesis system.
    """
    
    def __init__(self, base_dir=None, gpt_sovits_path=None):
        """
        Initialize the GPTSoVITSIntegration.
        
        Args:
            base_dir: Base directory for the platform
            gpt_sovits_path: Path to GPT-SoVITS installation
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / 'models'
        self.data_dir = self.base_dir / 'data'
        
        # Path to GPT-SoVITS installation
        self.gpt_sovits_path = Path(gpt_sovits_path) if gpt_sovits_path else None
        
        logger.info(f"GPTSoVITSIntegration initialized with base directory: {self.base_dir}")
        if self.gpt_sovits_path:
            logger.info(f"GPT-SoVITS path: {self.gpt_sovits_path}")
        else:
            logger.warning("GPT-SoVITS path not specified. You'll need to set it before using inference.")
    
    def import_model(self, user_id, gpt_checkpoint_path, sovits_checkpoint_path, config_path=None, model_name=None):
        """
        Import a GPT-SoVITS model into the platform.
        
        Args:
            user_id: User ID
            gpt_checkpoint_path: Path to GPT checkpoint file
            sovits_checkpoint_path: Path to SoVITS checkpoint file
            config_path: Path to config file (optional)
            model_name: Name for the model (optional)
            
        Returns:
            Dictionary with import status
        """
        logger.info(f"Importing GPT-SoVITS model for user {user_id}")
        
        try:
            # Create model directory
            model_dir = self.models_dir / 'voice' / user_id / 'gpt_sovits'
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Set model name
            if not model_name:
                model_name = f"GPT-SoVITS-{user_id}"
            
            # Copy checkpoint files
            gpt_dest = model_dir / os.path.basename(gpt_checkpoint_path)
            sovits_dest = model_dir / os.path.basename(sovits_checkpoint_path)
            
            shutil.copy2(gpt_checkpoint_path, gpt_dest)
            shutil.copy2(sovits_checkpoint_path, sovits_dest)
            
            logger.info(f"Copied GPT checkpoint to: {gpt_dest}")
            logger.info(f"Copied SoVITS checkpoint to: {sovits_dest}")
            
            # Copy config file if provided
            config_dest = None
            if config_path and os.path.exists(config_path):
                config_dest = model_dir / os.path.basename(config_path)
                shutil.copy2(config_path, config_dest)
                logger.info(f"Copied config file to: {config_dest}")
            
            # Create model info file
            model_info = {
                "model_type": "gpt_sovits",
                "model_name": model_name,
                "gpt_checkpoint": str(gpt_dest),
                "sovits_checkpoint": str(sovits_dest),
                "config_file": str(config_dest) if config_dest else None,
                "imported_at": str(Path.ctime(Path.cwd()))
            }
            
            with open(str(model_dir / 'model_info.json'), 'w') as f:
                json.dump(model_info, f, indent=4)
            
            # Create a flag file to indicate this is a GPT-SoVITS model
            with open(str(model_dir / 'gpt_sovits_model.flag'), 'w') as f:
                f.write("This is a GPT-SoVITS model")
            
            return {
                "success": True,
                "message": f"Successfully imported GPT-SoVITS model: {model_name}",
                "model_dir": str(model_dir),
                "model_info": model_info
            }
        
        except Exception as e:
            logger.error(f"Error importing GPT-SoVITS model: {e}")
            return {
                "success": False,
                "message": f"Error importing GPT-SoVITS model: {str(e)}"
            }
    
    def synthesize_speech(self, user_id, text, output_path=None, reference_audio=None, 
                          prompt_text=None, prompt_language="en", text_language="en"):
        """
        Synthesize speech using GPT-SoVITS model.
        
        Args:
            user_id: User ID
            text: Text to synthesize
            output_path: Path to save output audio (optional)
            reference_audio: Path to reference audio file (optional)
            prompt_text: Text of the reference audio (optional)
            prompt_language: Language of the prompt (optional)
            text_language: Language of the text to synthesize (optional)
            
        Returns:
            Path to synthesized audio file or None if synthesis failed
        """
        logger.info(f"Synthesizing speech with GPT-SoVITS for user {user_id}: '{text[:50]}...'")
        
        try:
            # Check if GPT-SoVITS path is set
            if not self.gpt_sovits_path:
                logger.error("GPT-SoVITS path not set")
                return None
            
            # Check if model exists
            model_dir = self.models_dir / 'voice' / user_id / 'gpt_sovits'
            if not model_dir.exists():
                logger.error(f"GPT-SoVITS model directory not found: {model_dir}")
                return None
            
            # Load model info
            model_info_path = model_dir / 'model_info.json'
            if not model_info_path.exists():
                logger.error(f"Model info file not found: {model_info_path}")
                return None
            
            with open(str(model_info_path), 'r') as f:
                model_info = json.load(f)
            
            # Get checkpoint paths
            gpt_checkpoint = model_info.get("gpt_checkpoint")
            sovits_checkpoint = model_info.get("sovits_checkpoint")
            config_file = model_info.get("config_file")
            
            if not gpt_checkpoint or not sovits_checkpoint:
                logger.error("Missing checkpoint paths in model info")
                return None
            
            # Create output directory if not specified
            if not output_path:
                output_dir = self.data_dir / 'voice' / user_id / 'generated'
                output_dir.mkdir(parents=True, exist_ok=True)
                
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
                output_path = output_dir / f"gpt_sovits_{text_hash}.wav"
            
            # Determine inference method based on available components
            if os.path.exists(os.path.join(self.gpt_sovits_path, "inference_webui.py")):
                # Use web UI API if available
                return self._synthesize_with_webui(
                    text, output_path, gpt_checkpoint, sovits_checkpoint, 
                    reference_audio, prompt_text, prompt_language, text_language
                )
            else:
                # Use command-line inference
                return self._synthesize_with_cli(
                    text, output_path, gpt_checkpoint, sovits_checkpoint, config_file,
                    reference_audio, prompt_text, prompt_language, text_language
                )
        
        except Exception as e:
            logger.error(f"Error synthesizing speech with GPT-SoVITS: {e}")
            return None
    
    def _synthesize_with_webui(self, text, output_path, gpt_checkpoint, sovits_checkpoint, 
                              reference_audio=None, prompt_text=None, prompt_language="en", text_language="en"):
        """
        Synthesize speech using GPT-SoVITS web UI API.
        
        Args:
            text: Text to synthesize
            output_path: Path to save output audio
            gpt_checkpoint: Path to GPT checkpoint
            sovits_checkpoint: Path to SoVITS checkpoint
            reference_audio: Path to reference audio file (optional)
            prompt_text: Text of the reference audio (optional)
            prompt_language: Language of the prompt (optional)
            text_language: Language of the text to synthesize (optional)
            
        Returns:
            Path to synthesized audio file or None if synthesis failed
        """
        logger.info("Synthesizing speech with GPT-SoVITS web UI API")
        
        try:
            import requests
            
            # Prepare API request
            url = "http://localhost:7860/api/predict"
            
            payload = {
                "fn_index": 0,
                "data": [
                    text,
                    text_language,
                    gpt_checkpoint,
                    sovits_checkpoint,
                    reference_audio if reference_audio else "",
                    prompt_text if prompt_text else "",
                    prompt_language,
                    0.2,  # Top K
                    0.7,  # Top P
                    1.0,  # Temperature
                    1.0   # Speak speed
                ]
            }
            
            # Make API request
            response = requests.post(url, json=payload)
            
            # Check response status
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                
                # Extract audio data
                if "data" in response_data and len(response_data["data"]) > 0:
                    audio_path = response_data["data"][0]
                    
                    # Copy audio file to output path
                    shutil.copy2(audio_path, output_path)
                    
                    logger.info(f"Synthesized speech saved to: {output_path}")
                    return output_path
                else:
                    logger.error("No audio data in API response")
                    return None
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error synthesizing speech with web UI API: {e}")
            return None
    
    def _synthesize_with_cli(self, text, output_path, gpt_checkpoint, sovits_checkpoint, config_file=None,
                            reference_audio=None, prompt_text=None, prompt_language="en", text_language="en"):
        """
        Synthesize speech using GPT-SoVITS command-line interface.
        
        Args:
            text: Text to synthesize
            output_path: Path to save output audio
            gpt_checkpoint: Path to GPT checkpoint
            sovits_checkpoint: Path to SoVITS checkpoint
            config_file: Path to config file (optional)
            reference_audio: Path to reference audio file (optional)
            prompt_text: Text of the reference audio (optional)
            prompt_language: Language of the prompt (optional)
            text_language: Language of the text to synthesize (optional)
            
        Returns:
            Path to synthesized audio file or None if synthesis failed
        """
        logger.info("Synthesizing speech with GPT-SoVITS CLI")
        
        try:
            # Prepare command
            cmd = [
                "python",
                os.path.join(self.gpt_sovits_path, "inference.py"),
                "--text", text,
                "--text_language", text_language,
                "--gpt_path", gpt_checkpoint,
                "--sovits_path", sovits_checkpoint,
                "--output_path", str(output_path)
            ]
            
            # Add optional arguments
            if config_file:
                cmd.extend(["--config_path", config_file])
            
            if reference_audio:
                cmd.extend(["--reference_audio", reference_audio])
            
            if prompt_text:
                cmd.extend(["--prompt_text", prompt_text])
                cmd.extend(["--prompt_language", prompt_language])
            
            # Run command
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check result
            if result.returncode == 0:
                logger.info(f"Synthesized speech saved to: {output_path}")
                return output_path
            else:
                logger.error(f"Command failed with return code: {result.returncode}")
                logger.error(f"Error: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error synthesizing speech with CLI: {e}")
            return None
    
    def get_model_info(self, user_id):
        """
        Get information about the user's GPT-SoVITS model.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with model information or None if not found
        """
        logger.info(f"Getting GPT-SoVITS model info for user {user_id}")
        
        try:
            # Check if model exists
            model_dir = self.models_dir / 'voice' / user_id / 'gpt_sovits'
            model_info_path = model_dir / 'model_info.json'
            
            if not model_info_path.exists():
                logger.warning(f"Model info file not found: {model_info_path}")
                return None
            
            # Load model info
            with open(str(model_info_path), 'r') as f:
                model_info = json.load(f)
            
            return model_info
        
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    def list_available_models(self, user_id=None):
        """
        List available GPT-SoVITS models.
        
        Args:
            user_id: User ID (optional, if None, list all models)
            
        Returns:
            List of available models
        """
        logger.info(f"Listing available GPT-SoVITS models for user {user_id if user_id else 'all'}")
        
        models = []
        
        try:
            if user_id:
                # List models for specific user
                model_dir = self.models_dir / 'voice' / user_id / 'gpt_sovits'
                if model_dir.exists():
                    model_info_path = model_dir / 'model_info.json'
                    if model_info_path.exists():
                        with open(str(model_info_path), 'r') as f:
                            model_info = json.load(f)
                        models.append(model_info)
            else:
                # List all models
                voice_dir = self.models_dir / 'voice'
                if voice_dir.exists():
                    for user_dir in voice_dir.iterdir():
                        if user_dir.is_dir():
                            gpt_sovits_dir = user_dir / 'gpt_sovits'
                            if gpt_sovits_dir.exists():
                                model_info_path = gpt_sovits_dir / 'model_info.json'
                                if model_info_path.exists():
                                    with open(str(model_info_path), 'r') as f:
                                        model_info = json.load(f)
                                    models.append(model_info)
        
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        
        return models
    
    def set_gpt_sovits_path(self, path):
        """
        Set the path to GPT-SoVITS installation.
        
        Args:
            path: Path to GPT-SoVITS installation
            
        Returns:
            Success status
        """
        try:
            self.gpt_sovits_path = Path(path)
            logger.info(f"Set GPT-SoVITS path to: {self.gpt_sovits_path}")
            return True
        except Exception as e:
            logger.error(f"Error setting GPT-SoVITS path: {e}")
            return False
