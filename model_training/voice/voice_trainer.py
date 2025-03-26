"""
Voice Model Training Module for AI Avatar Platform

This module handles the training of voice synthesis models based on user-provided
audio samples.
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import librosa
import soundfile as sf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voice_trainer')

class VoiceModelTrainer:
    """Trains voice synthesis models from audio samples."""
    
    def __init__(self, base_dir: str = None, output_dir: str = None):
        """
        Initialize the VoiceModelTrainer.
        
        Args:
            base_dir: Base directory for input data
            output_dir: Directory for trained models and outputs
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'models')
        
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory for voice models
        self.voice_dir = self.output_dir / 'voice'
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VoiceModelTrainer initialized with base directory: {self.base_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def train_voice_model(self, user_id: str, audio_paths: List[Union[str, Path]]) -> Tuple[bool, str, Dict]:
        """
        Train a voice synthesis model from audio samples.
        
        Args:
            user_id: Unique identifier for the user
            audio_paths: List of paths to audio samples
            
        Returns:
            Tuple of (success, message, metadata)
        """
        logger.info(f"Training voice model for user {user_id} with {len(audio_paths)} audio samples")
        
        # Create user output directory
        user_output_dir = self.voice_dir / user_id
        user_output_dir.mkdir(parents=True, exist_ok=True)
        
        # In a real implementation, this would train a Tacotron 2 or similar TTS model
        # For this prototype, we'll simulate the process by analyzing the audio samples
        # and creating a simple voice profile
        
        try:
            # Process audio samples
            audio_features = []
            total_duration = 0
            
            for audio_path in audio_paths:
                # Load audio
                y, sr = librosa.load(audio_path, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                total_duration += duration
                
                # Extract basic features
                # In a real implementation, this would extract more sophisticated features
                pitch = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                pitch_mean = np.mean(pitch[~np.isnan(pitch)])
                
                # Extract spectral features
                spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
                
                # Extract energy
                energy = np.mean(np.abs(y))
                
                audio_features.append({
                    "path": str(audio_path),
                    "duration": duration,
                    "sample_rate": sr,
                    "pitch_mean": float(pitch_mean),
                    "spectral_centroid": float(spectral_centroid),
                    "spectral_bandwidth": float(spectral_bandwidth),
                    "energy": float(energy)
                })
            
            # Calculate average features
            avg_pitch = np.mean([f["pitch_mean"] for f in audio_features])
            avg_spectral_centroid = np.mean([f["spectral_centroid"] for f in audio_features])
            avg_spectral_bandwidth = np.mean([f["spectral_bandwidth"] for f in audio_features])
            avg_energy = np.mean([f["energy"] for f in audio_features])
            
            # Create a voice profile
            voice_profile = {
                "pitch": float(avg_pitch),
                "spectral_centroid": float(avg_spectral_centroid),
                "spectral_bandwidth": float(avg_spectral_bandwidth),
                "energy": float(avg_energy),
                "sample_rate": audio_features[0]["sample_rate"] if audio_features else 22050
            }
            
            # Save voice profile
            profile_path = user_output_dir / "voice_profile.json"
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(voice_profile, f, ensure_ascii=False, indent=2)
            
            # Create metadata
            metadata = {
                "samples_count": len(audio_features),
                "total_duration": total_duration,
                "voice_profile": voice_profile,
                "profile_path": str(profile_path)
            }
            
            # Save metadata
            metadata_path = user_output_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Generate example synthesized speech
            self._generate_example_speech(user_id, voice_profile)
            
            return True, f"Voice model trained successfully from {len(audio_features)} samples ({total_duration:.2f} seconds)", metadata
        
        except Exception as e:
            logger.error(f"Error training voice model: {e}")
            return False, f"Error training voice model: {str(e)}", {}
    
    def _generate_example_speech(self, user_id: str, voice_profile: Dict) -> str:
        """
        Generate example synthesized speech using the trained model.
        
        Args:
            user_id: Unique identifier for the user
            voice_profile: Voice profile parameters
            
        Returns:
            Path to the generated audio file
        """
        user_output_dir = self.voice_dir / user_id
        
        # In a real implementation, this would use the trained TTS model
        # For this prototype, we'll generate a simple sine wave with the voice profile parameters
        
        # Generate a 3-second audio sample
        duration = 3.0
        sr = voice_profile["sample_rate"]
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        # Use the pitch from the voice profile
        frequency = voice_profile["pitch"]
        
        # Generate a sine wave
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Apply an envelope
        envelope = np.ones_like(audio)
        attack = int(0.1 * sr)
        release = int(0.1 * sr)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        audio = audio * envelope
        
        # Scale by energy
        audio = audio * voice_profile["energy"] * 10
        
        # Add some noise based on spectral bandwidth
        noise_level = voice_profile["spectral_bandwidth"] / 5000
        noise = np.random.normal(0, noise_level, len(audio))
        audio = audio + noise
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        # Save the audio
        output_path = user_output_dir / "example_speech.wav"
        sf.write(output_path, audio, sr)
        
        return str(output_path)
    
    def synthesize_speech(self, user_id: str, text: str) -> Tuple[bool, str, Dict]:
        """
        Synthesize speech from text using the trained model.
        
        Args:
            user_id: Unique identifier for the user
            text: Text to synthesize
            
        Returns:
            Tuple of (success, message, metadata)
        """
        logger.info(f"Synthesizing speech for user {user_id}: '{text}'")
        
        user_output_dir = self.voice_dir / user_id
        if not user_output_dir.exists():
            return False, f"No voice model found for user {user_id}", {}
        
        # Check if we have a voice profile
        profile_path = user_output_dir / "voice_profile.json"
        if not profile_path.exists():
            return False, f"No voice profile found for user {user_id}", {}
        
        try:
            # Load voice profile
            with open(profile_path, 'r', encoding='utf-8') as f:
                voice_profile = json.load(f)
            
            # In a real implementation, this would use the trained TTS model
            # For this prototype, we'll generate a simple audio based on the text and voice profile
            
            # Calculate duration based on text length (rough estimate)
            words = text.split()
            duration = len(words) * 0.3  # Approx 0.3 seconds per word
            
            sr = voice_profile["sample_rate"]
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            
            # Use the pitch from the voice profile
            frequency = voice_profile["pitch"]
            
            # Generate a base audio
            audio = np.zeros_like(t)
            
            # Create a simple pattern based on words
            word_duration_samples = int(0.3 * sr)
            for i, word in enumerate(words):
                start_idx = i * word_duration_samples
                end_idx = min(start_idx + word_duration_samples, len(audio))
                
                # Different frequency for each word
                word_freq = frequency * (0.9 + 0.2 * (len(word) % 3) / 3)
                
                word_audio = np.sin(2 * np.pi * word_freq * t[start_idx:end_idx])
                
                # Apply an envelope
                envelope = np.ones_like(word_audio)
                attack = min(int(0.05 * sr), len(envelope) // 4)
                release = min(int(0.05 * sr), len(envelope) // 4)
                
                if attack > 0:
                    envelope[:attack] = np.linspace(0, 1, attack)
                if release > 0:
                    envelope[-release:] = np.linspace(1, 0, release)
                
                word_audio = word_audio * envelope
                
                audio[start_idx:end_idx] = word_audio
            
            # Scale by energy
            audio = audio * voice_profile["energy"] * 10
            
            # Add some noise based on spectral bandwidth
            noise_level = voice_profile["spectral_bandwidth"] / 5000
            noise = np.random.normal(0, noise_level, len(audio))
            audio = audio + noise
            
            # Normalize
            audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
            
            # Save the audio
            output_filename = f"speech_{text[:20].replace(' ', '_')}.wav"
            output_path = user_output_dir / output_filename
            sf.write(output_path, audio, sr)
            
            metadata = {
                "text": text,
                "duration": duration,
                "path": str(output_path)
            }
            
            return True, f"Speech synthesized successfully: '{text}'", metadata
        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return False, f"Error synthesizing speech: {str(e)}", {}
    
    def get_voice_summary(self, user_id: str) -> Dict:
        """
        Get a summary of voice model data for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with voice model data summary
        """
        user_output_dir = self.voice_dir / user_id
        if not user_output_dir.exists():
            return {
                "has_model": False,
                "message": f"No voice model found for user {user_id}"
            }
        
        # Check if we have metadata from previous processing
        metadata_path = user_output_dir / "metadata.json"
        if not metadata_path.exists():
            return {
                "has_model": False,
                "message": f"No voice model metadata found for user {user_id}"
            }
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check for example speech
            example_path = user_output_dir / "example_speech.wav"
            has_example = example_path.exists()
            
            return {
                "has_model": True,
                "samples_count": metadata.get("samples_count", 0),
                "total_duration": metadata.get("total_duration", 0),
                "has_example": has_example,
                "example_path": str(example_path) if has_example else None,
                "voice_profile": metadata.get("voice_profile", {})
            }
        
        except Exception as e:
            logger.error(f"Error getting voice model summary: {e}")
            return {
                "has_model": False,
                "message": f"Error getting voice model summary: {str(e)}"
            }


# Example usage
if __name__ == "__main__":
    trainer = VoiceModelTrainer()
    print("Voice Model Trainer initialized and ready for use.")
