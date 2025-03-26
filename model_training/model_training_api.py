"""
Model Training API Module for AI Avatar Platform

This module provides a unified API interface for the model training components,
allowing the frontend to interact with the training pipelines.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('model_training_api')

# Import model training components
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'appearance'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voice'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'communication'))

from appearance.appearance_trainer import AppearanceModelTrainer
from voice.voice_trainer import VoiceModelTrainer
from communication.communication_trainer import CommunicationModelTrainer

class ModelTrainingAPI:
    """API interface for model training components."""
    
    def __init__(self, base_dir: str = None, output_dir: str = None):
        """
        Initialize the ModelTrainingAPI.
        
        Args:
            base_dir: Base directory for input data
            output_dir: Directory for trained models and outputs
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
        
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize trainers
        self.appearance_trainer = AppearanceModelTrainer(base_dir, output_dir)
        self.voice_trainer = VoiceModelTrainer(base_dir, output_dir)
        self.communication_trainer = CommunicationModelTrainer(base_dir, output_dir)
        
        logger.info(f"ModelTrainingAPI initialized with base directory: {self.base_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def train_appearance_model(self, user_id: str, data_path: Union[str, Path], 
                              is_lora: bool = False) -> Dict:
        """
        Train an appearance model.
        
        Args:
            user_id: Unique identifier for the user
            data_path: Path to the LoRA model or directory of images
            is_lora: Whether the data is a LoRA model
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Training appearance model for user {user_id}")
        
        try:
            if is_lora:
                success, message, metadata = self.appearance_trainer.train_from_lora(
                    user_id, data_path
                )
            else:
                # If it's a directory, get all image paths
                data_path = Path(data_path)
                if data_path.is_dir():
                    image_paths = []
                    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        image_paths.extend(list(data_path.glob(f"**/*{ext}")))
                    
                    success, message, metadata = self.appearance_trainer.train_from_images(
                        user_id, image_paths
                    )
                else:
                    return {
                        "success": False,
                        "message": f"Invalid data path: {data_path}. Must be a LoRA model file or directory of images.",
                        "model_type": "appearance"
                    }
            
            return {
                "success": success,
                "message": message,
                "model_type": "appearance",
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error training appearance model: {e}")
            return {
                "success": False,
                "message": f"Error training appearance model: {str(e)}",
                "model_type": "appearance"
            }
    
    def train_voice_model(self, user_id: str, audio_dir: Union[str, Path]) -> Dict:
        """
        Train a voice model.
        
        Args:
            user_id: Unique identifier for the user
            audio_dir: Directory containing audio samples
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Training voice model for user {user_id}")
        
        try:
            audio_dir = Path(audio_dir)
            if not audio_dir.is_dir():
                return {
                    "success": False,
                    "message": f"Invalid audio directory: {audio_dir}",
                    "model_type": "voice"
                }
            
            # Get all audio files
            audio_paths = []
            for ext in ['.wav', '.mp3', '.flac', '.ogg']:
                audio_paths.extend(list(audio_dir.glob(f"**/*{ext}")))
            
            if not audio_paths:
                return {
                    "success": False,
                    "message": f"No audio files found in directory: {audio_dir}",
                    "model_type": "voice"
                }
            
            success, message, metadata = self.voice_trainer.train_voice_model(
                user_id, audio_paths
            )
            
            return {
                "success": success,
                "message": message,
                "model_type": "voice",
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error training voice model: {e}")
            return {
                "success": False,
                "message": f"Error training voice model: {str(e)}",
                "model_type": "voice"
            }
    
    def train_communication_model(self, user_id: str, dialog_path: Union[str, Path]) -> Dict:
        """
        Train a communication model.
        
        Args:
            user_id: Unique identifier for the user
            dialog_path: Path to the dialog samples file
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Training communication model for user {user_id}")
        
        try:
            dialog_path = Path(dialog_path)
            if not dialog_path.is_file():
                return {
                    "success": False,
                    "message": f"Invalid dialog file: {dialog_path}",
                    "model_type": "communication"
                }
            
            success, message, metadata = self.communication_trainer.train_language_model(
                user_id, dialog_path
            )
            
            return {
                "success": success,
                "message": message,
                "model_type": "communication",
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error training communication model: {e}")
            return {
                "success": False,
                "message": f"Error training communication model: {str(e)}",
                "model_type": "communication"
            }
    
    def generate_action_images(self, user_id: str, action: str, frames: int = 5) -> Dict:
        """
        Generate images for a specific action or animation.
        
        Args:
            user_id: Unique identifier for the user
            action: Name of the action to generate
            frames: Number of frames for the animation
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Generating action images for user {user_id}: {action}")
        
        try:
            success, message, metadata = self.appearance_trainer.generate_action_images(
                user_id, action, frames
            )
            
            return {
                "success": success,
                "message": message,
                "action": action,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error generating action images: {e}")
            return {
                "success": False,
                "message": f"Error generating action images: {str(e)}",
                "action": action
            }
    
    def synthesize_speech(self, user_id: str, text: str) -> Dict:
        """
        Synthesize speech from text.
        
        Args:
            user_id: Unique identifier for the user
            text: Text to synthesize
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Synthesizing speech for user {user_id}")
        
        try:
            success, message, metadata = self.voice_trainer.synthesize_speech(
                user_id, text
            )
            
            return {
                "success": success,
                "message": message if not success else "Speech synthesized successfully",
                "text": text,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return {
                "success": False,
                "message": f"Error synthesizing speech: {str(e)}",
                "text": text
            }
    
    def generate_response(self, user_id: str, prompt: str) -> Dict:
        """
        Generate a response to a prompt.
        
        Args:
            user_id: Unique identifier for the user
            prompt: Input prompt
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Generating response for user {user_id}")
        
        try:
            success, message, metadata = self.communication_trainer.generate_response(
                user_id, prompt
            )
            
            return {
                "success": success,
                "message": message if not success else "Response generated successfully",
                "prompt": prompt,
                "response": message if success else "",
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "success": False,
                "message": f"Error generating response: {str(e)}",
                "prompt": prompt
            }
    
    def get_models_summary(self, user_id: str) -> Dict:
        """
        Get a summary of all models for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with models summary
        """
        logger.info(f"Getting models summary for user {user_id}")
        
        try:
            appearance_summary = self.appearance_trainer.get_appearance_summary(user_id)
            voice_summary = self.voice_trainer.get_voice_summary(user_id)
            communication_summary = self.communication_trainer.get_communication_summary(user_id)
            
            return {
                "success": True,
                "message": "Models summary retrieved successfully",
                "user_id": user_id,
                "appearance": appearance_summary,
                "voice": voice_summary,
                "communication": communication_summary,
                "all_trained": (
                    appearance_summary.get("has_data", False) and
                    voice_summary.get("has_model", False) and
                    communication_summary.get("has_model", False)
                )
            }
        
        except Exception as e:
            logger.error(f"Error getting models summary: {e}")
            return {
                "success": False,
                "message": f"Error getting models summary: {str(e)}",
                "user_id": user_id
            }


# Example usage
if __name__ == "__main__":
    api = ModelTrainingAPI()
    print("Model Training API initialized and ready for use.")
