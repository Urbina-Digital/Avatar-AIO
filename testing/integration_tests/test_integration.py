"""
Integration Tests for AI Avatar Platform

This module contains integration tests for the AI Avatar Platform,
testing the interaction between different components.
"""

import os
import sys
import unittest
import json
from pathlib import Path
import tempfile
import shutil
import time
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from data_handling.data_handler import DataHandler
from model_training.model_training_api import ModelTrainingAPI
from action_system.action_api import ActionSystemAPI
from integration.avatar_controller import AvatarController
from compute_management.resource_manager import ResourceManager
from testing.sample_data.sample_data_generator import SampleDataGenerator

class TestEndToEndFlow(unittest.TestCase):
    """Test cases for end-to-end flow of the AI Avatar Platform."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        os.makedirs(os.path.join(self.test_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'models'), exist_ok=True)
        
        # Create sample data generator
        self.sample_data_generator = SampleDataGenerator(
            output_dir=os.path.join(self.test_dir, 'data')
        )
        
        # Generate sample data
        self.sample_data_generator.generate_all_sample_data(user_id='test_user')
        
        # Create components
        self.data_handler = DataHandler(
            base_dir=os.path.join(self.test_dir, 'data')
        )
        
        self.model_training_api = ModelTrainingAPI(
            base_dir=os.path.join(self.test_dir, 'data'),
            output_dir=os.path.join(self.test_dir, 'models')
        )
        
        self.action_api = ActionSystemAPI(
            models_dir=os.path.join(self.test_dir, 'models')
        )
        
        self.avatar_controller = AvatarController(
            base_dir=self.test_dir
        )
        
        self.resource_manager = ResourceManager()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_data_to_model_flow(self):
        """Test flow from data handling to model training."""
        # Get data directories
        appearance_dir = os.path.join(self.test_dir, 'data', 'appearance', 'test_user')
        voice_dir = os.path.join(self.test_dir, 'data', 'voice', 'test_user')
        communication_dir = os.path.join(self.test_dir, 'data', 'communication', 'test_user')
        
        # Preprocess data
        appearance_result = self.data_handler.preprocess_appearance_data(appearance_dir)
        voice_result = self.data_handler.preprocess_voice_data(voice_dir)
        communication_result = self.data_handler.preprocess_communication_data(communication_dir)
        
        # Check preprocessing results
        self.assertTrue(appearance_result['success'])
        self.assertTrue(voice_result['success'])
        self.assertTrue(communication_result['success'])
        
        # Train models
        appearance_train_result = self.model_training_api.train_appearance_model('test_user')
        voice_train_result = self.model_training_api.train_voice_model('test_user')
        communication_train_result = self.model_training_api.train_communication_model('test_user')
        
        # Check training results
        self.assertTrue(appearance_train_result['success'])
        self.assertTrue(voice_train_result['success'])
        self.assertTrue(communication_train_result['success'])
        
        # Check model files
        self.assertTrue(os.path.exists(appearance_train_result['model_path']))
        self.assertTrue(os.path.exists(voice_train_result['model_path']))
        self.assertTrue(os.path.exists(communication_train_result['model_path']))
    
    def test_model_to_action_flow(self):
        """Test flow from model training to action system."""
        # Train models
        appearance_train_result = self.model_training_api.train_appearance_model('test_user')
        voice_train_result = self.model_training_api.train_voice_model('test_user')
        communication_train_result = self.model_training_api.train_communication_model('test_user')
        
        # Check training results
        self.assertTrue(appearance_train_result['success'])
        self.assertTrue(voice_train_result['success'])
        self.assertTrue(communication_train_result['success'])
        
        # Trigger action
        action_result = self.action_api.trigger_action('test_user', 'wave')
        
        # Check action result
        self.assertTrue(action_result['success'])
        
        # Generate response
        response_result = self.model_training_api.generate_response('test_user', 'Hello, how are you?')
        
        # Check response result
        self.assertTrue(response_result['success'])
        self.assertIsNotNone(response_result['response'])
        
        # Synthesize speech
        speech_result = self.model_training_api.synthesize_speech('test_user', response_result['response'])
        
        # Check speech result
        self.assertTrue(speech_result['success'])
        self.assertTrue(os.path.exists(speech_result['metadata']['path']))
    
    def test_avatar_controller_flow(self):
        """Test flow through the avatar controller."""
        # Start session
        session_result = self.avatar_controller.start_session('test_user')
        
        # Check session result
        self.assertTrue(session_result['success'])
        
        # Process user input
        input_result = self.avatar_controller.process_user_input('test_user', 'Hello, can you wave at me?')
        
        # Check input result
        self.assertTrue(input_result['success'])
        self.assertIsNotNone(input_result['response']['text'])
        
        # Trigger action
        action_result = self.avatar_controller.trigger_action('test_user', 'wave')
        
        # Check action result
        self.assertTrue(action_result['success'])
        
        # Get avatar status
        status_result = self.avatar_controller.get_avatar_status('test_user')
        
        # Check status result
        self.assertTrue(status_result['success'])
        
        # End session
        end_result = self.avatar_controller.end_session('test_user')
        
        # Check end result
        self.assertTrue(end_result['success'])
    
    def test_resource_management_flow(self):
        """Test flow through the resource manager."""
        # Get resource summary
        summary = self.resource_manager.get_resource_summary()
        
        # Check summary
        self.assertIn('hardware_summary', summary)
        self.assertIn('can_run_locally', summary)
        self.assertIn('should_use_cloud', summary)
        
        # Train appearance model
        job_info = self.resource_manager.train_appearance_model(
            'test_user',
            os.path.join(self.test_dir, 'data', 'appearance', 'test_user')
        )
        
        # Check job info
        self.assertIn('job_id', job_info)
        self.assertEqual(job_info['job_type'], 'train_appearance')
        
        # Wait for job to complete (in a real test, would use proper waiting mechanism)
        time.sleep(2)
        
        # Get job status
        status = self.resource_manager.get_job_status(job_info['job_id'])
        
        # Check status
        self.assertIn('job_id', status)
        self.assertIn('status', status)


class TestConcurrentOperations(unittest.TestCase):
    """Test cases for concurrent operations in the AI Avatar Platform."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        os.makedirs(os.path.join(self.test_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'models'), exist_ok=True)
        
        # Create sample data generator
        self.sample_data_generator = SampleDataGenerator(
            output_dir=os.path.join(self.test_dir, 'data')
        )
        
        # Generate sample data for multiple users
        self.sample_data_generator.generate_all_sample_data(user_id='user1')
        self.sample_data_generator.generate_all_sample_data(user_id='user2')
        self.sample_data_generator.generate_all_sample_data(user_id='user3')
        
        # Create avatar controller
        self.avatar_controller = AvatarController(
            base_dir=self.test_dir
        )
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_concurrent_sessions(self):
        """Test concurrent avatar sessions."""
        # Start sessions for multiple users
        session1 = self.avatar_controller.start_session('user1')
        session2 = self.avatar_controller.start_session('user2')
        session3 = self.avatar_controller.start_session('user3')
        
        # Check session results
        self.assertTrue(session1['success'])
        self.assertTrue(session2['success'])
        self.assertTrue(session3['success'])
        
        # Process inputs concurrently
        def process_input(user_id, input_text):
            return self.avatar_controller.process_user_input(user_id, input_text)
        
        # Create threads
        thread1 = threading.Thread(target=process_input, args=('user1', 'Hello from user1'))
        thread2 = threading.Thread(target=process_input, args=('user2', 'Hello from user2'))
        thread3 = threading.Thread(target=process_input, args=('user3', 'Hello from user3'))
        
        # Start threads
        thread1.start()
        thread2.start()
        thread3.start()
        
        # Wait for threads to complete
        thread1.join()
        thread2.join()
        thread3.join()
        
        # Get pending responses
        responses1 = self.avatar_controller.get_pending_responses('user1', False)
        responses2 = self.avatar_controller.get_pending_responses('user2', False)
        responses3 = self.avatar_controller.get_pending_responses('user3', False)
        
        # Check responses
        self.assertTrue(responses1['success'])
        self.assertTrue(responses2['success'])
        self.assertTrue(responses3['success'])
        
        # End sessions
        end1 = self.avatar_controller.end_session('user1')
        end2 = self.avatar_controller.end_session('user2')
        end3 = self.avatar_controller.end_session('user3')
        
        # Check end results
        self.assertTrue(end1['success'])
        self.assertTrue(end2['success'])
        self.assertTrue(end3['success'])


if __name__ == '__main__':
    unittest.main()
