"""
Sample Data Generator for AI Avatar Platform

This module generates sample data for testing the platform without requiring actual user uploads.
"""

import os
import json
import random
import logging
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import librosa
import soundfile as sf
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sample_data_generator')

class SampleDataGenerator:
    """Generates sample data for testing the platform."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the SampleDataGenerator.
        
        Args:
            output_dir: Directory to store generated samples
        """
        if output_dir is None:
            output_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'sample_data'
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.image_dir = self.output_dir / 'appearance'
        self.audio_dir = self.output_dir / 'voice'
        self.text_dir = self.output_dir / 'communication'
        
        for directory in [self.image_dir, self.audio_dir, self.text_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SampleDataGenerator initialized with output directory: {self.output_dir}")
    
    def generate_sample_images(self, count: int = 10, size: Tuple[int, int] = (512, 512)) -> List[str]:
        """
        Generate sample images for appearance data.
        
        Args:
            count: Number of images to generate
            size: Size of each image (width, height)
            
        Returns:
            List of paths to generated images
        """
        logger.info(f"Generating {count} sample images of size {size}")
        
        image_paths = []
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (0, 128, 0),    # Dark Green
            (128, 128, 128) # Gray
        ]
        
        try:
            # Try to use a font if available
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = None
        
        for i in range(count):
            # Create a new image with a color
            color_idx = i % len(colors)
            img = Image.new('RGB', size, colors[color_idx])
            draw = ImageDraw.Draw(img)
            
            # Add some shapes for variety
            # Circle
            circle_x = random.randint(50, size[0] - 50)
            circle_y = random.randint(50, size[1] - 50)
            circle_radius = random.randint(20, 100)
            draw.ellipse(
                (circle_x - circle_radius, circle_y - circle_radius,
                 circle_x + circle_radius, circle_y + circle_radius),
                fill=(255, 255, 255, 128)
            )
            
            # Rectangle
            rect_x = random.randint(50, size[0] - 150)
            rect_y = random.randint(50, size[1] - 150)
            rect_width = random.randint(50, 150)
            rect_height = random.randint(50, 150)
            draw.rectangle(
                (rect_x, rect_y, rect_x + rect_width, rect_y + rect_height),
                fill=(0, 0, 0, 128)
            )
            
            # Add text
            if font:
                text = f"Sample Image {i+1}"
                text_width = draw.textlength(text, font=font)
                text_x = (size[0] - text_width) // 2
                text_y = size[1] - 50
                draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
            
            # Save the image
            image_path = self.image_dir / f"sample_image_{i+1:02d}.jpg"
            img.save(image_path)
            image_paths.append(str(image_path))
        
        logger.info(f"Generated {len(image_paths)} sample images")
        return image_paths
    
    def generate_sample_audio(self, count: int = 10, duration: float = 6.0, sr: int = 22050) -> List[str]:
        """
        Generate sample audio files for voice data.
        
        Args:
            count: Number of audio files to generate
            duration: Duration of each audio file in seconds
            sr: Sample rate
            
        Returns:
            List of paths to generated audio files
        """
        logger.info(f"Generating {count} sample audio files of {duration}s each")
        
        audio_paths = []
        
        for i in range(count):
            # Generate a simple sine wave with varying frequency
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            
            # Base frequency (different for each file)
            base_freq = 220 * (1 + i * 0.1)  # A3 and up
            
            # Generate a melody-like sequence
            audio = np.zeros_like(t)
            segment_duration = duration / 4
            samples_per_segment = int(sr * segment_duration)
            
            for j in range(4):
                segment_start = j * samples_per_segment
                segment_end = (j + 1) * samples_per_segment
                
                # Different frequency for each segment
                freq = base_freq * (1 + j * 0.2)
                
                # Generate sine wave for this segment
                segment = 0.5 * np.sin(2 * np.pi * freq * t[segment_start:segment_end])
                
                # Apply fade in/out
                fade_samples = int(0.1 * samples_per_segment)
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                
                segment[:fade_samples] *= fade_in
                segment[-fade_samples:] *= fade_out
                
                audio[segment_start:segment_end] = segment
            
            # Add some noise
            noise = np.random.normal(0, 0.01, len(audio))
            audio += noise
            
            # Normalize
            audio = audio / np.max(np.abs(audio))
            
            # Save the audio
            audio_path = self.audio_dir / f"sample_audio_{i+1:02d}.wav"
            sf.write(audio_path, audio, sr)
            audio_paths.append(str(audio_path))
        
        logger.info(f"Generated {len(audio_paths)} sample audio files")
        return audio_paths
    
    def generate_sample_text(self, num_dialogs: int = 15) -> str:
        """
        Generate sample text dialog for communication data.
        
        Args:
            num_dialogs: Number of dialog exchanges to generate
            
        Returns:
            Path to generated text file
        """
        logger.info(f"Generating sample text with {num_dialogs} dialog exchanges")
        
        # Sample prompts and responses
        prompts = [
            "Hello, how are you today?",
            "What's your favorite color?",
            "Tell me about yourself.",
            "What do you like to do for fun?",
            "What's the weather like?",
            "Do you have any hobbies?",
            "What's your favorite food?",
            "Tell me a joke.",
            "What's your favorite movie?",
            "What music do you like?",
            "Where would you like to travel?",
            "What's your favorite book?",
            "Do you have any pets?",
            "What's your favorite season?",
            "What do you think about AI?"
        ]
        
        responses = [
            "I'm doing great, thanks for asking! How about you?",
            "My favorite color is blue. It reminds me of the ocean and the sky.",
            "I'm a friendly AI avatar created to chat and interact with you. I enjoy learning new things and having interesting conversations.",
            "I enjoy reading, watching movies, and having thoughtful conversations. What about you?",
            "It's a beautiful sunny day with clear skies and a gentle breeze.",
            "I love photography, painting, and exploring new places. I find creative activities very fulfilling.",
            "I'm a fan of Italian cuisine, especially pasta dishes with rich tomato sauces and fresh herbs.",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I really enjoy 'The Matrix' for its philosophical themes and groundbreaking visual effects.",
            "I appreciate a wide range of music genres, from classical to jazz to contemporary pop. Music is a universal language.",
            "Japan is at the top of my list. I'm fascinated by the blend of ancient traditions and cutting-edge technology.",
            "'Dune' by Frank Herbert is a masterpiece of science fiction with its complex world-building and themes.",
            "I have an adorable tabby cat named Whiskers who loves to curl up on my lap while I'm reading.",
            "Autumn is my favorite season. I love the colorful foliage and the crisp, cool air.",
            "I think AI has tremendous potential to help humanity solve complex problems, but it's important to develop it responsibly and ethically."
        ]
        
        # Generate dialog samples
        dialogs = []
        
        for i in range(min(num_dialogs, len(prompts))):
            dialogs.append({
                "prompt": prompts[i],
                "response": responses[i]
            })
        
        # If we need more dialogs than our predefined list
        for i in range(len(prompts), num_dialogs):
            # Create variations of existing prompts/responses
            prompt_idx = random.randint(0, len(prompts) - 1)
            response_idx = random.randint(0, len(responses) - 1)
            
            dialogs.append({
                "prompt": prompts[prompt_idx],
                "response": responses[response_idx]
            })
        
        # Save as JSON
        json_path = self.text_dir / "sample_dialog.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dialogs, f, ensure_ascii=False, indent=2)
        
        # Also save as TXT for alternative format
        txt_path = self.text_dir / "sample_dialog.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            for dialog in dialogs:
                f.write(f"User: {dialog['prompt']}\n")
                f.write(f"Avatar: {dialog['response']}\n\n")
        
        logger.info(f"Generated sample dialog with {len(dialogs)} exchanges")
        return str(json_path)
    
    def generate_all_samples(self) -> Dict[str, List[str]]:
        """
        Generate all types of sample data.
        
        Returns:
            Dictionary with paths to all generated samples
        """
        logger.info("Generating all sample data types")
        
        samples = {
            "appearance": self.generate_sample_images(),
            "voice": self.generate_sample_audio(),
            "communication": [self.generate_sample_text()]
        }
        
        logger.info("All sample data generated successfully")
        return samples


# Example usage
if __name__ == "__main__":
    generator = SampleDataGenerator()
    samples = generator.generate_all_samples()
    print("Sample data generated successfully:")
    for data_type, paths in samples.items():
        print(f"- {data_type}: {len(paths)} files")
