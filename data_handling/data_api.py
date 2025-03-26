"""
Data API Module for AI Avatar Platform

This module provides a RESTful API interface for the data handling components,
allowing the frontend to interact with the data handling system.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_api')

# Import data handling components
from data_handler import DataHandler
from upload_handler import UploadHandler
from data_validator import DataValidator
from sample_data_generator import SampleDataGenerator

class DataAPI:
    """API interface for data handling components."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the DataAPI.
        
        Args:
            base_dir: Base directory for data storage
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        
        self.base_dir = Path(base_dir)
        self.data_handler = DataHandler(base_dir)
        self.upload_handler = UploadHandler(self.data_handler)
        self.sample_generator = SampleDataGenerator(os.path.join(base_dir, 'samples'))
        
        logger.info(f"DataAPI initialized with base directory: {self.base_dir}")
    
    def handle_upload(self, file_data: bytes, filename: str, user_id: str, 
                     data_type: str) -> Dict:
        """
        Handle a file upload from the frontend.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: Unique identifier for the user
            data_type: Type of data ('appearance', 'voice', or 'communication')
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Handling {data_type} upload for user {user_id}: {filename}")
        
        try:
            success, message, metadata = self.upload_handler.handle_upload(
                file_data, filename, user_id, data_type
            )
            
            return {
                "success": success,
                "message": message,
                "data_type": data_type,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error handling upload: {e}")
            return {
                "success": False,
                "message": f"Error processing upload: {str(e)}",
                "data_type": data_type,
                "metadata": {}
            }
    
    def preprocess_data(self, user_id: str, data_type: str) -> Dict:
        """
        Preprocess user data for model training.
        
        Args:
            user_id: Unique identifier for the user
            data_type: Type of data ('appearance', 'voice', or 'communication')
            
        Returns:
            Response dictionary with status and details
        """
        logger.info(f"Preprocessing {data_type} data for user {user_id}")
        
        try:
            if data_type == 'appearance':
                success, message, metadata = self.data_handler.preprocess_images(user_id)
            elif data_type == 'voice':
                success, message, metadata = self.data_handler.preprocess_audio(user_id)
            elif data_type == 'communication':
                success, message, metadata = self.data_handler.preprocess_text(user_id)
            else:
                return {
                    "success": False,
                    "message": f"Invalid data type: {data_type}",
                    "data_type": data_type,
                    "metadata": {}
                }
            
            return {
                "success": success,
                "message": message,
                "data_type": data_type,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            return {
                "success": False,
                "message": f"Error preprocessing data: {str(e)}",
                "data_type": data_type,
                "metadata": {}
            }
    
    def get_user_data_summary(self, user_id: str) -> Dict:
        """
        Get a summary of all data for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with data summary
        """
        logger.info(f"Getting data summary for user {user_id}")
        
        try:
            summary = self.data_handler.get_user_data_summary(user_id)
            return {
                "success": True,
                "message": "Data summary retrieved successfully",
                "summary": summary
            }
        
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {
                "success": False,
                "message": f"Error getting data summary: {str(e)}",
                "summary": {}
            }
    
    def generate_sample_data(self, user_id: str = None) -> Dict:
        """
        Generate sample data for testing.
        
        Args:
            user_id: Optional user ID to associate with the samples
            
        Returns:
            Dictionary with sample data paths
        """
        logger.info(f"Generating sample data for user {user_id if user_id else 'test'}")
        
        try:
            # Generate samples
            samples = self.sample_generator.generate_all_samples()
            
            # If user_id is provided, process the samples for the user
            if user_id:
                # Process appearance data
                appearance_success = False
                for image_path in samples["appearance"]:
                    success, _, _ = self.data_handler.process_appearance_data(image_path, user_id)
                    if success:
                        appearance_success = True
                
                # Process voice data
                voice_success = False
                for audio_path in samples["voice"]:
                    success, _, _ = self.data_handler.process_voice_data(audio_path, user_id)
                    if success:
                        voice_success = True
                
                # Process communication data
                communication_success = False
                for text_path in samples["communication"]:
                    success, _, _ = self.data_handler.process_communication_data(text_path, user_id)
                    if success:
                        communication_success = True
                
                return {
                    "success": True,
                    "message": "Sample data generated and processed successfully",
                    "samples": samples,
                    "processed": {
                        "appearance": appearance_success,
                        "voice": voice_success,
                        "communication": communication_success
                    }
                }
            
            return {
                "success": True,
                "message": "Sample data generated successfully",
                "samples": samples
            }
        
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            return {
                "success": False,
                "message": f"Error generating sample data: {str(e)}",
                "samples": {}
            }
    
    def validate_data(self, user_id: str, data_type: str) -> Dict:
        """
        Validate user data.
        
        Args:
            user_id: Unique identifier for the user
            data_type: Type of data ('appearance', 'voice', or 'communication')
            
        Returns:
            Response dictionary with validation results
        """
        logger.info(f"Validating {data_type} data for user {user_id}")
        
        try:
            summary = self.data_handler.get_user_data_summary(user_id)
            
            if data_type == 'appearance':
                if not summary["appearance"]["has_data"]:
                    return {
                        "success": False,
                        "message": f"No appearance data found for user {user_id}",
                        "data_type": data_type,
                        "validation": {}
                    }
                
                if summary["appearance"]["details"]["type"] == "lora_model":
                    # Validate LoRA model
                    lora_path = summary["appearance"]["details"]["files"][0]
                    success, message, details = DataValidator.validate_lora_model(lora_path)
                else:
                    # Validate image dataset
                    image_paths = summary["appearance"]["details"]["files"]
                    success, message, details = DataValidator.validate_image_dataset(image_paths)
            
            elif data_type == 'voice':
                if not summary["voice"]["has_data"]:
                    return {
                        "success": False,
                        "message": f"No voice data found for user {user_id}",
                        "data_type": data_type,
                        "validation": {}
                    }
                
                # Validate audio dataset
                audio_paths = summary["voice"]["details"]["files"]
                success, message, details = DataValidator.validate_audio_dataset(audio_paths)
            
            elif data_type == 'communication':
                if not summary["communication"]["has_data"]:
                    return {
                        "success": False,
                        "message": f"No communication data found for user {user_id}",
                        "data_type": data_type,
                        "validation": {}
                    }
                
                # Validate text dataset
                text_paths = summary["communication"]["details"]["files"]
                success, message, details = DataValidator.validate_text_dataset(text_paths)
            
            else:
                return {
                    "success": False,
                    "message": f"Invalid data type: {data_type}",
                    "data_type": data_type,
                    "validation": {}
                }
            
            return {
                "success": success,
                "message": message,
                "data_type": data_type,
                "validation": details
            }
        
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {
                "success": False,
                "message": f"Error validating data: {str(e)}",
                "data_type": data_type,
                "validation": {}
            }


# Example usage
if __name__ == "__main__":
    api = DataAPI()
    print("Data API initialized and ready for use.")
