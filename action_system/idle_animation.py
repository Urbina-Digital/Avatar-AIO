"""
Idle Animation System Module for AI Avatar Platform

This module handles the generation and management of idle animations
when the avatar is not actively responding to user input.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import random
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('idle_animation')

class IdleAnimationSystem:
    """Manages idle animations for the avatar."""
    
    def __init__(self, action_system=None):
        """
        Initialize the IdleAnimationSystem.
        
        Args:
            action_system: Reference to the ActionSystem
        """
        self.action_system = action_system
        self.is_running = False
        self.idle_thread = None
        self.last_activity_time = time.time()
        self.idle_timeout = 5.0  # Seconds of inactivity before idle animations start
        self.idle_interval = (3.0, 10.0)  # Min and max seconds between idle animations
        self.current_idle_action = None
        self.idle_callback = None
        
        # Define idle actions with weights
        self.idle_actions = {
            "idle_breathe": 10,
            "idle_look_around": 7,
            "idle_shift_weight": 5,
            "idle_check_phone": 3,
            "idle_stretch": 2
        }
        
        # Define idle sequences for variety
        self.idle_sequences = [
            ["idle_breathe", "idle_look_around", "idle_breathe"],
            ["idle_shift_weight", "idle_check_phone", "idle_look_around"],
            ["idle_breathe", "idle_stretch", "idle_breathe"],
            ["idle_look_around", "idle_shift_weight", "idle_look_around"]
        ]
        
        logger.info("IdleAnimationSystem initialized")
    
    def set_idle_callback(self, callback):
        """
        Set the callback function to be called when an idle action is triggered.
        
        Args:
            callback: Function to call with idle action details
        """
        self.idle_callback = callback
    
    def register_activity(self):
        """Register user activity to reset the idle timer."""
        self.last_activity_time = time.time()
        self.current_idle_action = None
    
    def select_idle_action(self) -> str:
        """
        Select an idle action based on weights.
        
        Returns:
            Selected idle action name
        """
        # Create a weighted list of actions
        weighted_actions = []
        for action, weight in self.idle_actions.items():
            weighted_actions.extend([action] * weight)
        
        # Select a random action
        return random.choice(weighted_actions)
    
    def select_idle_sequence(self) -> List[str]:
        """
        Select an idle action sequence.
        
        Returns:
            List of idle action names
        """
        # Either select a predefined sequence or create a random one
        if random.random() < 0.7:  # 70% chance of using a predefined sequence
            return random.choice(self.idle_sequences)
        else:
            # Create a random sequence of 2-3 idle actions
            sequence_length = random.randint(2, 3)
            return [self.select_idle_action() for _ in range(sequence_length)]
    
    def _idle_loop(self, user_id: str):
        """
        Background thread for idle animations.
        
        Args:
            user_id: Unique identifier for the user
        """
        logger.info(f"Starting idle animation loop for user {user_id}")
        
        while self.is_running:
            current_time = time.time()
            time_since_activity = current_time - self.last_activity_time
            
            # Check if we should trigger an idle animation
            if time_since_activity >= self.idle_timeout and not self.current_idle_action:
                # Decide whether to use a single action or a sequence
                if random.random() < 0.3:  # 30% chance of using a sequence
                    idle_sequence = self.select_idle_sequence()
                    logger.info(f"Triggering idle sequence: {idle_sequence}")
                    
                    if self.action_system:
                        sequence_details = self.action_system.create_action_sequence(idle_sequence)
                        self.current_idle_action = {
                            "type": "sequence",
                            "actions": idle_sequence,
                            "details": sequence_details
                        }
                else:
                    # Select a single idle action
                    idle_action = self.select_idle_action()
                    logger.info(f"Triggering idle action: {idle_action}")
                    
                    if self.action_system:
                        success, message, metadata = self.action_system.trigger_action(user_id, idle_action)
                        if success:
                            self.current_idle_action = {
                                "type": "single",
                                "action": idle_action,
                                "metadata": metadata
                            }
                
                # Call the callback if set
                if self.idle_callback and self.current_idle_action:
                    self.idle_callback(self.current_idle_action)
                
                # Reset the idle action after a delay
                idle_duration = random.uniform(*self.idle_interval)
                time.sleep(idle_duration)
                self.current_idle_action = None
            
            # Sleep a short time before checking again
            time.sleep(0.5)
    
    def start(self, user_id: str):
        """
        Start the idle animation system.
        
        Args:
            user_id: Unique identifier for the user
        """
        if not self.is_running:
            self.is_running = True
            self.last_activity_time = time.time()
            self.idle_thread = threading.Thread(target=self._idle_loop, args=(user_id,))
            self.idle_thread.daemon = True
            self.idle_thread.start()
            logger.info(f"Idle animation system started for user {user_id}")
    
    def stop(self):
        """Stop the idle animation system."""
        if self.is_running:
            self.is_running = False
            if self.idle_thread:
                self.idle_thread.join(timeout=1.0)
            logger.info("Idle animation system stopped")
    
    def set_idle_timeout(self, timeout: float):
        """
        Set the idle timeout.
        
        Args:
            timeout: Seconds of inactivity before idle animations start
        """
        self.idle_timeout = max(1.0, timeout)
        logger.info(f"Idle timeout set to {self.idle_timeout} seconds")
    
    def set_idle_interval(self, min_interval: float, max_interval: float):
        """
        Set the interval between idle animations.
        
        Args:
            min_interval: Minimum seconds between idle animations
            max_interval: Maximum seconds between idle animations
        """
        self.idle_interval = (max(1.0, min_interval), max(min_interval, max_interval))
        logger.info(f"Idle interval set to {self.idle_interval} seconds")


# Example usage
if __name__ == "__main__":
    from action_system import ActionSystem
    
    def idle_callback(action_details):
        print(f"Idle action triggered: {action_details}")
    
    action_system = ActionSystem()
    idle_system = IdleAnimationSystem(action_system)
    idle_system.set_idle_callback(idle_callback)
    
    print("Idle Animation System initialized and ready for use.")
