"""
Voice synthesis module for the AI Avatar Platform.

This module handles voice synthesis for avatars using user-provided audio samples.
"""

import os
import json
import logging
import requests
import base64
from pathlib import Path
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voice_synthesizer')

class VoiceSynthesizer:
    """
    Synthesizer for avatar voices.
    
    This class handles voice synthesis for avatars using user-provided audio samples,
    supporting both local synthesis and API-based synthesis.
    """
    
    def __init__(self, base_dir=None, elevenlabs_api_key=None):
        """
        Initialize the VoiceSynthesizer.
        
        Args:
            base_dir: Base directory for the platform
            elevenlabs_api_key: API key for ElevenLabs voice synthesis service
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / 'models'
        self.data_dir = self.base_dir / 'data'
        
        self.elevenlabs_api_key = elevenlabs_api_key
        self.elevenlabs_api_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        logger.info(f"VoiceSynthesizer initialized with base directory: {self.base_dir}")
        if elevenlabs_api_key:
            logger.info("Using ElevenLabs API for voice synthesis")
        else:
            logger.info("Using local synthesis (simulated)")
    
    def synthesize_speech(self, user_id, text):
        """
        Synthesize speech for the avatar.
        
        Args:
            user_id: User ID
            text: Text to synthesize
            
        Returns:
            Path to synthesized audio file or None if synthesis failed
        """
        logger.info(f"Synthesizing speech for user {user_id}: '{text[:50]}...'")
        
        try:
            # Check if user has voice data
            voice_status = self._check_voice_status(user_id)
            
            if not voice_status["valid"]:
                logger.warning(f"No valid voice data for user: {user_id}")
                return self._get_placeholder_audio(text)
            
            # Determine synthesis method
            if self.elevenlabs_api_key:
                # Synthesize using ElevenLabs API
                return self._synthesize_with_elevenlabs(user_id, text)
            else:
                # Simulate voice synthesis
                return self._simulate_voice_synthesis(user_id, text)
        
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return self._get_placeholder_audio(text)
    
    def _check_voice_status(self, user_id):
        """
        Check voice status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with voice status
        """
        # Initialize status
        status = {
            "uploaded": False,
            "valid": False,
            "type": None,
            "details": {}
        }
        
        try:
            # Check voice
            voice_model_dir = self.models_dir / 'voice' / user_id
            if voice_model_dir.exists():
                status["uploaded"] = True
                
                # Check for model info
                if (voice_model_dir / 'model_info.json').exists() and (voice_model_dir / 'model.bin').exists():
                    with open(str(voice_model_dir / 'model_info.json'), 'r') as f:
                        model_info = json.load(f)
                    
                    if model_info.get("total_duration", 0) >= 60:
                        status["valid"] = True
                        status["type"] = "voice_model"
                        status["details"] = model_info
        
        except Exception as e:
            logger.error(f"Error checking voice status: {e}")
        
        return status
    
    def _synthesize_with_elevenlabs(self, user_id, text):
        """
        Synthesize speech using ElevenLabs API.
        
        Args:
            user_id: User ID
            text: Text to synthesize
            
        Returns:
            Path to synthesized audio file
        """
        logger.info(f"Synthesizing speech with ElevenLabs API for user {user_id}")
        
        try:
            # Create output directory
            output_dir = self.data_dir / 'voice' / user_id / 'generated'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output path
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            output_path = output_dir / f"speech_{text_hash}.mp3"
            
            # Check if already synthesized
            if output_path.exists():
                logger.info(f"Using cached synthesis: {output_path}")
                return output_path
            
            # Get voice ID
            # For a production version, we would create a custom voice using the user's audio samples
            # For the prototype, we'll use a default voice
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice
            
            # Prepare API request
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            # Make API request
            response = requests.post(
                f"{self.elevenlabs_api_url}/{voice_id}",
                headers=headers,
                json=payload
            )
            
            # Check response status
            if response.status_code == 200:
                # Save audio
                with open(str(output_path), 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Synthesized speech saved to: {output_path}")
                return output_path
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return self._get_placeholder_audio(text)
        
        except Exception as e:
            logger.error(f"Error synthesizing speech with ElevenLabs API: {e}")
            return self._get_placeholder_audio(text)
    
    def _simulate_voice_synthesis(self, user_id, text):
        """
        Simulate voice synthesis for testing purposes.
        
        Args:
            user_id: User ID
            text: Text to synthesize
            
        Returns:
            Path to synthesized audio file
        """
        logger.info(f"Simulating voice synthesis for user {user_id}")
        
        try:
            # Create output directory
            output_dir = self.data_dir / 'voice' / user_id / 'generated'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output path
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            output_path = output_dir / f"speech_{text_hash}.mp3"
            
            # Check if already synthesized
            if output_path.exists():
                logger.info(f"Using cached synthesis: {output_path}")
                return output_path
            
            # Generate a text file with the speech content
            # In a production version, this would be an actual audio file
            with open(str(output_path) + ".txt", 'w', encoding='utf-8') as f:
                f.write(f"Simulated speech: {text}")
            
            # Try to generate a simple audio file if possible
            try:
                # Try to use gTTS (Google Text-to-Speech) if available
                from gtts import gTTS
                tts = gTTS(text=text, lang='en')
                tts.save(str(output_path))
                logger.info(f"Generated audio with gTTS: {output_path}")
                return output_path
            except ImportError:
                logger.warning("gTTS not available, using text file as placeholder")
                return output_path.with_suffix(".txt")
            except Exception as e:
                logger.error(f"Error generating audio with gTTS: {e}")
                return output_path.with_suffix(".txt")
        
        except Exception as e:
            logger.error(f"Error simulating voice synthesis: {e}")
            return self._get_placeholder_audio(text)
    
    def _get_placeholder_audio(self, text):
        """
        Get a placeholder audio file.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Path to placeholder audio file
        """
        logger.info("Creating placeholder audio")
        
        try:
            # Create output directory
            output_dir = self.data_dir / 'voice' / 'placeholder'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output path
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            output_path = output_dir / f"placeholder_{text_hash}.txt"
            
            # Create a text file with the speech content
            with open(str(output_path), 'w', encoding='utf-8') as f:
                f.write(f"Placeholder speech: {text}")
            
            logger.info(f"Placeholder audio saved to: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating placeholder audio: {e}")
            
            # Return None as a last resort
            return None
    
    def create_voice_model(self, user_id, voice_name=None):
        """
        Create a voice model for the user.
        
        Args:
            user_id: User ID
            voice_name: Name for the voice model
            
        Returns:
            Success status and message
        """
        logger.info(f"Creating voice model for user {user_id}")
        
        try:
            # Check if user has voice data
            voice_status = self._check_voice_status(user_id)
            
            if not voice_status["valid"]:
                logger.warning(f"No valid voice data for user: {user_id}")
                return {
                    "success": False,
                    "message": "No valid voice data found. Please upload at least 60 seconds of audio."
                }
            
            # If using ElevenLabs API, create a custom voice
            if self.elevenlabs_api_key:
                return self._create_elevenlabs_voice(user_id, voice_name)
            else:
                # Simulate voice model creation
                return {
                    "success": True,
                    "message": "Voice model created successfully (simulated)",
                    "voice_id": f"simulated_{user_id}"
                }
        
        except Exception as e:
            logger.error(f"Error creating voice model: {e}")
            return {
                "success": False,
                "message": f"Error creating voice model: {str(e)}"
            }
    
    def _create_elevenlabs_voice(self, user_id, voice_name):
        """
        Create a custom voice using ElevenLabs API.
        
        Args:
            user_id: User ID
            voice_name: Name for the voice model
            
        Returns:
            Success status and message
        """
        logger.info(f"Creating ElevenLabs voice for user {user_id}")
        
        try:
            # Get user's voice data directory
            voice_data_dir = self.data_dir / 'voice' / user_id
            if not voice_data_dir.exists():
                logger.warning(f"Voice data directory not found: {voice_data_dir}")
                return {
                    "success": False,
                    "message": "Voice data directory not found"
                }
            
            # Get audio files
            audio_files = []
            for ext in ['.wav', '.mp3', '.ogg', '.flac']:
                audio_files.extend(list(voice_data_dir.glob(f"*{ext}")))
            
            # Check if we have audio files
            if not audio_files:
                logger.warning(f"No audio files found in: {voice_data_dir}")
                return {
                    "success": False,
                    "message": "No audio files found"
                }
            
            # Set voice name
            if not voice_name:
                voice_name = f"Avatar Voice {user_id}"
            
            # Prepare API request
            url = "https://api.elevenlabs.io/v1/voices/add"
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Prepare files
            files = []
            for audio_file in audio_files[:10]:  # Limit to 10 files
                files.append(
                    ('files', (audio_file.name, open(str(audio_file), 'rb'), 'audio/mpeg'))
                )
            
            # Add form data
            data = {
                'name': voice_name,
                'description': f'Custom voice for user {user_id}'
            }
            
            # Make API request
            response = requests.post(url, headers=headers, data=data, files=files)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            # Check response status
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                
                # Save voice ID
                voice_model_dir = self.models_dir / 'voice' / user_id
                voice_model_dir.mkdir(parents=True, exist_ok=True)
                
                with open(str(voice_model_dir / 'elevenlabs_voice_id.txt'), 'w') as f:
                    f.write(response_data.get('voice_id', ''))
                
                logger.info(f"ElevenLabs voice created with ID: {response_data.get('voice_id', '')}")
                
                return {
                    "success": True,
                    "message": "Voice model created successfully",
                    "voice_id": response_data.get('voice_id', '')
                }
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    "success": False,
                    "message": f"API request failed: {response.text}"
                }
        
        except Exception as e:
            logger.error(f"Error creating ElevenLabs voice: {e}")
            return {
                "success": False,
                "message": f"Error creating ElevenLabs voice: {str(e)}"
            }
    
    def get_voice_id(self, user_id):
        """
        Get voice ID for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Voice ID or None if not found
        """
        logger.info(f"Getting voice ID for user {user_id}")
        
        try:
            # Check if user has a custom ElevenLabs voice
            voice_model_dir = self.models_dir / 'voice' / user_id
            voice_id_path = voice_model_dir / 'elevenlabs_voice_id.txt'
            
            if voice_id_path.exists():
                with open(str(voice_id_path), 'r') as f:
                    voice_id = f.read().strip()
                
                if voice_id:
                    logger.info(f"Found ElevenLabs voice ID: {voice_id}")
                    return voice_id
            
            # If no custom voice, return a default voice ID
            if self.elevenlabs_api_key:
                default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice
                logger.info(f"Using default ElevenLabs voice ID: {default_voice_id}")
                return default_voice_id
            else:
                # For simulated synthesis
                simulated_voice_id = f"simulated_{user_id}"
                logger.info(f"Using simulated voice ID: {simulated_voice_id}")
                return simulated_voice_id
        
        except Exception as e:
            logger.error(f"Error getting voice ID: {e}")
            return None
