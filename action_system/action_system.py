"""
Action System Module for AI Avatar Platform

This module handles the definition, triggering, and management of avatar actions
based on user interactions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import random
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('action_system')

class ActionSystem:
    """Manages avatar actions and animations."""
    
    def __init__(self, models_dir: str = None):
        """
        Initialize the ActionSystem.
        
        Args:
            models_dir: Directory containing trained models
        """
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
        
        self.models_dir = Path(models_dir)
        
        # Define standard actions
        self.standard_actions = {
            # Expressions
            "smile": {"type": "expression", "duration": 2.0, "category": "positive"},
            "laugh": {"type": "expression", "duration": 3.0, "category": "positive"},
            "think": {"type": "expression", "duration": 2.5, "category": "neutral"},
            "sad": {"type": "expression", "duration": 2.0, "category": "negative"},
            "angry": {"type": "expression", "duration": 2.0, "category": "negative"},
            "surprised": {"type": "expression", "duration": 1.5, "category": "neutral"},
            
            # Movements
            "wave": {"type": "movement", "duration": 2.0, "category": "greeting"},
            "nod": {"type": "movement", "duration": 1.5, "category": "agreement"},
            "shake_head": {"type": "movement", "duration": 1.5, "category": "disagreement"},
            "jump": {"type": "movement", "duration": 2.0, "category": "energetic"},
            "bow": {"type": "movement", "duration": 2.0, "category": "respectful"},
            "shrug": {"type": "movement", "duration": 1.5, "category": "neutral"},
            
            # Interactions
            "high_five": {"type": "interaction", "duration": 1.0, "category": "friendly"},
            "hug": {"type": "interaction", "duration": 2.0, "category": "friendly"},
            "handshake": {"type": "interaction", "duration": 1.5, "category": "formal"},
            "fist_bump": {"type": "interaction", "duration": 1.0, "category": "friendly"},
            "point": {"type": "interaction", "duration": 1.0, "category": "neutral"},
            
            # Idle actions
            "idle_breathe": {"type": "idle", "duration": 3.0, "category": "idle"},
            "idle_look_around": {"type": "idle", "duration": 4.0, "category": "idle"},
            "idle_shift_weight": {"type": "idle", "duration": 2.5, "category": "idle"},
            "idle_check_phone": {"type": "idle", "duration": 3.0, "category": "idle"},
            "idle_stretch": {"type": "idle", "duration": 3.5, "category": "idle"},
            
            # Outfit changes
            "change_casual": {"type": "outfit", "duration": 3.0, "category": "outfit"},
            "change_formal": {"type": "outfit", "duration": 3.0, "category": "outfit"},
            "change_sporty": {"type": "outfit", "duration": 3.0, "category": "outfit"},
            
            # Activities
            "eat": {"type": "activity", "duration": 3.0, "category": "daily"},
            "drink": {"type": "activity", "duration": 2.0, "category": "daily"},
            "read": {"type": "activity", "duration": 4.0, "category": "leisure"},
            "write": {"type": "activity", "duration": 3.0, "category": "work"},
            "yoga": {"type": "activity", "duration": 5.0, "category": "fitness"},
            "meditate": {"type": "activity", "duration": 4.0, "category": "wellness"}
        }
        
        # Define action triggers based on keywords in user input
        self.action_triggers = {
            "hello": ["wave", "smile"],
            "hi": ["wave", "smile"],
            "hey": ["wave", "smile"],
            "bye": ["wave"],
            "goodbye": ["wave"],
            "yes": ["nod"],
            "no": ["shake_head"],
            "agree": ["nod"],
            "disagree": ["shake_head"],
            "happy": ["smile", "laugh"],
            "sad": ["sad"],
            "angry": ["angry"],
            "surprised": ["surprised"],
            "think": ["think"],
            "jump": ["jump"],
            "hug": ["hug"],
            "high five": ["high_five"],
            "handshake": ["handshake"],
            "fist bump": ["fist_bump"],
            "point": ["point"],
            "casual": ["change_casual"],
            "formal": ["change_formal"],
            "sporty": ["change_sporty"],
            "eat": ["eat"],
            "drink": ["drink"],
            "read": ["read"],
            "write": ["write"],
            "yoga": ["yoga"],
            "meditate": ["meditate"],
        }
        
        # Define response categories for different emotions
        self.response_categories = {
            "greeting": ["wave", "smile", "nod"],
            "agreement": ["nod", "smile"],
            "disagreement": ["shake_head", "think"],
            "happy": ["smile", "laugh", "jump"],
            "sad": ["sad"],
            "thoughtful": ["think"],
            "friendly": ["wave", "high_five", "hug", "fist_bump"],
            "formal": ["handshake", "bow"],
            "surprised": ["surprised"],
            "confused": ["think", "shrug"]
        }
        
        logger.info(f"ActionSystem initialized with models directory: {self.models_dir}")
    
    def get_action_details(self, action_name: str) -> Dict:
        """
        Get details for a specific action.
        
        Args:
            action_name: Name of the action
            
        Returns:
            Dictionary with action details
        """
        if action_name in self.standard_actions:
            return {
                "name": action_name,
                **self.standard_actions[action_name]
            }
        else:
            return {
                "name": action_name,
                "type": "unknown",
                "duration": 2.0,
                "category": "custom"
            }
    
    def get_all_actions(self) -> Dict[str, List[Dict]]:
        """
        Get all available actions grouped by type.
        
        Returns:
            Dictionary with actions grouped by type
        """
        actions_by_type = {}
        
        for action_name, details in self.standard_actions.items():
            action_type = details["type"]
            
            if action_type not in actions_by_type:
                actions_by_type[action_type] = []
            
            actions_by_type[action_type].append({
                "name": action_name,
                **details
            })
        
        return actions_by_type
    
    def trigger_action(self, user_id: str, action_name: str) -> Tuple[bool, str, Dict]:
        """
        Trigger a specific action for the avatar.
        
        Args:
            user_id: Unique identifier for the user
            action_name: Name of the action to trigger
            
        Returns:
            Tuple of (success, message, metadata)
        """
        logger.info(f"Triggering action '{action_name}' for user {user_id}")
        
        # Check if the action exists
        if action_name not in self.standard_actions:
            return False, f"Unknown action: {action_name}", {}
        
        # Get action details
        action_details = self.get_action_details(action_name)
        
        # In a real implementation, this would trigger the actual animation
        # For this prototype, we'll simulate the process
        
        # Check if we have appearance data for this user
        appearance_dir = self.models_dir / 'appearance' / user_id
        if not appearance_dir.exists():
            return False, f"No appearance data found for user {user_id}", {}
        
        # Check if we have an action-specific animation
        action_dir = appearance_dir / "actions" / action_name
        if action_dir.exists():
            # Use existing animation
            gif_path = action_dir / f"{action_name}.gif"
            if gif_path.exists():
                metadata = {
                    "action": action_name,
                    "type": action_details["type"],
                    "duration": action_details["duration"],
                    "gif_path": str(gif_path),
                    "source": "custom"
                }
                
                return True, f"Action '{action_name}' triggered successfully", metadata
        
        # If we don't have a specific animation, use a generic one based on the action type
        # In a real implementation, this would generate the animation on-the-fly
        # For this prototype, we'll just return the action details
        
        metadata = {
            "action": action_name,
            "type": action_details["type"],
            "duration": action_details["duration"],
            "source": "generic"
        }
        
        return True, f"Action '{action_name}' triggered successfully (generic)", metadata
    
    def suggest_actions_for_input(self, input_text: str, max_suggestions: int = 3) -> List[str]:
        """
        Suggest actions based on user input text.
        
        Args:
            input_text: User input text
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggested action names
        """
        logger.info(f"Suggesting actions for input: '{input_text}'")
        
        input_lower = input_text.lower()
        suggested_actions = set()
        
        # Check for direct triggers
        for keyword, actions in self.action_triggers.items():
            if keyword in input_lower:
                for action in actions:
                    suggested_actions.add(action)
        
        # If we don't have enough suggestions, add some based on sentiment
        if len(suggested_actions) < max_suggestions:
            # Simple sentiment analysis (in a real implementation, this would be more sophisticated)
            positive_words = ["happy", "good", "great", "excellent", "wonderful", "love", "like", "enjoy"]
            negative_words = ["sad", "bad", "terrible", "awful", "hate", "dislike", "angry", "upset"]
            question_words = ["what", "how", "why", "when", "where", "who", "which"]
            
            # Check for positive sentiment
            if any(word in input_lower for word in positive_words):
                suggested_actions.update(self.response_categories["happy"][:2])
            
            # Check for negative sentiment
            if any(word in input_lower for word in negative_words):
                suggested_actions.update(self.response_categories["sad"][:2])
            
            # Check for questions
            if any(word in input_lower for word in question_words) or "?" in input_lower:
                suggested_actions.update(self.response_categories["thoughtful"][:2])
        
        # If we still don't have enough suggestions, add some random ones
        while len(suggested_actions) < max_suggestions:
            random_action = random.choice(list(self.standard_actions.keys()))
            suggested_actions.add(random_action)
        
        # Convert to list and limit to max_suggestions
        return list(suggested_actions)[:max_suggestions]
    
    def suggest_action_for_response(self, response_text: str) -> str:
        """
        Suggest an action based on the avatar's response text.
        
        Args:
            response_text: Avatar's response text
            
        Returns:
            Suggested action name
        """
        logger.info(f"Suggesting action for response: '{response_text}'")
        
        response_lower = response_text.lower()
        
        # Simple sentiment analysis (in a real implementation, this would be more sophisticated)
        positive_words = ["happy", "good", "great", "excellent", "wonderful", "love", "like", "enjoy"]
        negative_words = ["sad", "bad", "terrible", "awful", "hate", "dislike", "angry", "upset"]
        thoughtful_words = ["think", "consider", "perhaps", "maybe", "possibly", "interesting"]
        greeting_words = ["hello", "hi", "hey", "greetings", "welcome"]
        
        # Check for greetings
        if any(word in response_lower for word in greeting_words):
            return random.choice(self.response_categories["greeting"])
        
        # Check for positive sentiment
        if any(word in response_lower for word in positive_words):
            return random.choice(self.response_categories["happy"])
        
        # Check for negative sentiment
        if any(word in response_lower for word in negative_words):
            return random.choice(self.response_categories["sad"])
        
        # Check for thoughtful content
        if any(word in response_lower for word in thoughtful_words):
            return random.choice(self.response_categories["thoughtful"])
        
        # Check for questions
        if "?" in response_lower:
            return random.choice(self.response_categories["thoughtful"])
        
        # Default to a random neutral action
        return random.choice(["nod", "smile", "think"])
    
    def get_idle_action(self) -> str:
        """
        Get a random idle action.
        
        Returns:
            Idle action name
        """
        idle_actions = [name for name, details in self.standard_actions.items() 
                       if details["type"] == "idle"]
        
        return random.choice(idle_actions)
    
    def create_action_sequence(self, actions: List[str], 
                              transition_time: float = 0.5) -> Dict:
        """
        Create a sequence of actions with transitions.
        
        Args:
            actions: List of action names
            transition_time: Time between actions in seconds
            
        Returns:
            Dictionary with sequence details
        """
        logger.info(f"Creating action sequence with {len(actions)} actions")
        
        sequence = []
        total_duration = 0
        
        for i, action_name in enumerate(actions):
            action_details = self.get_action_details(action_name)
            
            start_time = total_duration
            duration = action_details["duration"]
            end_time = start_time + duration
            
            sequence.append({
                "action": action_name,
                "start_time": start_time,
                "duration": duration,
                "end_time": end_time,
                "type": action_details["type"]
            })
            
            total_duration = end_time
            
            # Add transition time if not the last action
            if i < len(actions) - 1:
                total_duration += transition_time
        
        return {
            "sequence": sequence,
            "total_duration": total_duration,
            "action_count": len(actions)
        }
    
    def create_conversation_actions(self, dialog: List[Dict]) -> Dict:
        """
        Create actions for a conversation based on dialog.
        
        Args:
            dialog: List of dialog exchanges (prompt/response pairs)
            
        Returns:
            Dictionary with conversation actions
        """
        logger.info(f"Creating conversation actions for {len(dialog)} exchanges")
        
        conversation_actions = []
        
        for exchange in dialog:
            prompt = exchange.get("prompt", "")
            response = exchange.get("response", "")
            
            # Suggest actions for user input
            user_actions = self.suggest_actions_for_input(prompt, max_suggestions=1)
            user_action = user_actions[0] if user_actions else "idle_breathe"
            
            # Suggest action for avatar response
            avatar_action = self.suggest_action_for_response(response)
            
            conversation_actions.append({
                "prompt": prompt,
                "response": response,
                "user_action": user_action,
                "avatar_action": avatar_action
            })
        
        return {
            "conversation_actions": conversation_actions,
            "exchange_count": len(dialog)
        }


# Example usage
if __name__ == "__main__":
    action_system = ActionSystem()
    print("Action System initialized and ready for use.")
