"""
Grok API Integration for the AI Avatar Platform.

This module provides integration with the Grok API for generating responses
based on user input and the avatar's communication style.
"""

import os
import json
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('grok_integration')

class GrokIntegration:
    """
    Integration with the Grok API for generating responses.
    
    This class provides methods for generating responses based on user input
    and the avatar's communication style using the Grok API.
    """
    
    def __init__(self, api_key=None, model="grok-2-latest"):
        """
        Initialize the GrokIntegration.
        
        Args:
            api_key: Grok API key
            model: Grok model to use
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.x.ai/v1/chat/completions"
        
        # Check if API key is provided
        if not self.api_key:
            logger.warning("No Grok API key provided. Using simulated responses.")
        else:
            logger.info(f"Grok integration initialized with model: {self.model}")
    
    def generate_response(self, user_input, communication_style=None, conversation_history=None):
        """
        Generate a response based on user input and communication style.
        
        Args:
            user_input: User input text
            communication_style: Communication style instructions
            conversation_history: Previous conversation history
            
        Returns:
            Generated response text
        """
        # If no API key, return simulated response
        if not self.api_key:
            logger.warning("No API key provided. Using simulated response.")
            return self._get_simulated_response(user_input)
        
        try:
            # Prepare conversation history
            messages = []
            
            # Add system message with communication style
            if communication_style:
                messages.append({
                    "role": "system",
                    "content": communication_style
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful AI avatar assistant. Keep your responses concise and friendly."
                })
            
            # Add conversation history
            if conversation_history:
                for message in conversation_history:
                    messages.append(message)
            
            # Add user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Prepare request payload
            payload = {
                "messages": messages,
                "model": self.model,
                "stream": False,
                "temperature": 0.7
            }
            
            # Set headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make API request
            logger.info("Sending request to Grok API")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Check response status
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                
                # Extract response text
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    response_text = response_data["choices"][0]["message"]["content"]
                    logger.info("Response generated successfully")
                    return response_text
                else:
                    logger.error("No response content in API response")
                    return "I'm sorry, I couldn't generate a response."
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return "I'm sorry, I couldn't generate a response due to an API error."
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I couldn't generate a response due to an error."
    
    def _get_simulated_response(self, user_input):
        """
        Get a simulated response for testing purposes.
        
        Args:
            user_input: User input text
            
        Returns:
            Simulated response text
        """
        # Simple keyword-based response system
        input_lower = user_input.lower()
        
        if "hello" in input_lower or "hi" in input_lower or "hey" in input_lower:
            return "Hello! How can I help you today?"
        
        if "how are you" in input_lower:
            return "I'm doing well, thank you for asking! How about you?"
        
        if "bye" in input_lower or "goodbye" in input_lower:
            return "Goodbye! It was nice chatting with you."
        
        if "thank" in input_lower:
            return "You're welcome! Is there anything else I can help you with?"
        
        if "help" in input_lower:
            return "I can assist you with various tasks. What would you like to know?"
        
        if "name" in input_lower:
            return "I'm your AI avatar assistant. You can customize me to your liking!"
        
        if "weather" in input_lower:
            return "I don't have real-time weather data, but I'd be happy to chat about other topics!"
        
        if "joke" in input_lower:
            return "Why don't scientists trust atoms? Because they make up everything!"
        
        if "music" in input_lower:
            return "I love music! What kind of music do you enjoy listening to?"
        
        if "movie" in input_lower or "film" in input_lower:
            return "Movies are great! Do you have a favorite genre or film you'd like to discuss?"
        
        # Default response
        return "That's interesting! Tell me more about that."
    
    def load_communication_style(self, user_id, models_dir=None):
        """
        Load communication style from user data.
        
        Args:
            user_id: User ID
            models_dir: Models directory
            
        Returns:
            Communication style instructions
        """
        if not models_dir:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")
        
        # Path to communication style file
        style_path = os.path.join(models_dir, "communication", user_id, "style.txt")
        
        # Check if file exists
        if os.path.exists(style_path):
            try:
                # Read communication style
                with open(style_path, "r", encoding="utf-8") as f:
                    communication_style = f.read().strip()
                
                logger.info(f"Communication style loaded for user: {user_id}")
                return communication_style
            except Exception as e:
                logger.error(f"Error loading communication style: {e}")
                return None
        else:
            logger.warning(f"No communication style found for user: {user_id}")
            return None
    
    def save_communication_style(self, user_id, communication_style, models_dir=None):
        """
        Save communication style to user data.
        
        Args:
            user_id: User ID
            communication_style: Communication style instructions
            models_dir: Models directory
            
        Returns:
            Success status
        """
        if not models_dir:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")
        
        # Path to communication style file
        style_dir = os.path.join(models_dir, "communication", user_id)
        style_path = os.path.join(style_dir, "style.txt")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(style_dir, exist_ok=True)
            
            # Write communication style
            with open(style_path, "w", encoding="utf-8") as f:
                f.write(communication_style)
            
            logger.info(f"Communication style saved for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving communication style: {e}")
            return False
    
    def analyze_dialog_samples(self, dialog_samples):
        """
        Analyze dialog samples to extract communication style.
        
        Args:
            dialog_samples: List of dialog samples
            
        Returns:
            Communication style instructions
        """
        if not self.api_key:
            logger.warning("No API key provided. Using simulated analysis.")
            return self._get_simulated_communication_style()
        
        try:
            # Prepare dialog samples text
            dialog_text = "\n\n".join(dialog_samples)
            
            # Prepare system message
            system_message = """
            You are an expert in analyzing communication styles. Your task is to analyze the provided dialog samples
            and extract a detailed communication style profile. Focus on aspects like:
            
            1. Tone (formal, casual, friendly, professional, etc.)
            2. Vocabulary level and complexity
            3. Sentence structure and length
            4. Use of humor, emojis, or slang
            5. Common phrases or expressions
            6. Response patterns and conversation flow
            
            Based on your analysis, create a detailed system prompt that could be used to instruct an AI to mimic
            this communication style. The prompt should be comprehensive but concise.
            """
            
            # Prepare user message
            user_message = f"""
            Please analyze the following dialog samples and create a system prompt that describes the communication style:
            
            {dialog_text}
            
            Create a system prompt that would instruct an AI to mimic this communication style.
            """
            
            # Prepare request payload
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "model": self.model,
                "stream": False,
                "temperature": 0.3
            }
            
            # Set headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make API request
            logger.info("Sending request to Grok API for dialog analysis")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Check response status
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                
                # Extract response text
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    communication_style = response_data["choices"][0]["message"]["content"]
                    logger.info("Dialog analysis completed successfully")
                    return communication_style
                else:
                    logger.error("No response content in API response")
                    return self._get_simulated_communication_style()
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return self._get_simulated_communication_style()
        
        except Exception as e:
            logger.error(f"Error analyzing dialog samples: {e}")
            return self._get_simulated_communication_style()
    
    def _get_simulated_communication_style(self):
        """
        Get a simulated communication style for testing purposes.
        
        Returns:
            Simulated communication style instructions
        """
        return """
        You are a friendly and helpful AI avatar assistant. Your communication style has the following characteristics:
        
        1. Tone: Warm, friendly, and conversational
        2. Vocabulary: Accessible but intelligent, avoiding overly technical terms unless necessary
        3. Sentence structure: Mix of short and medium-length sentences for natural flow
        4. Humor: Occasional light humor and playfulness
        5. Expressions: Use phrases like "I'd be happy to help", "That's interesting!", and "Let me know if you need anything else"
        6. Emojis: Occasional use of simple emojis like :) or :D for warmth
        7. Personality: Curious, empathetic, and eager to assist
        
        Keep your responses concise but informative, and always maintain a positive and supportive attitude.
        """
