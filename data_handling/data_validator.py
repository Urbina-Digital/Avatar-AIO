"""
Data Validation Module for AI Avatar Platform

This module provides validation functions for checking the quality and suitability
of user-provided datasets before processing.
"""

import os
import json
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
logger = logging.getLogger('data_validator')

# Import constants from data_handler
from data_handler import (
    MIN_IMAGES_REQUIRED,
    MIN_AUDIO_DURATION_SECONDS,
    MIN_TEXT_SAMPLES,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS,
    SUPPORTED_LORA_FORMATS,
    SUPPORTED_TEXT_FORMATS
)

class DataValidator:
    """Validates user-provided datasets for quality and suitability."""
    
    @staticmethod
    def validate_image_dataset(image_paths: List[Union[str, Path]]) -> Tuple[bool, str, Dict]:
        """
        Validate an image dataset.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Tuple of (is_valid, message, details)
        """
        if not image_paths:
            return False, "No image paths provided", {}
        
        # Check number of images
        if len(image_paths) < MIN_IMAGES_REQUIRED:
            return False, f"Insufficient images. Found {len(image_paths)}, minimum required is {MIN_IMAGES_REQUIRED}", {
                "count": len(image_paths),
                "min_required": MIN_IMAGES_REQUIRED
            }
        
        # Check file formats
        valid_images = []
        invalid_images = []
        
        for path in image_paths:
            path = Path(path)
            if path.suffix.lower() in SUPPORTED_IMAGE_FORMATS and path.exists():
                valid_images.append(str(path))
            else:
                invalid_images.append(str(path))
        
        if not valid_images:
            return False, "No valid images found. Supported formats: " + ", ".join(SUPPORTED_IMAGE_FORMATS), {
                "invalid_images": invalid_images
            }
        
        if len(valid_images) < MIN_IMAGES_REQUIRED:
            return False, f"Insufficient valid images. Found {len(valid_images)}, minimum required is {MIN_IMAGES_REQUIRED}", {
                "valid_count": len(valid_images),
                "invalid_count": len(invalid_images),
                "min_required": MIN_IMAGES_REQUIRED,
                "invalid_images": invalid_images
            }
        
        # Check image quality
        low_quality_images = []
        image_sizes = []
        
        for path in valid_images:
            try:
                img = Image.open(path)
                width, height = img.size
                image_sizes.append((width, height))
                
                # Check for very small images
                if width < 64 or height < 64:
                    low_quality_images.append({
                        "path": path,
                        "reason": f"Image too small: {width}x{height}"
                    })
                
                # Check for corrupted images
                img.verify()  # Verify that it's a valid image
                
            except Exception as e:
                low_quality_images.append({
                    "path": path,
                    "reason": f"Invalid image: {str(e)}"
                })
        
        # Calculate average image size
        avg_width = sum(w for w, h in image_sizes) / len(image_sizes) if image_sizes else 0
        avg_height = sum(h for w, h in image_sizes) / len(image_sizes) if image_sizes else 0
        
        details = {
            "valid_count": len(valid_images),
            "invalid_count": len(invalid_images),
            "low_quality_count": len(low_quality_images),
            "average_size": f"{int(avg_width)}x{int(avg_height)}",
            "low_quality_images": low_quality_images
        }
        
        # Final validation result
        valid_count = len(valid_images) - len(low_quality_images)
        if valid_count < MIN_IMAGES_REQUIRED:
            return False, f"Insufficient quality images. Found {valid_count} valid images, minimum required is {MIN_IMAGES_REQUIRED}", details
        
        return True, f"Image dataset validated successfully. {valid_count} valid images found.", details
    
    @staticmethod
    def validate_lora_model(model_path: Union[str, Path]) -> Tuple[bool, str, Dict]:
        """
        Validate a LoRA model file.
        
        Args:
            model_path: Path to the LoRA model file
            
        Returns:
            Tuple of (is_valid, message, details)
        """
        path = Path(model_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"Model file does not exist: {path}", {}
        
        # Check file format
        if path.suffix.lower() not in SUPPORTED_LORA_FORMATS:
            return False, f"Unsupported model format: {path.suffix}. Supported formats: " + ", ".join(SUPPORTED_LORA_FORMATS), {
                "format": path.suffix,
                "supported_formats": SUPPORTED_LORA_FORMATS
            }
        
        # Check file size (basic check)
        file_size = path.stat().st_size
        if file_size < 1024 * 1024:  # Less than 1MB is suspicious for a LoRA model
            return False, f"Model file is suspiciously small: {file_size / 1024:.2f} KB", {
                "file_size": file_size,
                "file_size_kb": file_size / 1024
            }
        
        # For a more thorough validation, we would need to load the model
        # and check its structure, but that requires specific libraries
        # and is beyond the scope of this basic validation
        
        details = {
            "file_size": file_size,
            "file_size_mb": file_size / (1024 * 1024)
        }
        
        return True, "LoRA model validated successfully", details
    
    @staticmethod
    def validate_audio_dataset(audio_paths: List[Union[str, Path]]) -> Tuple[bool, str, Dict]:
        """
        Validate an audio dataset.
        
        Args:
            audio_paths: List of paths to audio files
            
        Returns:
            Tuple of (is_valid, message, details)
        """
        if not audio_paths:
            return False, "No audio paths provided", {}
        
        # Check file formats
        valid_audio = []
        invalid_audio = []
        
        for path in audio_paths:
            path = Path(path)
            if path.suffix.lower() in SUPPORTED_AUDIO_FORMATS and path.exists():
                valid_audio.append(str(path))
            else:
                invalid_audio.append(str(path))
        
        if not valid_audio:
            return False, "No valid audio files found. Supported formats: " + ", ".join(SUPPORTED_AUDIO_FORMATS), {
                "invalid_audio": invalid_audio
            }
        
        # Check audio quality and duration
        low_quality_audio = []
        total_duration = 0
        sample_rates = []
        
        for path in valid_audio:
            try:
                # Load audio and get duration
                y, sr = librosa.load(path, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                total_duration += duration
                sample_rates.append(sr)
                
                # Check for very short clips
                if duration < 1.0:  # Less than 1 second
                    low_quality_audio.append({
                        "path": path,
                        "reason": f"Audio too short: {duration:.2f} seconds"
                    })
                
                # Check for silent audio
                if np.max(np.abs(y)) < 0.01:
                    low_quality_audio.append({
                        "path": path,
                        "reason": "Audio is nearly silent"
                    })
                
            except Exception as e:
                low_quality_audio.append({
                    "path": path,
                    "reason": f"Invalid audio: {str(e)}"
                })
        
        # Check total duration
        if total_duration < MIN_AUDIO_DURATION_SECONDS:
            return False, f"Insufficient audio duration. Found {total_duration:.2f} seconds, minimum required is {MIN_AUDIO_DURATION_SECONDS} seconds.", {
                "total_duration": total_duration,
                "min_required": MIN_AUDIO_DURATION_SECONDS,
                "valid_count": len(valid_audio),
                "low_quality_count": len(low_quality_audio)
            }
        
        # Calculate average sample rate
        avg_sample_rate = sum(sample_rates) / len(sample_rates) if sample_rates else 0
        
        details = {
            "valid_count": len(valid_audio),
            "invalid_count": len(invalid_audio),
            "low_quality_count": len(low_quality_audio),
            "total_duration": total_duration,
            "average_sample_rate": int(avg_sample_rate),
            "low_quality_audio": low_quality_audio
        }
        
        # Final validation result
        valid_count = len(valid_audio) - len(low_quality_audio)
        if valid_count == 0:
            return False, "No valid audio files found after quality checks", details
        
        return True, f"Audio dataset validated successfully. {valid_count} valid files, {total_duration:.2f} seconds total.", details
    
    @staticmethod
    def validate_text_dataset(text_paths: List[Union[str, Path]]) -> Tuple[bool, str, Dict]:
        """
        Validate a text dataset.
        
        Args:
            text_paths: List of paths to text files
            
        Returns:
            Tuple of (is_valid, message, details)
        """
        if not text_paths:
            return False, "No text paths provided", {}
        
        # Check file formats
        valid_text = []
        invalid_text = []
        
        for path in text_paths:
            path = Path(path)
            if path.suffix.lower() in SUPPORTED_TEXT_FORMATS and path.exists():
                valid_text.append(str(path))
            else:
                invalid_text.append(str(path))
        
        if not valid_text:
            return False, "No valid text files found. Supported formats: " + ", ".join(SUPPORTED_TEXT_FORMATS), {
                "invalid_text": invalid_text
            }
        
        # Check text content
        low_quality_text = []
        total_samples = 0
        
        for path in valid_text:
            try:
                # Count samples based on file format
                path_obj = Path(path)
                if path_obj.suffix.lower() == '.json':
                    with open(path, 'r', encoding='utf-8') as f:
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
                
                elif path_obj.suffix.lower() == '.csv':
                    with open(path, 'r', encoding='utf-8') as f:
                        # Count lines, subtract 1 for header
                        samples = sum(1 for _ in f) - 1
                
                else:  # .txt or other text formats
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count sentences (roughly)
                        samples = len([s for s in content.split('.') if s.strip()])
                
                total_samples += samples
                
                # Check for very small content
                if samples < 2:
                    low_quality_text.append({
                        "path": path,
                        "reason": f"Too few samples: {samples}"
                    })
                
            except Exception as e:
                low_quality_text.append({
                    "path": path,
                    "reason": f"Invalid text file: {str(e)}"
                })
        
        # Check total samples
        if total_samples < MIN_TEXT_SAMPLES:
            return False, f"Insufficient text samples. Found {total_samples}, minimum required is {MIN_TEXT_SAMPLES}.", {
                "total_samples": total_samples,
                "min_required": MIN_TEXT_SAMPLES,
                "valid_count": len(valid_text),
                "low_quality_count": len(low_quality_text)
            }
        
        details = {
            "valid_count": len(valid_text),
            "invalid_count": len(invalid_text),
            "low_quality_count": len(low_quality_text),
            "total_samples": total_samples,
            "low_quality_text": low_quality_text
        }
        
        # Final validation result
        valid_count = len(valid_text) - len(low_quality_text)
        if valid_count == 0:
            return False, "No valid text files found after quality checks", details
        
        return True, f"Text dataset validated successfully. {total_samples} samples found across {valid_count} files.", details


# Example usage
if __name__ == "__main__":
    print("Data Validator initialized and ready for use.")
