"""
Upload Handler for AI Avatar Platform

This module handles file uploads from the UI and passes them to the DataHandler.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import uuid
import zipfile
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('upload_handler')

# Import DataHandler
from data_handler import DataHandler, SUPPORTED_IMAGE_FORMATS, SUPPORTED_AUDIO_FORMATS, SUPPORTED_LORA_FORMATS, SUPPORTED_TEXT_FORMATS

class UploadHandler:
    """Handles file uploads from the UI and manages temporary storage."""
    
    def __init__(self, data_handler: DataHandler = None, temp_dir: str = None):
        """
        Initialize the UploadHandler.
        
        Args:
            data_handler: DataHandler instance for processing uploads
            temp_dir: Directory for temporary file storage
        """
        if data_handler is None:
            self.data_handler = DataHandler()
        else:
            self.data_handler = data_handler
        
        if temp_dir is None:
            self.temp_dir = Path(tempfile.gettempdir()) / "avatar_platform_uploads"
        else:
            self.temp_dir = Path(temp_dir)
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"UploadHandler initialized with temp directory: {self.temp_dir}")
    
    def handle_upload(self, file_data: bytes, filename: str, user_id: str, 
                     data_type: str) -> Tuple[bool, str, Dict]:
        """
        Handle a file upload from the UI.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: Unique identifier for the user
            data_type: Type of data ('appearance', 'voice', or 'communication')
            
        Returns:
            Tuple of (success, message, metadata)
        """
        # Create user temp directory
        user_temp_dir = self.temp_dir / user_id
        user_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to temp directory
        file_path = user_temp_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"Saved uploaded file to {file_path}")
        
        # Process based on data type
        if data_type == 'appearance':
            return self._process_appearance_upload(file_path, user_id)
        elif data_type == 'voice':
            return self._process_voice_upload(file_path, user_id)
        elif data_type == 'communication':
            return self._process_communication_upload(file_path, user_id)
        else:
            return False, f"Invalid data type: {data_type}", {}
    
    def _process_appearance_upload(self, file_path: Path, user_id: str) -> Tuple[bool, str, Dict]:
        """Process appearance data upload."""
        # Check file type
        if file_path.is_file():
            if file_path.suffix.lower() in SUPPORTED_LORA_FORMATS:
                # It's a LoRA model
                return self.data_handler.process_appearance_data(file_path, user_id)
            elif file_path.suffix.lower() == '.zip':
                # It's a zip file, could contain images
                return self.data_handler.process_appearance_data(file_path, user_id)
            elif file_path.suffix.lower() in SUPPORTED_IMAGE_FORMATS:
                # Single image, not enough for dataset
                return False, "A single image is not sufficient. Please upload a zip file with multiple images or a LoRA model.", {}
            else:
                return False, f"Unsupported file format for appearance data: {file_path.suffix}", {}
        else:
            return False, "Invalid file path", {}
    
    def _process_voice_upload(self, file_path: Path, user_id: str) -> Tuple[bool, str, Dict]:
        """Process voice data upload."""
        # Check file type
        if file_path.is_file():
            if file_path.suffix.lower() in SUPPORTED_AUDIO_FORMATS:
                # Single audio file
                return self.data_handler.process_voice_data(file_path, user_id)
            elif file_path.suffix.lower() == '.zip':
                # Zip file with multiple audio samples
                return self.data_handler.process_voice_data(file_path, user_id)
            else:
                return False, f"Unsupported file format for voice data: {file_path.suffix}", {}
        else:
            return False, "Invalid file path", {}
    
    def _process_communication_upload(self, file_path: Path, user_id: str) -> Tuple[bool, str, Dict]:
        """Process communication data upload."""
        # Check file type
        if file_path.is_file():
            if file_path.suffix.lower() in SUPPORTED_TEXT_FORMATS:
                # Text file
                return self.data_handler.process_communication_data(file_path, user_id)
            elif file_path.suffix.lower() == '.zip':
                # Zip file with multiple text files
                return self.data_handler.process_communication_data(file_path, user_id)
            else:
                return False, f"Unsupported file format for communication data: {file_path.suffix}", {}
        else:
            return False, "Invalid file path", {}
    
    def cleanup_temp_files(self, user_id: str = None) -> bool:
        """
        Clean up temporary files.
        
        Args:
            user_id: If provided, only clean up files for this user
            
        Returns:
            Success status
        """
        try:
            if user_id:
                user_temp_dir = self.temp_dir / user_id
                if user_temp_dir.exists():
                    shutil.rmtree(user_temp_dir)
                    logger.info(f"Cleaned up temp files for user {user_id}")
            else:
                # Clean up all temp files
                for item in self.temp_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                logger.info("Cleaned up all temp files")
            
            return True
        
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
            return False


# Example usage
if __name__ == "__main__":
    data_handler = DataHandler()
    upload_handler = UploadHandler(data_handler)
    print("Upload Handler initialized and ready for use.")
