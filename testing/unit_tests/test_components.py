"""
Unit Tests for AI Avatar Platform

This module contains unit tests for the various components of the AI Avatar Platform.
"""

import os
import sys
import unittest
import json
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from data_handling.data_handler import DataHandler
from data_handling.data_validator import DataValidator
from model_training.appearance.appearance_trainer import AppearanceTrainer
from model_training.voice.voice_trainer import VoiceTrainer
from model_training.communication.communication_trainer import CommunicationTrainer
from action_system.action_system import ActionSystem
from compute_management.hardware_detector import HardwareDetector
from testing.sample_data.sample_data_generator import SampleDataGenerator

class TestDataHandling(unittest.TestCase):
    """Test cases for data handling components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample data generator
        self.sample_data_generator = SampleDataGenerator(output_dir=self.test_dir)
        
        # Generate sample data
        self.sample_data_generator.generate_all_sample_data(user_id='test_user')
        
        # Create data handler
        self.data_handler = DataHandler(base_dir=self.test_dir)
        
        # Create data validator
        self.data_validator = DataValidator()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_appearance_data_validation(self):
        """Test appearance data validation."""
        # Get appearance data directory
        appearance_dir = os.path.join(self.test_dir, 'appearance', 'test_user')
        
        # Validate appearance data
        result = self.data_validator.validate_appearance_data(appearance_dir)
        
        # Check validation result
        self.assertTrue(result['valid'])
        self.assertEqual(result['num_images'], 10)
    
    def test_voice_data_validation(self):
        """Test voice data validation."""
        # Get voice data directory
        voice_dir = os.path.join(self.test_dir, 'voice', 'test_user')
        
        # Validate voice data
        result = self.data_validator.validate_voice_data(voice_dir)
        
        # Check validation result
        self.assertTrue(result['valid'])
        self.assertEqual(result['num_samples'], 10)
        self.assertGreaterEqual(result['total_duration'], 10.0)  # At least 10 seconds
    
    def test_communication_data_validation(self):
        """Test communication data validation."""
        # Get communication data directory
        communication_dir = os.path.join(self.test_dir, 'communication', 'test_user')
        
        # Validate communication data
        result = self.data_validator.validate_communication_data(communication_dir)
        
        # Check validation result
        self.assertTrue(result['valid'])
        self.assertEqual(result['num_samples'], 20)
    
    def test_data_preprocessing(self):
        """Test data preprocessing."""
        # Get data directories
        appearance_dir = os.path.join(self.test_dir, 'appearance', 'test_user')
        voice_dir = os.path.join(self.test_dir, 'voice', 'test_user')
        communication_dir = os.path.join(self.test_dir, 'communication', 'test_user')
        
        # Preprocess appearance data
        appearance_result = self.data_handler.preprocess_appearance_data(appearance_dir)
        
        # Preprocess voice data
        voice_result = self.data_handler.preprocess_voice_data(voice_dir)
        
        # Preprocess communication data
        communication_result = self.data_handler.preprocess_communication_data(communication_dir)
        
        # Check preprocessing results
        self.assertTrue(appearance_result['success'])
        self.assertTrue(voice_result['success'])
        self.assertTrue(communication_result['success'])


class TestModelTraining(unittest.TestCase):
    """Test cases for model training components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample data generator
        self.sample_data_generator = SampleDataGenerator(output_dir=self.test_dir)
        
        # Generate sample data
        self.sample_data_generator.generate_all_sample_data(user_id='test_user')
        
        # Create trainers
        self.appearance_trainer = AppearanceTrainer(
            data_dir=os.path.join(self.test_dir, 'appearance'),
            output_dir=os.path.join(self.test_dir, 'models', 'appearance')
        )
        
        self.voice_trainer = VoiceTrainer(
            data_dir=os.path.join(self.test_dir, 'voice'),
            output_dir=os.path.join(self.test_dir, 'models', 'voice')
        )
        
        self.communication_trainer = CommunicationTrainer(
            data_dir=os.path.join(self.test_dir, 'communication'),
            output_dir=os.path.join(self.test_dir, 'models', 'communication')
        )
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_appearance_training(self):
        """Test appearance model training."""
        # Train appearance model
        result = self.appearance_trainer.train_model('test_user')
        
        # Check training result
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['model_path']))
    
    def test_voice_training(self):
        """Test voice model training."""
        # Train voice model
        result = self.voice_trainer.train_model('test_user')
        
        # Check training result
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['model_path']))
    
    def test_communication_training(self):
        """Test communication model training."""
        # Train communication model
        result = self.communication_trainer.train_model('test_user')
        
        # Check training result
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['model_path']))
    
    def test_appearance_inference(self):
        """Test appearance model inference."""
        # Train appearance model
        train_result = self.appearance_trainer.train_model('test_user')
        
        # Generate image for action
        result = self.appearance_trainer.generate_image_for_action('test_user', 'wave')
        
        # Check inference result
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['image_path']))
    
    def test_voice_inference(self):
        """Test voice model inference."""
        # Train voice model
        train_result = self.voice_trainer.train_model('test_user')
        
        # Synthesize speech
        result = self.voice_trainer.synthesize_speech('test_user', 'Hello, this is a test.')
        
        # Check inference result
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['audio_path']))
    
    def test_communication_inference(self):
        """Test communication model inference."""
        # Train communication model
        train_result = self.communication_trainer.train_model('test_user')
        
        # Generate response
        result = self.communication_trainer.generate_response('test_user', 'Hello, how are you?')
        
        # Check inference result
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['response'])
        self.assertGreater(len(result['response']), 0)


class TestActionSystem(unittest.TestCase):
    """Test cases for action system components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create action system
        self.action_system = ActionSystem(models_dir=os.path.join(self.test_dir, 'models'))
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_action_triggering(self):
        """Test action triggering."""
        # Trigger action
        result = self.action_system.trigger_action('test_user', 'wave')
        
        # Check result
        self.assertTrue(result['success'])
    
    def test_input_analysis(self):
        """Test input analysis."""
        # Analyze input
        result = self.action_system.analyze_input('test_user', 'Hello, can you wave at me?')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertIn('analysis', result)
        self.assertIn('top_action', result['analysis'])
    
    def test_response_analysis(self):
        """Test response analysis."""
        # Analyze response
        result = self.action_system.analyze_response('test_user', 'Hello! *waves* Nice to meet you!')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertIn('analysis', result)
        self.assertIn('suggested_action', result['analysis'])
    
    def test_idle_animation(self):
        """Test idle animation system."""
        # Start idle animation
        self.action_system.start_idle_animation('test_user')
        
        # Check if idle animation is running
        self.assertTrue(self.action_system.is_idle_animation_running('test_user'))
        
        # Stop idle animation
        self.action_system.stop_idle_animation('test_user')
        
        # Check if idle animation is stopped
        self.assertFalse(self.action_system.is_idle_animation_running('test_user'))


class TestComputeManagement(unittest.TestCase):
    """Test cases for compute management components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create hardware detector
        self.hardware_detector = HardwareDetector()
    
    def test_hardware_detection(self):
        """Test hardware detection."""
        # Detect hardware
        hardware_info = self.hardware_detector.detect_hardware()
        
        # Check hardware info
        self.assertIn('cpu', hardware_info)
        self.assertIn('ram', hardware_info)
        self.assertIn('disk', hardware_info)
        self.assertIn('gpu', hardware_info)
        self.assertIn('platform', hardware_info)
    
    def test_requirements_check(self):
        """Test requirements check."""
        # Detect hardware
        hardware_info = self.hardware_detector.detect_hardware()
        
        # Check requirements
        requirement_check = self.hardware_detector.check_requirements(hardware_info)
        
        # Check requirement check result
        self.assertIn('cpu', requirement_check)
        self.assertIn('ram', requirement_check)
        self.assertIn('disk', requirement_check)
        self.assertIn('gpu', requirement_check)
        self.assertIn('overall', requirement_check)


if __name__ == '__main__':
    unittest.main()
