"""
File upload processing module for the AI Avatar Platform.

This module handles the processing of uploaded files for appearance, voice, and communication.
"""

import os
import json
import shutil
import logging
import zipfile
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('upload_processor')

class UploadProcessor:
    """
    Processor for uploaded files.
    
    This class handles the processing of uploaded files for appearance, voice, and communication,
    including validation, extraction, and storage.
    """
    
    def __init__(self, base_dir=None):
        """
        Initialize the UploadProcessor.
        
        Args:
            base_dir: Base directory for the platform
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        
        # Create directories if they don't exist
        self._create_directories()
        
        logger.info(f"UploadProcessor initialized with base directory: {self.base_dir}")
    
    def _create_directories(self):
        """Create necessary directories."""
        # Data directories
        (self.data_dir / 'appearance').mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'voice').mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'communication').mkdir(parents=True, exist_ok=True)
        
        # Models directories
        (self.models_dir / 'appearance').mkdir(parents=True, exist_ok=True)
        (self.models_dir / 'voice').mkdir(parents=True, exist_ok=True)
        (self.models_dir / 'communication').mkdir(parents=True, exist_ok=True)
    
    def process_appearance_upload(self, user_id, files):
        """
        Process appearance upload.
        
        Args:
            user_id: User ID
            files: Uploaded files
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing appearance upload for user: {user_id}")
        
        # Create user directories
        user_data_dir = self.data_dir / 'appearance' / user_id
        user_models_dir = self.models_dir / 'appearance' / user_id
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results
        results = {
            "success": True,
            "message": "Appearance data processed successfully",
            "processed_files": [],
            "errors": []
        }
        
        try:
            # Process each file
            for file in files:
                filename = secure_filename(file.filename)
                file_path = user_data_dir / filename
                
                # Save file
                file.save(str(file_path))
                logger.info(f"Saved file: {file_path}")
                
                # Check file type
                if filename.endswith(('.safetensors', '.ckpt', '.pt', '.bin')):
                    # Handle LoRA model
                    model_path = user_models_dir / 'model.safetensors'
                    shutil.copy(str(file_path), str(model_path))
                    logger.info(f"Copied LoRA model to: {model_path}")
                    
                    # Create model info file
                    model_info = {
                        "type": "lora",
                        "filename": filename,
                        "original_path": str(file_path)
                    }
                    with open(str(user_models_dir / 'model_info.json'), 'w') as f:
                        json.dump(model_info, f)
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "lora_model",
                        "path": str(file_path)
                    })
                elif filename.endswith(('.zip')):
                    # Handle zip file (assumed to be image dataset)
                    extract_dir = user_data_dir / 'images'
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Extract zip file
                    with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
                        zip_ref.extractall(str(extract_dir))
                    
                    # Count extracted images
                    image_count = len([f for f in extract_dir.glob('*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')])
                    
                    # Create dataset info file
                    dataset_info = {
                        "type": "image_dataset",
                        "image_count": image_count,
                        "path": str(extract_dir)
                    }
                    with open(str(user_models_dir / 'dataset_info.json'), 'w') as f:
                        json.dump(dataset_info, f)
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "image_dataset",
                        "image_count": image_count,
                        "path": str(extract_dir)
                    })
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # Handle individual image
                    images_dir = user_data_dir / 'images'
                    images_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Copy image to images directory
                    image_path = images_dir / filename
                    shutil.copy(str(file_path), str(image_path))
                    
                    # Count total images
                    image_count = len([f for f in images_dir.glob('*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')])
                    
                    # Create or update dataset info file
                    dataset_info_path = user_models_dir / 'dataset_info.json'
                    if dataset_info_path.exists():
                        with open(str(dataset_info_path), 'r') as f:
                            dataset_info = json.load(f)
                        dataset_info["image_count"] = image_count
                    else:
                        dataset_info = {
                            "type": "image_dataset",
                            "image_count": image_count,
                            "path": str(images_dir)
                        }
                    
                    with open(str(dataset_info_path), 'w') as f:
                        json.dump(dataset_info, f)
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "image",
                        "path": str(image_path)
                    })
                else:
                    # Unsupported file type
                    results["errors"].append({
                        "filename": filename,
                        "error": "Unsupported file type"
                    })
                    logger.warning(f"Unsupported file type: {filename}")
            
            # Create placeholder model file if none exists
            if not (user_models_dir / 'model.safetensors').exists() and not (user_models_dir / 'dataset_info.json').exists():
                # If we have at least 10 images, create a dataset info file
                images_dir = user_data_dir / 'images'
                if images_dir.exists():
                    image_count = len([f for f in images_dir.glob('*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')])
                    if image_count >= 10:
                        dataset_info = {
                            "type": "image_dataset",
                            "image_count": image_count,
                            "path": str(images_dir)
                        }
                        with open(str(user_models_dir / 'dataset_info.json'), 'w') as f:
                            json.dump(dataset_info, f)
                        
                        logger.info(f"Created dataset info file with {image_count} images")
                    else:
                        results["message"] = f"Insufficient images: {image_count}/10 minimum required"
                        results["success"] = False
            
            # Check if we have any valid appearance data
            if not (user_models_dir / 'model.safetensors').exists() and not (user_models_dir / 'dataset_info.json').exists():
                results["message"] = "No valid appearance data found"
                results["success"] = False
        
        except Exception as e:
            logger.error(f"Error processing appearance upload: {e}")
            results["success"] = False
            results["message"] = f"Error processing appearance upload: {str(e)}"
        
        return results
    
    def process_voice_upload(self, user_id, files):
        """
        Process voice upload.
        
        Args:
            user_id: User ID
            files: Uploaded files
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing voice upload for user: {user_id}")
        
        # Create user directories
        user_data_dir = self.data_dir / 'voice' / user_id
        user_models_dir = self.models_dir / 'voice' / user_id
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results
        results = {
            "success": True,
            "message": "Voice data processed successfully",
            "processed_files": [],
            "errors": [],
            "total_duration": 0
        }
        
        try:
            # Process each file
            for file in files:
                filename = secure_filename(file.filename)
                file_path = user_data_dir / filename
                
                # Save file
                file.save(str(file_path))
                logger.info(f"Saved file: {file_path}")
                
                # Check file type
                if filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
                    # Handle audio file
                    # In a production version, we would analyze the audio duration here
                    # For the prototype, we'll assume each file is 10 seconds
                    duration = 10  # seconds
                    results["total_duration"] += duration
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "audio",
                        "duration": duration,
                        "path": str(file_path)
                    })
                elif filename.endswith(('.zip')):
                    # Handle zip file (assumed to be audio dataset)
                    extract_dir = user_data_dir / 'audio'
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Extract zip file
                    with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
                        zip_ref.extractall(str(extract_dir))
                    
                    # Count extracted audio files
                    audio_files = [f for f in extract_dir.glob('*') if f.suffix.lower() in ('.wav', '.mp3', '.ogg', '.flac')]
                    audio_count = len(audio_files)
                    
                    # In a production version, we would analyze the audio duration here
                    # For the prototype, we'll assume each file is 10 seconds
                    total_duration = audio_count * 10  # seconds
                    results["total_duration"] += total_duration
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "audio_dataset",
                        "audio_count": audio_count,
                        "total_duration": total_duration,
                        "path": str(extract_dir)
                    })
                else:
                    # Unsupported file type
                    results["errors"].append({
                        "filename": filename,
                        "error": "Unsupported file type"
                    })
                    logger.warning(f"Unsupported file type: {filename}")
            
            # Create voice model info file
            if results["total_duration"] >= 60:  # At least 1 minute of audio
                # Create model info file
                model_info = {
                    "type": "voice_model",
                    "total_duration": results["total_duration"],
                    "file_count": len(results["processed_files"]),
                    "data_path": str(user_data_dir)
                }
                with open(str(user_models_dir / 'model_info.json'), 'w') as f:
                    json.dump(model_info, f)
                
                # Create placeholder model file
                with open(str(user_models_dir / 'model.bin'), 'w') as f:
                    f.write("placeholder")
                
                logger.info(f"Created voice model info with {results['total_duration']} seconds of audio")
            else:
                results["message"] = f"Insufficient audio: {results['total_duration']}/60 seconds minimum required"
                results["success"] = False
        
        except Exception as e:
            logger.error(f"Error processing voice upload: {e}")
            results["success"] = False
            results["message"] = f"Error processing voice upload: {str(e)}"
        
        return results
    
    def process_communication_upload(self, user_id, files):
        """
        Process communication upload.
        
        Args:
            user_id: User ID
            files: Uploaded files
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing communication upload for user: {user_id}")
        
        # Create user directories
        user_data_dir = self.data_dir / 'communication' / user_id
        user_models_dir = self.models_dir / 'communication' / user_id
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results
        results = {
            "success": True,
            "message": "Communication data processed successfully",
            "processed_files": [],
            "errors": [],
            "sample_count": 0,
            "dialog_samples": []
        }
        
        try:
            # Process each file
            for file in files:
                filename = secure_filename(file.filename)
                file_path = user_data_dir / filename
                
                # Save file
                file.save(str(file_path))
                logger.info(f"Saved file: {file_path}")
                
                # Check file type
                if filename.endswith(('.txt', '.json')):
                    # Handle text file
                    with open(str(file_path), 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse content
                    if filename.endswith('.json'):
                        try:
                            # Try to parse as JSON
                            dialog_data = json.loads(content)
                            
                            # Check if it's an array
                            if isinstance(dialog_data, list):
                                sample_count = len(dialog_data)
                                dialog_samples = dialog_data
                            else:
                                # If it's an object, try to extract samples
                                if "samples" in dialog_data:
                                    sample_count = len(dialog_data["samples"])
                                    dialog_samples = dialog_data["samples"]
                                else:
                                    # Treat each key-value pair as a sample
                                    sample_count = len(dialog_data)
                                    dialog_samples = [f"{k}: {v}" for k, v in dialog_data.items()]
                        except json.JSONDecodeError:
                            # If JSON parsing fails, treat as plain text
                            lines = content.strip().split('\n')
                            sample_count = len(lines)
                            dialog_samples = lines
                    else:
                        # Plain text file
                        lines = content.strip().split('\n')
                        sample_count = len(lines)
                        dialog_samples = lines
                    
                    results["sample_count"] += sample_count
                    results["dialog_samples"].extend(dialog_samples)
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "text",
                        "sample_count": sample_count,
                        "path": str(file_path)
                    })
                elif filename.endswith(('.zip')):
                    # Handle zip file (assumed to be text dataset)
                    extract_dir = user_data_dir / 'text'
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Extract zip file
                    with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
                        zip_ref.extractall(str(extract_dir))
                    
                    # Process extracted text files
                    text_files = [f for f in extract_dir.glob('*') if f.suffix.lower() in ('.txt', '.json')]
                    
                    for text_file in text_files:
                        with open(str(text_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Parse content (simplified for prototype)
                        lines = content.strip().split('\n')
                        sample_count = len(lines)
                        dialog_samples = lines
                        
                        results["sample_count"] += sample_count
                        results["dialog_samples"].extend(dialog_samples)
                    
                    results["processed_files"].append({
                        "filename": filename,
                        "type": "text_dataset",
                        "file_count": len(text_files),
                        "sample_count": results["sample_count"],
                        "path": str(extract_dir)
                    })
                else:
                    # Unsupported file type
                    results["errors"].append({
                        "filename": filename,
                        "error": "Unsupported file type"
                    })
                    logger.warning(f"Unsupported file type: {filename}")
            
            # Create communication model info file
            if results["sample_count"] >= 10:  # At least 10 dialog samples
                # Create model info file
                model_info = {
                    "type": "communication_model",
                    "sample_count": results["sample_count"],
                    "file_count": len(results["processed_files"]),
                    "data_path": str(user_data_dir)
                }
                with open(str(user_models_dir / 'model_info.json'), 'w') as f:
                    json.dump(model_info, f)
                
                # Create style file with dialog samples
                with open(str(user_models_dir / 'style.txt'), 'w', encoding='utf-8') as f:
                    f.write("\n".join(results["dialog_samples"]))
                
                # Create placeholder model file
                with open(str(user_models_dir / 'model.bin'), 'w') as f:
                    f.write("placeholder")
                
                logger.info(f"Created communication model info with {results['sample_count']} dialog samples")
            else:
                results["message"] = f"Insufficient dialog samples: {results['sample_count']}/10 minimum required"
                results["success"] = False
        
        except Exception as e:
            logger.error(f"Error processing communication upload: {e}")
            results["success"] = False
            results["message"] = f"Error processing communication upload: {str(e)}"
        
        return results
    
    def get_upload_status(self, user_id):
        """
        Get upload status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with upload status
        """
        logger.info(f"Getting upload status for user: {user_id}")
        
        # Initialize status
        status = {
            "appearance": {
                "uploaded": False,
                "valid": False,
                "type": None,
                "details": {}
            },
            "voice": {
                "uploaded": False,
                "valid": False,
                "type": None,
                "details": {}
            },
            "communication": {
                "uploaded": False,
                "valid": False,
                "type": None,
                "details": {}
            }
        }
        
        try:
            # Check appearance
            appearance_model_dir = self.models_dir / 'appearance' / user_id
            if appearance_model_dir.exists():
                status["appearance"]["uploaded"] = True
                
                # Check for model file
                if (appearance_model_dir / 'model.safetensors').exists():
                    status["appearance"]["valid"] = True
                    status["appearance"]["type"] = "lora_model"
                    
                    # Get model info
                    if (appearance_model_dir / 'model_info.json').exists():
                        with open(str(appearance_model_dir / 'model_info.json'), 'r') as f:
                            status["appearance"]["details"] = json.load(f)
                
                # Check for dataset info
                elif (appearance_model_dir / 'dataset_info.json').exists():
                    with open(str(appearance_model_dir / 'dataset_info.json'), 'r') as f:
                        dataset_info = json.load(f)
                    
                    if dataset_info.get("image_count", 0) >= 10:
                        status["appearance"]["valid"] = True
                        status["appearance"]["type"] = "image_dataset"
                        status["appearance"]["details"] = dataset_info
            
            # Check voice
            voice_model_dir = self.models_dir / 'voice' / user_id
            if voice_model_dir.exists():
                status["voice"]["uploaded"] = True
                
                # Check for model info
                if (voice_model_dir / 'model_info.json').exists() and (voice_model_dir / 'model.bin').exists():
                    with open(str(voice_model_dir / 'model_info.json'), 'r') as f:
                        model_info = json.load(f)
                    
                    if model_info.get("total_duration", 0) >= 60:
                        status["voice"]["valid"] = True
                        status["voice"]["type"] = "voice_model"
                        status["voice"]["details"] = model_info
            
            # Check communication
            communication_model_dir = self.models_dir / 'communication' / user_id
            if communication_model_dir.exists():
                status["communication"]["uploaded"] = True
                
                # Check for model info
                if (communication_model_dir / 'model_info.json').exists() and (communication_model_dir / 'model.bin').exists():
                    with open(str(communication_model_dir / 'model_info.json'), 'r') as f:
                        model_info = json.load(f)
                    
                    if model_info.get("sample_count", 0) >= 10:
                        status["communication"]["valid"] = True
                        status["communication"]["type"] = "communication_model"
                        status["communication"]["details"] = model_info
        
        except Exception as e:
            logger.error(f"Error getting upload status: {e}")
        
        return status
