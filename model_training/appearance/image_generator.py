"""
Image generation module for the AI Avatar Platform.

This module handles image generation for avatars using LoRA models or image datasets.
"""

import os
import json
import logging
import requests
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('image_generator')

class ImageGenerator:
    """
    Generator for avatar images.
    
    This class handles image generation for avatars using LoRA models or image datasets,
    supporting both local generation and API-based generation.
    """
    
    def __init__(self, base_dir=None, api_key=None, api_url=None):
        """
        Initialize the ImageGenerator.
        
        Args:
            base_dir: Base directory for the platform
            api_key: API key for image generation service
            api_url: URL for image generation service
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / 'models'
        self.data_dir = self.base_dir / 'data'
        
        self.api_key = api_key
        self.api_url = api_url or "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        logger.info(f"ImageGenerator initialized with base directory: {self.base_dir}")
        if api_key:
            logger.info("Using external API for image generation")
        else:
            logger.info("Using local generation (simulated)")
    
    def generate_image(self, user_id, prompt, action=None, size=(512, 512)):
        """
        Generate an image for the avatar.
        
        Args:
            user_id: User ID
            prompt: Text prompt for image generation
            action: Action to generate (e.g., "waving", "dancing")
            size: Image size (width, height)
            
        Returns:
            Path to generated image or None if generation failed
        """
        logger.info(f"Generating image for user {user_id} with action: {action}")
        
        try:
            # Check if user has appearance data
            appearance_status = self._check_appearance_status(user_id)
            
            if not appearance_status["valid"]:
                logger.warning(f"No valid appearance data for user: {user_id}")
                return self._get_placeholder_image(size)
            
            # Determine generation method based on appearance type
            if appearance_status["type"] == "lora_model":
                # Generate using LoRA model
                return self._generate_with_lora(user_id, prompt, action, size)
            elif appearance_status["type"] == "image_dataset":
                # Generate using image dataset
                return self._generate_from_dataset(user_id, action, size)
            else:
                logger.warning(f"Unsupported appearance type: {appearance_status['type']}")
                return self._get_placeholder_image(size)
        
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._get_placeholder_image(size)
    
    def _check_appearance_status(self, user_id):
        """
        Check appearance status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with appearance status
        """
        # Initialize status
        status = {
            "uploaded": False,
            "valid": False,
            "type": None,
            "details": {}
        }
        
        try:
            # Check appearance
            appearance_model_dir = self.models_dir / 'appearance' / user_id
            if appearance_model_dir.exists():
                status["uploaded"] = True
                
                # Check for model file
                if (appearance_model_dir / 'model.safetensors').exists():
                    status["valid"] = True
                    status["type"] = "lora_model"
                    
                    # Get model info
                    if (appearance_model_dir / 'model_info.json').exists():
                        with open(str(appearance_model_dir / 'model_info.json'), 'r') as f:
                            status["details"] = json.load(f)
                
                # Check for dataset info
                elif (appearance_model_dir / 'dataset_info.json').exists():
                    with open(str(appearance_model_dir / 'dataset_info.json'), 'r') as f:
                        dataset_info = json.load(f)
                    
                    if dataset_info.get("image_count", 0) >= 10:
                        status["valid"] = True
                        status["type"] = "image_dataset"
                        status["details"] = dataset_info
        
        except Exception as e:
            logger.error(f"Error checking appearance status: {e}")
        
        return status
    
    def _generate_with_lora(self, user_id, prompt, action, size):
        """
        Generate image using LoRA model.
        
        Args:
            user_id: User ID
            prompt: Text prompt for image generation
            action: Action to generate
            size: Image size (width, height)
            
        Returns:
            Path to generated image
        """
        logger.info(f"Generating image with LoRA model for user {user_id}")
        
        # Check if API key is available
        if self.api_key:
            return self._generate_with_api(user_id, prompt, action, size)
        else:
            # Simulate LoRA generation
            return self._simulate_lora_generation(user_id, prompt, action, size)
    
    def _generate_with_api(self, user_id, prompt, action, size):
        """
        Generate image using external API.
        
        Args:
            user_id: User ID
            prompt: Text prompt for image generation
            action: Action to generate
            size: Image size (width, height)
            
        Returns:
            Path to generated image
        """
        logger.info(f"Generating image with API for user {user_id}")
        
        try:
            # Prepare prompt with action
            if action:
                full_prompt = f"A person {action}, {prompt}"
            else:
                full_prompt = prompt
            
            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "text_prompts": [
                    {
                        "text": full_prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "height": size[1],
                "width": size[0],
                "samples": 1,
                "steps": 30
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            # Check response status
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                
                # Extract image data
                if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                    image_data = base64.b64decode(response_data["artifacts"][0]["base64"])
                    
                    # Create output directory
                    output_dir = self.data_dir / 'appearance' / user_id / 'generated'
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save image
                    action_str = action.replace(" ", "_") if action else "default"
                    output_path = output_dir / f"{action_str}.png"
                    
                    with open(str(output_path), 'wb') as f:
                        f.write(image_data)
                    
                    logger.info(f"Generated image saved to: {output_path}")
                    return output_path
                else:
                    logger.error("No image data in API response")
                    return self._get_placeholder_image(size)
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return self._get_placeholder_image(size)
        
        except Exception as e:
            logger.error(f"Error generating image with API: {e}")
            return self._get_placeholder_image(size)
    
    def _simulate_lora_generation(self, user_id, prompt, action, size):
        """
        Simulate LoRA generation for testing purposes.
        
        Args:
            user_id: User ID
            prompt: Text prompt for image generation
            action: Action to generate
            size: Image size (width, height)
            
        Returns:
            Path to generated image
        """
        logger.info(f"Simulating LoRA generation for user {user_id}")
        
        try:
            # Create output directory
            output_dir = self.data_dir / 'appearance' / user_id / 'generated'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a colored image based on action
            action_str = action.replace(" ", "_") if action else "default"
            output_path = output_dir / f"{action_str}.png"
            
            # Generate a colored image
            color = self._get_color_for_action(action)
            img = Image.new('RGB', size, color=color)
            
            # Add text to image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Add text
            text = f"Avatar: {user_id}\nAction: {action or 'default'}"
            draw.text((10, 10), text, fill="white", font=font)
            
            # Save image
            img.save(str(output_path))
            
            logger.info(f"Simulated image saved to: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error simulating LoRA generation: {e}")
            return self._get_placeholder_image(size)
    
    def _generate_from_dataset(self, user_id, action, size):
        """
        Generate image from dataset.
        
        Args:
            user_id: User ID
            action: Action to generate
            size: Image size (width, height)
            
        Returns:
            Path to generated image
        """
        logger.info(f"Generating image from dataset for user {user_id}")
        
        try:
            # Get dataset path
            appearance_model_dir = self.models_dir / 'appearance' / user_id
            dataset_info_path = appearance_model_dir / 'dataset_info.json'
            
            if not dataset_info_path.exists():
                logger.warning(f"No dataset info found for user: {user_id}")
                return self._get_placeholder_image(size)
            
            # Load dataset info
            with open(str(dataset_info_path), 'r') as f:
                dataset_info = json.load(f)
            
            # Get dataset path
            dataset_path = Path(dataset_info.get("path", ""))
            if not dataset_path.exists():
                logger.warning(f"Dataset path not found: {dataset_path}")
                return self._get_placeholder_image(size)
            
            # Get all images in dataset
            image_files = [f for f in dataset_path.glob('*') if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')]
            if not image_files:
                logger.warning(f"No images found in dataset: {dataset_path}")
                return self._get_placeholder_image(size)
            
            # Create output directory
            output_dir = self.data_dir / 'appearance' / user_id / 'generated'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Select image based on action
            # In a production version, we would use more sophisticated selection
            # For the prototype, we'll use a simple hash-based selection
            import hashlib
            
            action_str = action or "default"
            hash_value = int(hashlib.md5(action_str.encode()).hexdigest(), 16)
            selected_image = image_files[hash_value % len(image_files)]
            
            # Create output path
            action_str = action.replace(" ", "_") if action else "default"
            output_path = output_dir / f"{action_str}.png"
            
            # Load and resize image
            img = Image.open(str(selected_image))
            img = img.resize(size)
            
            # Save image
            img.save(str(output_path))
            
            logger.info(f"Generated image from dataset saved to: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating image from dataset: {e}")
            return self._get_placeholder_image(size)
    
    def _get_placeholder_image(self, size):
        """
        Get a placeholder image.
        
        Args:
            size: Image size (width, height)
            
        Returns:
            Path to placeholder image
        """
        logger.info("Creating placeholder image")
        
        try:
            # Create output directory
            output_dir = self.data_dir / 'appearance' / 'placeholder'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output path
            output_path = output_dir / f"placeholder_{size[0]}x{size[1]}.png"
            
            # Check if placeholder already exists
            if output_path.exists():
                return output_path
            
            # Create a gray image
            img = Image.new('RGB', size, color=(100, 100, 100))
            
            # Add text to image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Add text
            text = "Placeholder Avatar"
            draw.text((10, 10), text, fill="white", font=font)
            
            # Save image
            img.save(str(output_path))
            
            logger.info(f"Placeholder image saved to: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
            
            # Return None as a last resort
            return None
    
    def _get_color_for_action(self, action):
        """
        Get color for action.
        
        Args:
            action: Action to get color for
            
        Returns:
            RGB color tuple
        """
        if not action:
            return (100, 100, 100)  # Gray for default
        
        action_lower = action.lower()
        
        if "jump" in action_lower:
            return (255, 165, 0)  # Orange
        elif "dance" in action_lower:
            return (138, 43, 226)  # Purple
        elif "wave" in action_lower:
            return (0, 128, 128)  # Teal
        elif "smile" in action_lower or "laugh" in action_lower:
            return (255, 215, 0)  # Gold
        elif "kiss" in action_lower:
            return (255, 105, 180)  # Hot Pink
        elif "wink" in action_lower:
            return (0, 191, 255)  # Deep Sky Blue
        elif "yoga" in action_lower:
            return (46, 139, 87)  # Sea Green
        elif "eat" in action_lower:
            return (210, 105, 30)  # Chocolate
        elif "business" in action_lower or "outfit" in action_lower:
            return (25, 25, 112)  # Midnight Blue
        elif "undress" in action_lower:
            return (220, 20, 60)  # Crimson
        elif "dress" in action_lower:
            return (0, 128, 0)  # Green
        else:
            # Generate a color based on action string
            import hashlib
            
            hash_value = int(hashlib.md5(action.encode()).hexdigest(), 16)
            r = (hash_value & 0xFF0000) >> 16
            g = (hash_value & 0x00FF00) >> 8
            b = hash_value & 0x0000FF
            
            return (r, g, b)
    
    def generate_action_images(self, user_id, actions, size=(512, 512)):
        """
        Generate images for multiple actions.
        
        Args:
            user_id: User ID
            actions: List of actions to generate
            size: Image size (width, height)
            
        Returns:
            Dictionary mapping actions to image paths
        """
        logger.info(f"Generating images for {len(actions)} actions for user {user_id}")
        
        results = {}
        
        for action in actions:
            try:
                # Generate image for action
                image_path = self.generate_image(user_id, f"A person {action}", action, size)
                
                if image_path:
                    results[action] = str(image_path)
                else:
                    logger.warning(f"Failed to generate image for action: {action}")
            except Exception as e:
                logger.error(f"Error generating image for action {action}: {e}")
        
        return results
    
    def get_available_actions(self):
        """
        Get available actions.
        
        Returns:
            Dictionary of action categories and actions
        """
        return {
            "expressions": [
                "smiling",
                "laughing",
                "winking",
                "thinking",
                "surprised"
            ],
            "movements": [
                "waving",
                "jumping",
                "dancing",
                "walking",
                "running"
            ],
            "interactions": [
                "blowing a kiss",
                "giving a high five",
                "thumbs up",
                "pointing",
                "nodding"
            ],
            "activities": [
                "yoga pose",
                "eating",
                "reading",
                "typing",
                "meditating"
            ],
            "outfits": [
                "business outfit",
                "casual outfit",
                "formal outfit",
                "sporty outfit",
                "pajamas"
            ]
        }
