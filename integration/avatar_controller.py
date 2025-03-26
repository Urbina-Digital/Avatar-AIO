"""
Avatar Controller for the AI Avatar Platform.

This module integrates all components of the platform and manages the avatar's behavior.
"""

import os
import json
import logging
import importlib
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('avatar_controller')

class AvatarController:
    """
    Controller for the AI avatar.
    
    This class integrates all components of the platform and manages the avatar's behavior,
    including appearance, voice, and communication.
    """
    
    def __init__(self, base_dir=None, user_id="default", 
                 grok_api_key=None, elevenlabs_api_key=None, stability_api_key=None,
                 force_local=False, force_cloud=False):
        """
        Initialize the AvatarController.
        
        Args:
            base_dir: Base directory for the platform
            user_id: User ID for the avatar
            grok_api_key: API key for Grok
            elevenlabs_api_key: API key for ElevenLabs
            stability_api_key: API key for Stability AI
            force_local: Force local processing
            force_cloud: Force cloud processing
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.user_id = user_id
        self.grok_api_key = grok_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.stability_api_key = stability_api_key
        self.force_local = force_local
        self.force_cloud = force_cloud
        
        # Initialize components
        self.appearance_module = None
        self.voice_module = None
        self.communication_module = None
        self.action_system = None
        
        # Initialize component status
        self.component_status = {
            "appearance": False,
            "voice": False,
            "communication": False,
            "action_system": False
        }
        
        # Load components
        self._load_components()
        
        logger.info(f"AvatarController initialized for user: {user_id}")
        
        # Log component status
        for component, status in self.component_status.items():
            if status:
                logger.info(f"Component loaded: {component}")
            else:
                logger.warning(f"Component not loaded: {component}")
        
        # Check if any components are available
        if not any(self.component_status.values()):
            logger.warning("No components could be loaded. The platform will operate with limited functionality.")
    
    def _load_components(self):
        """Load all components of the platform."""
        try:
            # Try to import appearance module
            try:
                from model_training.appearance.image_generator import ImageGenerator
                self.appearance_module = ImageGenerator(
                    base_dir=self.base_dir,
                    api_key=self.stability_api_key
                )
                self.component_status["appearance"] = True
            except ImportError as e:
                logger.warning(f"Could not import appearance module: {e}")
            
            # Try to import voice module
            try:
                from model_training.voice.voice_synthesizer import VoiceSynthesizer
                self.voice_module = VoiceSynthesizer(
                    base_dir=self.base_dir,
                    elevenlabs_api_key=self.elevenlabs_api_key
                )
                self.component_status["voice"] = True
            except ImportError as e:
                logger.warning(f"Could not import voice module: {e}")
            # In the _load_components method
            try:
                # Try to import GPT-SoVITS integration
                from model_training.voice.gpt_sovits_integration import GPTSoVITSIntegration
                self.gpt_sovits_module = GPTSoVITSIntegration(
                    base_dir=self.base_dir,
                    gpt_sovits_path="models/voice/GPT-SoVITS-v3"  # voice engine path
                )
                self.component_status["gpt_sovits"] = True
            except ImportError as e:
                logger.warning(f"Could not import GPT-SoVITS module: {e}")

            # Try to import communication module
            try:
                from model_training.communication.grok_integration import GrokIntegration
                self.communication_module = GrokIntegration(
                    api_key=self.grok_api_key
                )
                self.component_status["communication"] = True
            except ImportError as e:
                logger.warning(f"Could not import communication module: {e}")
            
            # Try to import action system
            try:
                from action_system.action_system import ActionSystem
                self.action_system = ActionSystem(base_dir=self.base_dir)
                self.component_status["action_system"] = True
            except ImportError as e:
                logger.warning(f"Could not import action system: {e}")
        
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            logger.warning("Some components could not be imported: {e}")
            logger.warning("The platform will operate with limited functionality")
    
    def process_input(self, user_input, input_type="text"):
        """
        Process user input and generate a response.
        
        Args:
            user_input: User input (text or audio file path)
            input_type: Type of input ("text" or "audio")
            
        Returns:
            Dictionary with response data
        """
        logger.info(f"Processing {input_type} input: {user_input[:50] if input_type == 'text' else user_input}")
        
        # Initialize response
        response = {
            "text": None,
            "audio": None,
            "image": None,
            "action": None,
            "error": None
        }
        
        try:
            # Process input based on type
            if input_type == "audio":
                # Convert audio to text (not implemented in prototype)
                # In a production version, this would use speech-to-text
                text_input = f"Audio input: {user_input}"
            else:
                text_input = user_input
            
            # Generate text response
            if self.component_status["communication"] and self.communication_module:
                # Load communication style
                communication_style = self.communication_module.load_communication_style(self.user_id)
                
                # Generate response
                text_response = self.communication_module.generate_response(
                    text_input, 
                    communication_style=communication_style
                )
                response["text"] = text_response
            else:
                # Fallback response
                response["text"] = self._get_fallback_response(text_input)
            
            # Determine action based on input and response
            if self.component_status["action_system"] and self.action_system:
                action = self.action_system.determine_action(text_input, response["text"])
                response["action"] = action
            else:
                # Default action
                response["action"] = "idle"
            
            # GPT-SoVITS integration | Generate audio response
            if self.component_status["gpt_sovits"] and self.gpt_sovits_module:
                audio_path = self.gpt_sovits_module.synthesize_speech(
                    self.user_id, 
                    response["text"]
                )
                if audio_path:
                    response["audio"] = str(audio_path)
            elif self.component_status["voice"] and self.voice_module:
                # Fallback to regular voice synthesis
                audio_path = self.voice_module.synthesize_speech(self.user_id, response["text"])
                if audio_path:
                    response["audio"] = str(audio_path)

            # Generate image based on action
            if self.component_status["appearance"] and self.appearance_module:
                image_path = self.appearance_module.generate_image(
                    self.user_id,
                    f"A person {response['action']}",
                    response["action"]
                )
                if image_path:
                    response["image"] = str(image_path)
        
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            response["error"] = str(e)
            
            # Ensure we have at least a text response
            if not response["text"]:
                response["text"] = "I'm sorry, I encountered an error processing your input."
        
        return response
    
    def _get_fallback_response(self, user_input):
        """
        Get a fallback response when communication module is not available.
        
        Args:
            user_input: User input text
            
        Returns:
            Fallback response text
        """
        # Simple keyword-based response system
        input_lower = user_input.lower()
        
        if "hello" in input_lower or "hi" in input_lower or "hey" in input_lower:
            return "Hello! How can I help you today?"
        
        if "how are you" in input_lower:
            return "I'm doing well, thank you for asking! How about you?"
        
        if "bye" in input_lower or "goodbye" in input_lower:
            return "Goodbye! It was nice chatting with you."
        
        if "thank" in input_lower:
            return "You're welcome! Is there anything else I can help you with?"
        
        if "help" in input_lower:
            return "I can assist you with various tasks. What would you like to know?"
        
        if "name" in input_lower:
            return "I'm your AI avatar assistant. You can customize me to your liking!"
        
        # Default response
        return "That's interesting! Tell me more about that."
    
    def get_component_status(self):
        """
        Get the status of all components.
        
        Returns:
            Dictionary with component status
        """
        return self.component_status
    
    def get_upload_status(self):
        """
        Get the status of user uploads.
        
        Returns:
            Dictionary with upload status
        """
        try:
            # Import upload processor
            from data_handling.upload_processor import UploadProcessor
            
            # Create upload processor
            upload_processor = UploadProcessor(base_dir=self.base_dir)
            
            # Get upload status
            return upload_processor.get_upload_status(self.user_id)
        
        except Exception as e:
            logger.error(f"Error getting upload status: {e}")
            return {
                "appearance": {"uploaded": False, "valid": False},
                "voice": {"uploaded": False, "valid": False},
                "communication": {"uploaded": False, "valid": False}
            }
    
    def process_upload(self, module_type, files):
        """
        Process uploaded files.
        
        Args:
            module_type: Type of module ("appearance", "voice", or "communication")
            files: Uploaded files
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing {module_type} upload for user {self.user_id}")
        
        try:
            # Import upload processor
            from data_handling.upload_processor import UploadProcessor
            
            # Create upload processor
            upload_processor = UploadProcessor(base_dir=self.base_dir)
            
            # Process upload based on module type
            if module_type == "appearance":
                return upload_processor.process_appearance_upload(self.user_id, files)
            elif module_type == "voice":
                return upload_processor.process_voice_upload(self.user_id, files)
            elif module_type == "communication":
                return upload_processor.process_communication_upload(self.user_id, files)
            else:
                logger.warning(f"Unsupported module type: {module_type}")
                return {
                    "success": False,
                    "message": f"Unsupported module type: {module_type}"
                }
        
        except Exception as e:
            logger.error(f"Error processing upload: {e}")
            return {
                "success": False,
                "message": f"Error processing upload: {str(e)}"
            }
    
    def get_available_actions(self):
        """
        Get available actions for the avatar.
        
        Returns:
            Dictionary of action categories and actions
        """
        if self.component_status["appearance"] and self.appearance_module:
            return self.appearance_module.get_available_actions()
        else:
            # Default actions
            return {
                "expressions": ["smiling", "laughing", "winking"],
                "movements": ["waving", "jumping", "dancing"],
                "interactions": ["blowing a kiss", "giving a high five"],
                "activities": ["yoga pose", "eating", "reading"],
                "outfits": ["business outfit", "casual outfit", "formal outfit"]
            }
    
    def trigger_action(self, action):
        """
        Trigger a specific action.
        
        Args:
            action: Action to trigger
            
        Returns:
            Dictionary with action result
        """
        logger.info(f"Triggering action: {action}")
        
        result = {
            "success": True,
            "message": f"Action triggered: {action}",
            "image": None
        }
        
        try:
            # Generate image for action
            if self.component_status["appearance"] and self.appearance_module:
                image_path = self.appearance_module.generate_image(
                    self.user_id,
                    f"A person {action}",
                    action
                )
                if image_path:
                    result["image"] = str(image_path)
        
        except Exception as e:
            logger.error(f"Error triggering action: {e}")
            result["success"] = False
            result["message"] = f"Error triggering action: {str(e)}"
        
        return result
    
    def create_voice_model(self, voice_name=None):
        """
        Create a voice model for the user.
        
        Args:
            voice_name: Name for the voice model
            
        Returns:
            Success status and message
        """
        if self.component_status["voice"] and self.voice_module:
            return self.voice_module.create_voice_model(self.user_id, voice_name)
        else:
            return {
                "success": False,
                "message": "Voice module not available"
            }
    
    def analyze_dialog_samples(self, dialog_samples):
        """
        Analyze dialog samples to extract communication style.
        
        Args:
            dialog_samples: List of dialog samples
            
        Returns:
            Communication style instructions
        """
        if self.component_status["communication"] and self.communication_module:
            return self.communication_module.analyze_dialog_samples(dialog_samples)
        else:
            return "You are a friendly and helpful AI avatar assistant. Keep your responses concise and friendly."
    
    def save_communication_style(self, communication_style):
        """
        Save communication style for the user.
        
        Args:
            communication_style: Communication style instructions
            
        Returns:
            Success status
        """
        if self.component_status["communication"] and self.communication_module:
            return self.communication_module.save_communication_style(self.user_id, communication_style)
        else:
            return False
