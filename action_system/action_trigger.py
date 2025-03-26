"""
Action Trigger Module for AI Avatar Platform

This module handles the triggering of avatar actions based on user input
and avatar responses.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import random
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('action_trigger')

class ActionTrigger:
    """Triggers avatar actions based on user input and avatar responses."""
    
    def __init__(self, action_system=None):
        """
        Initialize the ActionTrigger.
        
        Args:
            action_system: Reference to the ActionSystem
        """
        self.action_system = action_system
        
        # Define command patterns for direct action triggering
        self.command_patterns = [
            (r"^/(\w+)$", "Command: /{action}"),
            (r"^!(\w+)$", "Command: !{action}"),
            (r"^(\w+)!$", "Command: {action}!"),
            (r"please (\w+)", "Request: please {action}"),
            (r"do a (\w+)", "Request: do a {action}"),
            (r"do the (\w+)", "Request: do the {action}"),
            (r"can you (\w+)", "Request: can you {action}"),
            (r"(\w+) now", "Request: {action} now"),
            (r"(\w+) please", "Request: {action} please")
        ]
        
        # Define emotion patterns for sentiment-based action triggering
        self.emotion_patterns = {
            "happy": [
                r"i('m| am) (happy|glad|excited|thrilled)",
                r"that('s| is) (great|awesome|amazing|wonderful)",
                r"(yay|woohoo|hurray|congratulations)"
            ],
            "sad": [
                r"i('m| am) (sad|upset|depressed|unhappy)",
                r"that('s| is) (terrible|awful|sad|unfortunate)",
                r"(sigh|alas|unfortunately)"
            ],
            "angry": [
                r"i('m| am) (angry|mad|furious|annoyed)",
                r"that('s| is) (infuriating|annoying|frustrating)",
                r"(grr|argh|damn)"
            ],
            "surprised": [
                r"i('m| am) (surprised|shocked|amazed|astonished)",
                r"that('s| is) (surprising|shocking|unexpected)",
                r"(wow|whoa|oh my)"
            ],
            "confused": [
                r"i('m| am) (confused|puzzled|perplexed)",
                r"that('s| is) (confusing|puzzling|perplexing)",
                r"(huh|hmm|um)"
            ]
        }
        
        # Define action-emotion mappings
        self.emotion_actions = {
            "happy": ["smile", "laugh", "dance", "jump"],
            "sad": ["sad", "shake_head"],
            "angry": ["angry", "shake_head"],
            "surprised": ["surprised"],
            "confused": ["think", "shrug"]
        }
        
        logger.info("ActionTrigger initialized")
    
    def detect_direct_commands(self, input_text: str) -> List[Dict]:
        """
        Detect direct action commands in user input.
        
        Args:
            input_text: User input text
            
        Returns:
            List of detected commands with action names
        """
        input_lower = input_text.lower()
        detected_commands = []
        
        for pattern, template in self.command_patterns:
            matches = re.finditer(pattern, input_lower)
            
            for match in matches:
                action_name = match.group(1)
                
                # Check if it's a valid action
                if self.action_system and action_name in self.action_system.standard_actions:
                    command_text = template.format(action=action_name)
                    
                    detected_commands.append({
                        "action": action_name,
                        "command_text": command_text,
                        "confidence": 0.9,  # High confidence for direct commands
                        "match": match.group(0)
                    })
        
        return detected_commands
    
    def detect_emotions(self, input_text: str) -> Dict[str, float]:
        """
        Detect emotions in user input.
        
        Args:
            input_text: User input text
            
        Returns:
            Dictionary mapping emotions to confidence scores
        """
        input_lower = input_text.lower()
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            
            for pattern in patterns:
                matches = re.finditer(pattern, input_lower)
                for match in matches:
                    # Increase score based on match length relative to input length
                    match_length = len(match.group(0))
                    score += match_length / len(input_lower) * 0.5
            
            if score > 0:
                emotion_scores[emotion] = min(score, 0.9)  # Cap at 0.9
        
        return emotion_scores
    
    def suggest_actions_from_emotions(self, emotion_scores: Dict[str, float], 
                                     max_suggestions: int = 2) -> List[Dict]:
        """
        Suggest actions based on detected emotions.
        
        Args:
            emotion_scores: Dictionary mapping emotions to confidence scores
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggested actions with confidence scores
        """
        suggested_actions = []
        
        # Sort emotions by score in descending order
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        for emotion, score in sorted_emotions:
            if emotion in self.emotion_actions:
                actions = self.emotion_actions[emotion]
                
                for action in actions:
                    # Check if we already have this action
                    if any(a["action"] == action for a in suggested_actions):
                        continue
                    
                    suggested_actions.append({
                        "action": action,
                        "emotion": emotion,
                        "confidence": score,
                        "source": "emotion"
                    })
                    
                    if len(suggested_actions) >= max_suggestions:
                        break
            
            if len(suggested_actions) >= max_suggestions:
                break
        
        return suggested_actions
    
    def analyze_input(self, input_text: str, max_suggestions: int = 3) -> Dict:
        """
        Analyze user input for action triggers.
        
        Args:
            input_text: User input text
            max_suggestions: Maximum number of action suggestions to return
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing input for action triggers: '{input_text}'")
        
        # Detect direct commands
        commands = self.detect_direct_commands(input_text)
        
        # Detect emotions
        emotion_scores = self.detect_emotions(input_text)
        
        # Suggest actions from emotions
        emotion_actions = self.suggest_actions_from_emotions(emotion_scores)
        
        # Get keyword-based suggestions if we have an action system
        keyword_actions = []
        if self.action_system:
            action_names = self.action_system.suggest_actions_for_input(input_text, max_suggestions)
            
            for action_name in action_names:
                # Check if we already have this action from commands or emotions
                if any(a["action"] == action_name for a in commands) or \
                   any(a["action"] == action_name for a in emotion_actions):
                    continue
                
                keyword_actions.append({
                    "action": action_name,
                    "confidence": 0.7,  # Medium confidence for keyword matches
                    "source": "keyword"
                })
        
        # Combine all suggestions
        all_suggestions = commands + emotion_actions + keyword_actions
        
        # Sort by confidence and limit to max_suggestions
        sorted_suggestions = sorted(all_suggestions, key=lambda x: x.get("confidence", 0), reverse=True)
        final_suggestions = sorted_suggestions[:max_suggestions]
        
        return {
            "input_text": input_text,
            "has_direct_command": len(commands) > 0,
            "emotions": emotion_scores,
            "suggested_actions": final_suggestions,
            "top_action": final_suggestions[0]["action"] if final_suggestions else None
        }
    
    def analyze_response(self, response_text: str) -> Dict:
        """
        Analyze avatar response for appropriate actions.
        
        Args:
            response_text: Avatar's response text
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing response for actions: '{response_text}'")
        
        # Detect emotions in the response
        emotion_scores = self.detect_emotions(response_text)
        
        # Get action suggestion from action system
        suggested_action = None
        if self.action_system:
            suggested_action = self.action_system.suggest_action_for_response(response_text)
        
        # If no suggestion from action system, use emotion-based suggestion
        if not suggested_action and emotion_scores:
            top_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            if top_emotion in self.emotion_actions:
                suggested_action = random.choice(self.emotion_actions[top_emotion])
        
        # If still no suggestion, use a default
        if not suggested_action:
            suggested_action = "idle_breathe"
        
        return {
            "response_text": response_text,
            "emotions": emotion_scores,
            "suggested_action": suggested_action
        }
    
    def process_conversation(self, dialog: List[Dict]) -> Dict:
        """
        Process a conversation to suggest actions for each exchange.
        
        Args:
            dialog: List of dialog exchanges (prompt/response pairs)
            
        Returns:
            Dictionary with suggested actions for each exchange
        """
        logger.info(f"Processing conversation with {len(dialog)} exchanges")
        
        processed_dialog = []
        
        for exchange in dialog:
            prompt = exchange.get("prompt", "")
            response = exchange.get("response", "")
            
            # Analyze user input
            input_analysis = self.analyze_input(prompt)
            
            # Analyze avatar response
            response_analysis = self.analyze_response(response)
            
            processed_dialog.append({
                "prompt": prompt,
                "response": response,
                "input_analysis": input_analysis,
                "response_analysis": response_analysis,
                "user_action": input_analysis.get("top_action"),
                "avatar_action": response_analysis.get("suggested_action")
            })
        
        return {
            "processed_dialog": processed_dialog,
            "exchange_count": len(dialog)
        }


# Example usage
if __name__ == "__main__":
    from action_system import ActionSystem
    
    action_system = ActionSystem()
    trigger = ActionTrigger(action_system)
    
    print("Action Trigger initialized and ready for use.")
