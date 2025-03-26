"""
Data Handling Module for AI Avatar Platform

This module handles the upload, validation, and preprocessing of user-provided datasets
for appearance, voice, and communication style.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import numpy as np
from PIL import Image
import cv2
import librosa

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_handler')

# Define constants
MIN_IMAGES_REQUIRED = 10
MIN_AUDIO_DURATION_SECONDS = 60
MIN_TEXT_SAMPLES = 10
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.flac', '.ogg']
SUPPORTED_LORA_FORMATS = ['.safetensors', '.ckpt', '.pt']
SUPPORTED_TEXT_FORMATS = ['.txt', '.json', '.csv']

class DataHandler:
    """Main class for handling data uploads and preprocessing."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the DataHandler.
        
        Args:
            base_dir: Base directory for storing user data
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        
        self.base_dir = Path(base_dir)
        self.image_dir = self.base_dir / 'image'
        self.audio_dir = self.base_dir / 'audio'
        self.text_dir = self.base_dir / 'text'
        self.processed_dir = self.base_dir / 'processed'
        
        # Create directories if they don't exist
        for directory in [self.base_dir, self.image_dir, self.audio_dir, 
                          self.text_dir, self.processed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataHandler initialized with base directory: {self.base_dir}")
    
    def validate_upload_path(self, upload_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate if the upload path exists.
        
        Args:
            upload_path: Path to the uploaded file or directory
            
        Returns:
            Tuple of (is_valid, message)
        """
        path = Path(upload_path)
        if not path.exists():
            return False, f"Path does not exist: {path}"
        return True, "Path is valid"
    
    def process_appearance_data(self, upload_path: Union[str, Path], 
                               user_id: str) -> Tuple[bool, str, Dict]:
        """
        Process appearance data (LoRA model or image dataset).
        
        Args:
            upload_path: Path to the uploaded file or directory
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (success, message, metadata)
        """
        path = Path(upload_path)
        user_image_dir = self.image_dir / user_id
        user_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if it's a LoRA model
        if path.is_file() and path.suffix.lower() in SUPPORTED_LORA_FORMATS:
            logger.info(f"Processing LoRA model: {path}")
            
            # Copy the LoRA model to the user's directory
            dest_path = user_image_dir / path.name
            shutil.copy2(path, dest_path)
            
            metadata = {
                "type": "lora_model",
                "filename": path.name,
                "path": str(dest_path),
                "size_bytes": dest_path.stat().st_size
            }
            
            return True, "LoRA model processed successfully", metadata
        
        # Check if it's an image dataset (directory or zip file)
        elif (path.is_dir() or 
              (path.is_file() and path.suffix.lower() == '.zip')):
            
            # If it's a zip file, extract it
            if path.is_file() and path.suffix.lower() == '.zip':
                import zipfile
                extract_dir = user_image_dir / "extracted"
                extract_dir.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                path = extract_dir
            
            # Process image files
            image_files = []
            for img_format in SUPPORTED_IMAGE_FORMATS:
                image_files.extend(list(path.glob(f"**/*{img_format}")))
            
            if len(image_files) < MIN_IMAGES_REQUIRED:
                return False, f"Insufficient images. Found {len(image_files)}, minimum required is {MIN_IMAGES_REQUIRED}", {}
            
            # Copy images to user directory
            processed_images = []
            for i, img_path in enumerate(image_files):
                dest_path = user_image_dir / f"image_{i:04d}{img_path.suffix}"
                shutil.copy2(img_path, dest_path)
                processed_images.append(str(dest_path))
            
            metadata = {
                "type": "image_dataset",
                "count": len(processed_images),
                "paths": processed_images,
                "formats": list(set(Path(p).suffix for p in processed_images))
            }
            
            return True, f"Image dataset processed successfully. {len(processed_images)} images found.", metadata
        
        else:
            return False, "Invalid appearance data. Must be a LoRA model file or image dataset.", {}
    
    def process_voice_data(self, upload_path: Union[str, Path], 
                          user_id: str) -> Tuple[bool, str, Dict]:
        """
        Process voice data (audio samples).
        
        Args:
            upload_path: Path to the uploaded file or directory
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (success, message, metadata)
        """
        path = Path(upload_path)
        user_audio_dir = self.audio_dir / user_id
        user_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if it's a directory or zip file
        if path.is_dir() or (path.is_file() and path.suffix.lower() == '.zip'):
            # If it's a zip file, extract it
            if path.is_file() and path.suffix.lower() == '.zip':
                import zipfile
                extract_dir = user_audio_dir / "extracted"
                extract_dir.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                path = extract_dir
            
            # Process audio files
            audio_files = []
            for audio_format in SUPPORTED_AUDIO_FORMATS:
                audio_files.extend(list(path.glob(f"**/*{audio_format}")))
            
            if len(audio_files) == 0:
                return False, "No audio files found in the provided data.", {}
            
            # Copy and analyze audio files
            processed_audio = []
            total_duration = 0
            
            for i, audio_path in enumerate(audio_files):
                dest_path = user_audio_dir / f"audio_{i:04d}{audio_path.suffix}"
                shutil.copy2(audio_path, dest_path)
                
                try:
                    # Get audio duration
                    y, sr = librosa.load(dest_path, sr=None)
                    duration = librosa.get_duration(y=y, sr=sr)
                    total_duration += duration
                    
                    processed_audio.append({
                        "path": str(dest_path),
                        "duration": duration,
                        "sample_rate": sr
                    })
                except Exception as e:
                    logger.error(f"Error processing audio file {dest_path}: {e}")
                    # Continue with other files even if one fails
            
            if total_duration < MIN_AUDIO_DURATION_SECONDS:
                return False, f"Insufficient audio duration. Found {total_duration:.2f} seconds, minimum required is {MIN_AUDIO_DURATION_SECONDS} seconds.", {}
            
            metadata = {
                "type": "audio_dataset",
                "count": len(processed_audio),
                "total_duration": total_duration,
                "files": processed_audio
            }
            
            return True, f"Voice data processed successfully. {len(processed_audio)} files, {total_duration:.2f} seconds total.", metadata
        
        # Check if it's a single audio file
        elif path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_FORMATS:
            dest_path = user_audio_dir / path.name
            shutil.copy2(path, dest_path)
            
            try:
                # Get audio duration
                y, sr = librosa.load(dest_path, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                
                if duration < MIN_AUDIO_DURATION_SECONDS:
                    return False, f"Insufficient audio duration. Found {duration:.2f} seconds, minimum required is {MIN_AUDIO_DURATION_SECONDS} seconds.", {}
                
                metadata = {
                    "type": "audio_file",
                    "filename": path.name,
                    "path": str(dest_path),
                    "duration": duration,
                    "sample_rate": sr
                }
                
                return True, f"Voice data processed successfully. Duration: {duration:.2f} seconds.", metadata
            
            except Exception as e:
                logger.error(f"Error processing audio file {dest_path}: {e}")
                return False, f"Error processing audio file: {e}", {}
        
        else:
            return False, "Invalid voice data. Must be audio files in supported formats.", {}
    
    def process_communication_data(self, upload_path: Union[str, Path], 
                                  user_id: str) -> Tuple[bool, str, Dict]:
        """
        Process communication style data (text dialog).
        
        Args:
            upload_path: Path to the uploaded file or directory
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (success, message, metadata)
        """
        path = Path(upload_path)
        user_text_dir = self.text_dir / user_id
        user_text_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if it's a directory or zip file
        if path.is_dir() or (path.is_file() and path.suffix.lower() == '.zip'):
            # If it's a zip file, extract it
            if path.is_file() and path.suffix.lower() == '.zip':
                import zipfile
                extract_dir = user_text_dir / "extracted"
                extract_dir.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                path = extract_dir
            
            # Process text files
            text_files = []
            for text_format in SUPPORTED_TEXT_FORMATS:
                text_files.extend(list(path.glob(f"**/*{text_format}")))
            
            if len(text_files) == 0:
                return False, "No text files found in the provided data.", {}
            
            # Copy and analyze text files
            processed_text = []
            total_samples = 0
            
            for i, text_path in enumerate(text_files):
                dest_path = user_text_dir / f"text_{i:04d}{text_path.suffix}"
                shutil.copy2(text_path, dest_path)
                
                try:
                    # Count samples based on file format
                    if text_path.suffix.lower() == '.json':
                        with open(dest_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Assuming JSON contains a list of dialog samples
                            if isinstance(data, list):
                                samples = len(data)
                            # Or a dict with a 'samples' or 'dialogs' key
                            elif isinstance(data, dict) and ('samples' in data or 'dialogs' in data):
                                samples = len(data.get('samples', data.get('dialogs', [])))
                            else:
                                # Count each key as a sample
                                samples = len(data)
                    
                    elif text_path.suffix.lower() == '.csv':
                        with open(dest_path, 'r', encoding='utf-8') as f:
                            # Count lines, subtract 1 for header
                            samples = sum(1 for _ in f) - 1
                    
                    else:  # .txt or other text formats
                        with open(dest_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Count sentences (roughly)
                            samples = len([s for s in content.split('.') if s.strip()])
                    
                    total_samples += samples
                    
                    processed_text.append({
                        "path": str(dest_path),
                        "samples": samples,
                        "format": text_path.suffix
                    })
                
                except Exception as e:
                    logger.error(f"Error processing text file {dest_path}: {e}")
                    # Continue with other files even if one fails
            
            if total_samples < MIN_TEXT_SAMPLES:
                return False, f"Insufficient text samples. Found {total_samples}, minimum required is {MIN_TEXT_SAMPLES}.", {}
            
            metadata = {
                "type": "text_dataset",
                "count": len(processed_text),
                "total_samples": total_samples,
                "files": processed_text
            }
            
            return True, f"Communication data processed successfully. {total_samples} samples found across {len(processed_text)} files.", metadata
        
        # Check if it's a single text file
        elif path.is_file() and path.suffix.lower() in SUPPORTED_TEXT_FORMATS:
            dest_path = user_text_dir / path.name
            shutil.copy2(path, dest_path)
            
            try:
                # Count samples based on file format
                if path.suffix.lower() == '.json':
                    with open(dest_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Assuming JSON contains a list of dialog samples
                        if isinstance(data, list):
                            samples = len(data)
                        # Or a dict with a 'samples' or 'dialogs' key
                        elif isinstance(data, dict) and ('samples' in data or 'dialogs' in data):
                            samples = len(data.get('samples', data.get('dialogs', [])))
                        else:
                            # Count each key as a sample
                            samples = len(data)
                
                elif path.suffix.lower() == '.csv':
                    with open(dest_path, 'r', encoding='utf-8') as f:
                        # Count lines, subtract 1 for header
                        samples = sum(1 for _ in f) - 1
                
                else:  # .txt or other text formats
                    with open(dest_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count sentences (roughly)
                        samples = len([s for s in content.split('.') if s.strip()])
                
                if samples < MIN_TEXT_SAMPLES:
                    return False, f"Insufficient text samples. Found {samples}, minimum required is {MIN_TEXT_SAMPLES}.", {}
                
                metadata = {
                    "type": "text_file",
                    "filename": path.name,
                    "path": str(dest_path),
                    "samples": samples,
                    "format": path.suffix
                }
                
                return True, f"Communication data processed successfully. {samples} samples found.", metadata
            
            except Exception as e:
                logger.error(f"Error processing text file {dest_path}: {e}")
                return False, f"Error processing text file: {e}", {}
        
        else:
            return False, "Invalid communication data. Must be text files in supported formats.", {}
    
    def preprocess_images(self, user_id: str, target_size: Tuple[int, int] = (512, 512)) -> Tuple[bool, str, Dict]:
        """
        Preprocess images for model training.
        
        Args:
            user_id: Unique identifier for the user
            target_size: Target size for resized images
            
        Returns:
            Tuple of (success, message, metadata)
        """
        user_image_dir = self.image_dir / user_id
        processed_dir = self.processed_dir / user_id / "images"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if user has image data
        if not user_image_dir.exists():
            return False, f"No image data found for user {user_id}", {}
        
        # Check if it's a LoRA model
        lora_files = []
        for lora_format in SUPPORTED_LORA_FORMATS:
            lora_files.extend(list(user_image_dir.glob(f"*{lora_format}")))
        
        if lora_files:
            # For LoRA models, just copy them to processed directory
            for lora_file in lora_files:
                dest_path = processed_dir / lora_file.name
                shutil.copy2(lora_file, dest_path)
            
            metadata = {
                "type": "lora_model",
                "files": [str(processed_dir / lora_file.name) for lora_file in lora_files]
            }
            
            return True, f"LoRA model(s) prepared for training.", metadata
        
        # Process image dataset
        image_files = []
        for img_format in SUPPORTED_IMAGE_FORMATS:
            image_files.extend(list(user_image_dir.glob(f"*{img_format}")))
        
        if not image_files:
            return False, f"No image files found for user {user_id}", {}
        
        processed_images = []
        
        for img_path in image_files:
            try:
                # Load and preprocess image
                img = Image.open(img_path)
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image
                img = img.resize(target_size, Image.LANCZOS)
                
                # Save processed image
                dest_path = processed_dir / f"processed_{img_path.stem}.jpg"
                img.save(dest_path, quality=95)
                
                processed_images.append(str(dest_path))
            
            except Exception as e:
                logger.error(f"Error preprocessing image {img_path}: {e}")
                # Continue with other images even if one fails
        
        if not processed_images:
            return False, "Failed to preprocess any images.", {}
        
        metadata = {
            "type": "image_dataset",
            "count": len(processed_images),
            "paths": processed_images,
            "target_size": target_size
        }
        
        return True, f"Image preprocessing completed. {len(processed_images)} images processed.", metadata
    
    def preprocess_audio(self, user_id: str, target_sr: int = 22050) -> Tuple[bool, str, Dict]:
        """
        Preprocess audio for model training.
        
        Args:
            user_id: Unique identifier for the user
            target_sr: Target sample rate
            
        Returns:
            Tuple of (success, message, metadata)
        """
        user_audio_dir = self.audio_dir / user_id
        processed_dir = self.processed_dir / user_id / "audio"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if user has audio data
        if not user_audio_dir.exists():
            return False, f"No audio data found for user {user_id}", {}
        
        # Process audio files
        audio_files = []
        for audio_format in SUPPORTED_AUDIO_FORMATS:
            audio_files.extend(list(user_audio_dir.glob(f"*{audio_format}")))
        
        if not audio_files:
            return False, f"No audio files found for user {user_id}", {}
        
        processed_audio = []
        total_duration = 0
        
        for audio_path in audio_files:
            try:
                # Load audio
                y, sr = librosa.load(audio_path, sr=None)
                
                # Resample if needed
                if sr != target_sr:
                    y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
                
                # Normalize audio
                y = librosa.util.normalize(y)
                
                # Save processed audio
                dest_path = processed_dir / f"processed_{audio_path.stem}.wav"
                librosa.output.write_wav(dest_path, y, target_sr)
                
                duration = librosa.get_duration(y=y, sr=target_sr)
                total_duration += duration
                
                processed_audio.append({
                    "path": str(dest_path),
                    "duration": duration,
                    "original_path": str(audio_path)
                })
            
            except Exception as e:
                logger.error(f"Error preprocessing audio {audio_path}: {e}")
                # Continue with other audio files even if one fails
        
        if not processed_audio:
            return False, "Failed to preprocess any audio files.", {}
        
        metadata = {
            "type": "audio_dataset",
            "count": len(processed_audio),
            "total_duration": total_duration,
            "sample_rate": target_sr,
            "files": processed_audio
        }
        
        return True, f"Audio preprocessing completed. {len(processed_audio)} files processed, {total_duration:.2f} seconds total.", metadata
    
    def preprocess_text(self, user_id: str) -> Tuple[bool, str, Dict]:
        """
        Preprocess text for model training.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (success, message, metadata)
        """
        user_text_dir = self.text_dir / user_id
        processed_dir = self.processed_dir / user_id / "text"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if user has text data
        if not user_text_dir.exists():
            return False, f"No text data found for user {user_id}", {}
        
        # Process text files
        text_files = []
        for text_format in SUPPORTED_TEXT_FORMATS:
            text_files.extend(list(user_text_dir.glob(f"*{text_format}")))
        
        if not text_files:
            return False, f"No text files found for user {user_id}", {}
        
        # Combine all text data into a standardized format
        all_samples = []
        
        for text_path in text_files:
            try:
                if text_path.suffix.lower() == '.json':
                    with open(text_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle different JSON structures
                        if isinstance(data, list):
                            # Assuming each item is a dialog sample
                            all_samples.extend(data)
                        elif isinstance(data, dict):
                            if 'samples' in data:
                                all_samples.extend(data['samples'])
                            elif 'dialogs' in data:
                                all_samples.extend(data['dialogs'])
                            else:
                                # Add each key-value pair as a sample
                                for key, value in data.items():
                                    all_samples.append({"prompt": key, "response": value})
                
                elif text_path.suffix.lower() == '.csv':
                    import csv
                    with open(text_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader)  # Skip header
                        
                        # Assuming CSV has at least 2 columns: prompt and response
                        for row in reader:
                            if len(row) >= 2:
                                all_samples.append({
                                    "prompt": row[0],
                                    "response": row[1]
                                })
                
                else:  # .txt or other text formats
                    with open(text_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Split by lines and try to identify dialog patterns
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        
                        i = 0
                        while i < len(lines) - 1:
                            # Try to identify prompt-response pairs
                            all_samples.append({
                                "prompt": lines[i],
                                "response": lines[i+1]
                            })
                            i += 2
            
            except Exception as e:
                logger.error(f"Error preprocessing text file {text_path}: {e}")
                # Continue with other text files even if one fails
        
        if not all_samples:
            return False, "Failed to extract any dialog samples from text files.", {}
        
        # Save processed samples to a standardized JSON file
        processed_path = processed_dir / "processed_dialog.json"
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(all_samples, f, ensure_ascii=False, indent=2)
        
        metadata = {
            "type": "text_dataset",
            "count": len(all_samples),
            "path": str(processed_path)
        }
        
        return True, f"Text preprocessing completed. {len(all_samples)} dialog samples extracted.", metadata
    
    def get_user_data_summary(self, user_id: str) -> Dict:
        """
        Get a summary of all data for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with data summary
        """
        summary = {
            "user_id": user_id,
            "appearance": {
                "has_data": False,
                "details": {}
            },
            "voice": {
                "has_data": False,
                "details": {}
            },
            "communication": {
                "has_data": False,
                "details": {}
            },
            "processed": {
                "appearance": False,
                "voice": False,
                "communication": False
            }
        }
        
        # Check appearance data
        user_image_dir = self.image_dir / user_id
        if user_image_dir.exists():
            lora_files = []
            for lora_format in SUPPORTED_LORA_FORMATS:
                lora_files.extend(list(user_image_dir.glob(f"*{lora_format}")))
            
            image_files = []
            for img_format in SUPPORTED_IMAGE_FORMATS:
                image_files.extend(list(user_image_dir.glob(f"*{img_format}")))
            
            if lora_files:
                summary["appearance"]["has_data"] = True
                summary["appearance"]["details"] = {
                    "type": "lora_model",
                    "count": len(lora_files),
                    "files": [str(f) for f in lora_files]
                }
            elif image_files:
                summary["appearance"]["has_data"] = True
                summary["appearance"]["details"] = {
                    "type": "image_dataset",
                    "count": len(image_files),
                    "files": [str(f) for f in image_files]
                }
        
        # Check voice data
        user_audio_dir = self.audio_dir / user_id
        if user_audio_dir.exists():
            audio_files = []
            for audio_format in SUPPORTED_AUDIO_FORMATS:
                audio_files.extend(list(user_audio_dir.glob(f"*{audio_format}")))
            
            if audio_files:
                summary["voice"]["has_data"] = True
                summary["voice"]["details"] = {
                    "count": len(audio_files),
                    "files": [str(f) for f in audio_files]
                }
        
        # Check communication data
        user_text_dir = self.text_dir / user_id
        if user_text_dir.exists():
            text_files = []
            for text_format in SUPPORTED_TEXT_FORMATS:
                text_files.extend(list(user_text_dir.glob(f"*{text_format}")))
            
            if text_files:
                summary["communication"]["has_data"] = True
                summary["communication"]["details"] = {
                    "count": len(text_files),
                    "files": [str(f) for f in text_files]
                }
        
        # Check processed data
        processed_dir = self.processed_dir / user_id
        if processed_dir.exists():
            if (processed_dir / "images").exists():
                summary["processed"]["appearance"] = True
            
            if (processed_dir / "audio").exists():
                summary["processed"]["voice"] = True
            
            if (processed_dir / "text").exists():
                summary["processed"]["communication"] = True
        
        return summary


# Example usage
if __name__ == "__main__":
    handler = DataHandler()
    print("Data Handler initialized and ready for use.")
