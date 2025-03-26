"""
Communication Model Training Module for AI Avatar Platform

This module handles the training of language models based on user-provided
text dialog samples.
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('communication_trainer')

class CommunicationModelTrainer:
    """Trains language models from text dialog samples."""
    
    def __init__(self, base_dir: str = None, output_dir: str = None):
        """
        Initialize the CommunicationModelTrainer.
        
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
        
        # Create subdirectory for communication models
        self.communication_dir = self.output_dir / 'communication'
        self.communication_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CommunicationModelTrainer initialized with base directory: {self.base_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def train_language_model(self, user_id: str, dialog_path: Union[str, Path]) -> Tuple[bool, str, Dict]:
        """
        Train a language model from text dialog samples.
        
        Args:
            user_id: Unique identifier for the user
            dialog_path: Path to the dialog samples file
            
        Returns:
            Tuple of (success, message, metadata)
        """
        logger.info(f"Training language model for user {user_id} from {dialog_path}")
        
        # Create user output directory
        user_output_dir = self.communication_dir / user_id
        user_output_dir.mkdir(parents=True, exist_ok=True)
        
        # In a real implementation, this would fine-tune a language model like Llama or GPT
        # For this prototype, we'll simulate the process by analyzing the dialog samples
        # and creating a simple language profile
        
        try:
            # Load dialog samples
            dialog_path = Path(dialog_path)
            
            if dialog_path.suffix.lower() == '.json':
                with open(dialog_path, 'r', encoding='utf-8') as f:
                    dialogs = json.load(f)
            elif dialog_path.suffix.lower() == '.txt':
                # Parse text file
                dialogs = []
                with open(dialog_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                i = 0
                while i < len(lines) - 1:
                    line = lines[i].strip()
                    next_line = lines[i+1].strip()
                    
                    if line.startswith("User:"):
                        prompt = line[5:].strip()
                        if next_line.startswith("Avatar:"):
                            response = next_line[7:].strip()
                            dialogs.append({
                                "prompt": prompt,
                                "response": response
                            })
                    
                    i += 1
            else:
                return False, f"Unsupported dialog file format: {dialog_path.suffix}", {}
            
            # Ensure dialogs is a list of dictionaries with 'prompt' and 'response' keys
            if not isinstance(dialogs, list):
                return False, "Dialog data is not in the expected format (list)", {}
            
            # Filter out any dialogs without both prompt and response
            valid_dialogs = []
            for dialog in dialogs:
                if isinstance(dialog, dict) and 'prompt' in dialog and 'response' in dialog:
                    valid_dialogs.append(dialog)
            
            if not valid_dialogs:
                return False, "No valid dialog samples found", {}
            
            # Analyze dialog style
            word_counts = []
            sentence_counts = []
            avg_word_lengths = []
            question_counts = 0
            exclamation_counts = 0
            emoji_counts = 0
            
            # Common emojis for detection
            emojis = ['😊', '😂', '🙂', '😍', '😁', '😉', '🙄', '😎', '😢', '😭', '😡', '🤔', '👍', '❤️']
            
            for dialog in valid_dialogs:
                response = dialog['response']
                
                # Count words
                words = response.split()
                word_counts.append(len(words))
                
                # Count sentences
                sentences = [s for s in response.split('.') if s.strip()]
                sentence_counts.append(len(sentences))
                
                # Calculate average word length
                if words:
                    avg_word_length = sum(len(word) for word in words) / len(words)
                    avg_word_lengths.append(avg_word_length)
                
                # Count questions
                question_counts += response.count('?')
                
                # Count exclamations
                exclamation_counts += response.count('!')
                
                # Count emojis
                for emoji in emojis:
                    emoji_counts += response.count(emoji)
            
            # Calculate averages
            avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
            avg_sentence_count = sum(sentence_counts) / len(sentence_counts) if sentence_counts else 0
            avg_word_length = sum(avg_word_lengths) / len(avg_word_lengths) if avg_word_lengths else 0
            
            # Create language profile
            language_profile = {
                "avg_word_count": float(avg_word_count),
                "avg_sentence_count": float(avg_sentence_count),
                "avg_word_length": float(avg_word_length),
                "question_frequency": float(question_counts / len(valid_dialogs)) if valid_dialogs else 0,
                "exclamation_frequency": float(exclamation_counts / len(valid_dialogs)) if valid_dialogs else 0,
                "emoji_frequency": float(emoji_counts / len(valid_dialogs)) if valid_dialogs else 0,
                "sample_responses": [dialog["response"] for dialog in valid_dialogs[:5]]
            }
            
            # Save language profile
            profile_path = user_output_dir / "language_profile.json"
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(language_profile, f, ensure_ascii=False, indent=2)
            
            # Save processed dialogs
            processed_path = user_output_dir / "processed_dialogs.json"
            with open(processed_path, 'w', encoding='utf-8') as f:
                json.dump(valid_dialogs, f, ensure_ascii=False, indent=2)
            
            # Create metadata
            metadata = {
                "dialog_count": len(valid_dialogs),
                "language_profile": language_profile,
                "profile_path": str(profile_path),
                "processed_path": str(processed_path)
            }
            
            # Save metadata
            metadata_path = user_output_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True, f"Language model trained successfully from {len(valid_dialogs)} dialog samples", metadata
        
        except Exception as e:
            logger.error(f"Error training language model: {e}")
            return False, f"Error training language model: {str(e)}", {}
    
    def generate_response(self, user_id: str, prompt: str) -> Tuple[bool, str, Dict]:
        """
        Generate a response to a prompt using the trained model.
        
        Args:
            user_id: Unique identifier for the user
            prompt: Input prompt
            
        Returns:
            Tuple of (success, message, metadata)
        """
        logger.info(f"Generating response for user {user_id}: '{prompt}'")
        
        user_output_dir = self.communication_dir / user_id
        if not user_output_dir.exists():
            return False, f"No language model found for user {user_id}", {}
        
        # Check if we have processed dialogs
        processed_path = user_output_dir / "processed_dialogs.json"
        if not processed_path.exists():
            return False, f"No processed dialogs found for user {user_id}", {}
        
        try:
            # Load processed dialogs
            with open(processed_path, 'r', encoding='utf-8') as f:
                dialogs = json.load(f)
            
            # Load language profile
            profile_path = user_output_dir / "language_profile.json"
            with open(profile_path, 'r', encoding='utf-8') as f:
                language_profile = json.load(f)
            
            # In a real implementation, this would use the fine-tuned language model
            # For this prototype, we'll use a simple approach:
            # 1. Look for similar prompts in the training data
            # 2. If found, return the corresponding response
            # 3. If not found, generate a response based on the language profile
            
            # Look for similar prompts
            best_match = None
            best_match_score = 0
            
            for dialog in dialogs:
                dialog_prompt = dialog["prompt"].lower()
                input_prompt = prompt.lower()
                
                # Calculate a simple similarity score
                words1 = set(dialog_prompt.split())
                words2 = set(input_prompt.split())
                
                common_words = words1.intersection(words2)
                
                if not common_words:
                    continue
                
                # Score based on common words relative to total unique words
                score = len(common_words) / len(words1.union(words2))
                
                if score > best_match_score:
                    best_match_score = score
                    best_match = dialog
            
            # If we found a good match (threshold of 0.3)
            if best_match and best_match_score > 0.3:
                response = best_match["response"]
                source = "training_data"
            else:
                # Generate a response based on the language profile
                response = self._generate_synthetic_response(prompt, language_profile)
                source = "synthetic"
            
            metadata = {
                "prompt": prompt,
                "response": response,
                "source": source,
                "match_score": best_match_score if best_match else 0
            }
            
            return True, response, metadata
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return False, f"Error generating response: {str(e)}", {}
    
    def _generate_synthetic_response(self, prompt: str, language_profile: Dict) -> str:
        """
        Generate a synthetic response based on the language profile.
        
        Args:
            prompt: Input prompt
            language_profile: Language profile parameters
            
        Returns:
            Generated response
        """
        # In a real implementation, this would use a more sophisticated approach
        # For this prototype, we'll use a template-based approach with the language profile
        
        # Extract parameters from language profile
        avg_word_count = int(language_profile["avg_word_count"])
        avg_sentence_count = max(1, int(language_profile["avg_sentence_count"]))
        question_freq = language_profile["question_frequency"]
        exclamation_freq = language_profile["exclamation_frequency"]
        emoji_freq = language_profile["emoji_frequency"]
        sample_responses = language_profile.get("sample_responses", [])
        
        # Common templates
        templates = [
            "I understand what you're saying about {topic}.",
            "That's an interesting point about {topic}.",
            "I've been thinking about {topic} too.",
            "When it comes to {topic}, I have some thoughts.",
            "I appreciate you bringing up {topic}."
        ]
        
        # Extract a topic from the prompt
        words = prompt.split()
        if len(words) > 3:
            # Try to extract a noun phrase
            if len(words) > 5:
                topic_start = random.randint(0, len(words) - 3)
                topic_length = random.randint(1, 3)
                topic = " ".join(words[topic_start:topic_start + topic_length])
            else:
                topic = " ".join(words[1:3])
        else:
            topic = prompt
        
        # Generate sentences
        sentences = []
        
        # Start with a template
        template = random.choice(templates)
        first_sentence = template.format(topic=topic)
        sentences.append(first_sentence)
        
        # Add more sentences if needed
        for i in range(avg_sentence_count - 1):
            # If we have sample responses, use parts of them
            if sample_responses and random.random() < 0.7:
                sample = random.choice(sample_responses)
                sample_sentences = [s.strip() for s in sample.split('.') if s.strip()]
                
                if sample_sentences:
                    sentences.append(random.choice(sample_sentences))
                    continue
            
            # Otherwise, use generic sentences
            generic_sentences = [
                f"I think {topic} is really important.",
                f"There's a lot to consider about {topic}.",
                f"I've had some experience with {topic} before.",
                f"It's always good to discuss {topic}.",
                f"Let me know if you want to talk more about {topic}."
            ]
            
            sentences.append(random.choice(generic_sentences))
        
        # Add questions based on question frequency
        if random.random() < question_freq:
            questions = [
                f"What do you think about {topic}?",
                f"Have you considered other aspects of {topic}?",
                f"Would you like to know more about {topic}?",
                f"Isn't {topic} fascinating?",
                f"What else would you like to discuss about {topic}?"
            ]
            
            sentences.append(random.choice(questions))
        
        # Add exclamations based on exclamation frequency
        if random.random() < exclamation_freq:
            exclamations = [
                f"I love discussing {topic}!",
                f"This is so interesting!",
                f"{topic} is amazing!",
                f"I'm excited about this conversation!",
                f"I can't wait to talk more about {topic}!"
            ]
            
            # Replace a random sentence with an exclamation
            if sentences:
                idx = random.randint(0, len(sentences) - 1)
                sentences[idx] = random.choice(exclamations)
        
        # Combine sentences
        response = ". ".join(sentences)
        if not response.endswith('.') and not response.endswith('!') and not response.endswith('?'):
            response += '.'
        
        # Add emojis based on emoji frequency
        if random.random() < emoji_freq:
            emojis = ['😊', '😂', '🙂', '😍', '😁', '😉', '🙄', '😎']
            response += f" {random.choice(emojis)}"
        
        return response
    
    def get_communication_summary(self, user_id: str) -> Dict:
        """
        Get a summary of communication model data for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with communication model data summary
        """
        user_output_dir = self.communication_dir / user_id
        if not user_output_dir.exists():
            return {
                "has_model": False,
                "message": f"No communication model found for user {user_id}"
            }
        
        # Check if we have metadata from previous processing
        metadata_path = user_output_dir / "metadata.json"
        if not metadata_path.exists():
            return {
                "has_model": False,
                "message": f"No communication model metadata found for user {user_id}"
            }
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {
                "has_model": True,
                "dialog_count": metadata.get("dialog_count", 0),
                "language_profile": metadata.get("language_profile", {})
            }
        
        except Exception as e:
            logger.error(f"Error getting communication model summary: {e}")
            return {
                "has_model": False,
                "message": f"Error getting communication model summary: {str(e)}"
            }


# Example usage
if __name__ == "__main__":
    trainer = CommunicationModelTrainer()
    print("Communication Model Trainer initialized and ready for use.")
