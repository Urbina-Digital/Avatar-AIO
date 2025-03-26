"""
Action System API Module for AI Avatar Platform

This module provides a unified API interface for the action system components,
allowing the frontend to interact with the action system.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('action_api')

# Import action system components
from action_system import ActionSystem
from action_trigger import ActionTrigger
from idle_animation import IdleAnimationSystem

class ActionSystemAPI:
    """API interface for action system components."""
    
    def __init__(self, models_dir: str = None):
        """
        Initialize the ActionSystemAPI.
        
        Args:
            models_dir: Directory containing trained models
        """
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
        
        self.models_dir = Path(models_dir)
        
        # Initialize components
        self.action_system = ActionSystem(models_dir)
        self.action_trigger = ActionTrigger(self.action_system)
        self.idle_system = IdleAnimationSystem(self.action_system)
        
        # Set up idle callback
        self.idle_system.set_idle_callback(self._handle_idle_action)
        
        # Active user sessions
        self.active_sessions = {}
        
        logger.info(f"ActionSystemAPI initialized with models directory: {self.models_dir}")
    
    def _handle_idle_action(self, action_details: Dict):
        """
        Handle idle action callback.
        
        Args:
            action_details: Details of the idle action
        """
        logger.info(f"Idle action triggered: {action_details}")
        # In a real implementation, this would notify the frontend
    
    def start_session(self, user_id: str) -> Dict:
        """
        Start an action system session for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Response dictionary with session details
        """
        logger.info(f"Starting action system session for user {user_id}")
        
        if user_id in self.active_sessions:
            return {
                "success": True,
                "message": f"Session already active for user {user_id}",
                "user_id": user_id,
                "session_id": self.active_sessions[user_id]["session_id"]
            }
        
        # Create a new session
        session_id = f"action_session_{user_id}_{id(threading.current_thread())}"
        
        # Start idle animation system
        self.idle_system.start(user_id)
        
        # Store session details
        self.active_sessions[user_id] = {
            "session_id": session_id,
            "start_time": threading.current_thread().name,
            "idle_system_active": True
        }
        
        return {
            "success": True,
            "message": f"Action system session started for user {user_id}",
            "user_id": user_id,
            "session_id": session_id
        }
    
    def end_session(self, user_id: str) -> Dict:
        """
        End an action system session for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Response dictionary with status
        """
        logger.info(f"Ending action system session for user {user_id}")
        
        if user_id not in self.active_sessions:
            return {
                "success": False,
                "message": f"No active session found for user {user_id}",
                "user_id": user_id
            }
        
        # Stop idle animation system
        self.idle_system.stop()
        
        # Remove session
        session_id = self.active_sessions[user_id]["session_id"]
        del self.active_sessions[user_id]
        
        return {
            "success": True,
            "message": f"Action system session ended for user {user_id}",
            "user_id": user_id,
            "session_id": session_id
        }
    
    def register_activity(self, user_id: str) -> Dict:
        """
        Register user activity to reset the idle timer.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Response dictionary with status
        """
        logger.info(f"Registering activity for user {user_id}")
        
        if user_id not in self.active_sessions:
            return {
                "success": False,
                "message": f"No active session found for user {user_id}",
                "user_id": user_id
            }
        
        # Reset idle timer
        self.idle_system.register_activity()
        
        return {
            "success": True,
            "message": f"Activity registered for user {user_id}",
            "user_id": user_id
        }
    
    def trigger_action(self, user_id: str, action_name: str) -> Dict:
        """
        Trigger a specific action for the avatar.
        
        Args:
            user_id: Unique identifier for the user
            action_name: Name of the action to trigger
            
        Returns:
            Response dictionary with action details
        """
        logger.info(f"Triggering action '{action_name}' for user {user_id}")
        
        # Register activity to reset idle timer
        self.register_activity(user_id)
        
        # Trigger the action
        success, message, metadata = self.action_system.trigger_action(user_id, action_name)
        
        return {
            "success": success,
            "message": message,
            "action": action_name,
            "user_id": user_id,
            "metadata": metadata
        }
    
    def analyze_input(self, user_id: str, input_text: str) -> Dict:
        """
        Analyze user input for action triggers.
        
        Args:
            user_id: Unique identifier for the user
            input_text: User input text
            
        Returns:
            Response dictionary with analysis results
        """
        logger.info(f"Analyzing input for user {user_id}: '{input_text}'")
        
        # Register activity to reset idle timer
        self.register_activity(user_id)
        
        # Analyze the input
        analysis = self.action_trigger.analyze_input(input_text)
        
        # If there's a top action, trigger it
        if analysis.get("top_action"):
            action_name = analysis["top_action"]
            success, message, metadata = self.action_system.trigger_action(user_id, action_name)
            
            if success:
                analysis["triggered_action"] = {
                    "action": action_name,
                    "message": message,
                    "metadata": metadata
                }
        
        return {
            "success": True,
            "message": "Input analyzed successfully",
            "user_id": user_id,
            "analysis": analysis
        }
    
    def analyze_response(self, user_id: str, response_text: str) -> Dict:
        """
        Analyze avatar response for appropriate actions.
        
        Args:
            user_id: Unique identifier for the user
            response_text: Avatar's response text
            
        Returns:
            Response dictionary with analysis results
        """
        logger.info(f"Analyzing response for user {user_id}: '{response_text}'")
        
        # Register activity to reset idle timer
        self.register_activity(user_id)
        
        # Analyze the response
        analysis = self.action_trigger.analyze_response(response_text)
        
        # If there's a suggested action, trigger it
        if analysis.get("suggested_action"):
            action_name = analysis["suggested_action"]
            success, message, metadata = self.action_system.trigger_action(user_id, action_name)
            
            if success:
                analysis["triggered_action"] = {
                    "action": action_name,
                    "message": message,
                    "metadata": metadata
                }
        
        return {
            "success": True,
            "message": "Response analyzed successfully",
            "user_id": user_id,
            "analysis": analysis
        }
    
    def get_all_actions(self) -> Dict:
        """
        Get all available actions grouped by type.
        
        Returns:
            Response dictionary with actions grouped by type
        """
        logger.info("Getting all available actions")
        
        actions_by_type = self.action_system.get_all_actions()
        
        return {
            "success": True,
            "message": "Actions retrieved successfully",
            "actions_by_type": actions_by_type,
            "total_actions": sum(len(actions) for actions in actions_by_type.values())
        }
    
    def create_action_sequence(self, user_id: str, actions: List[str]) -> Dict:
        """
        Create a sequence of actions with transitions.
        
        Args:
            user_id: Unique identifier for the user
            actions: List of action names
            
        Returns:
            Response dictionary with sequence details
        """
        logger.info(f"Creating action sequence for user {user_id} with {len(actions)} actions")
        
        # Register activity to reset idle timer
        self.register_activity(user_id)
        
        # Create the sequence
        sequence = self.action_system.create_action_sequence(actions)
        
        return {
            "success": True,
            "message": f"Action sequence created with {len(actions)} actions",
            "user_id": user_id,
            "sequence": sequence
        }
    
    def set_idle_parameters(self, timeout: float = None, 
                           min_interval: float = None, 
                           max_interval: float = None) -> Dict:
        """
        Set parameters for the idle animation system.
        
        Args:
            timeout: Seconds of inactivity before idle animations start
            min_interval: Minimum seconds between idle animations
            max_interval: Maximum seconds between idle animations
            
        Returns:
            Response dictionary with updated parameters
        """
        logger.info("Setting idle animation parameters")
        
        if timeout is not None:
            self.idle_system.set_idle_timeout(timeout)
        
        if min_interval is not None and max_interval is not None:
            self.idle_system.set_idle_interval(min_interval, max_interval)
        
        return {
            "success": True,
            "message": "Idle animation parameters updated",
            "idle_timeout": self.idle_system.idle_timeout,
            "idle_interval": self.idle_system.idle_interval
        }


# Example usage
if __name__ == "__main__":
    api = ActionSystemAPI()
    print("Action System API initialized and ready for use.")
