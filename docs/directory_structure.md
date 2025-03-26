# AI Avatar Platform - Directory Structure and File Placement Guide

This document provides a comprehensive guide on how to organize the files for the AI Avatar Platform, including where to place the newly implemented functional components.

## Complete Directory Structure

```
ai_avatar_platform/
│
├── main.py                          # Main entry point for the application
├── setup.py                         # Setup script for installing dependencies
├── config.json                      # Configuration file (created automatically)
│
├── docs/                            # Documentation
│   ├── architecture.md              # Architecture documentation
│   ├── how_to_use.md                # User guide
│   ├── security_and_data_handling.md # Security documentation
│   └── directory_structure.md       # This file
│
├── data/                            # Data storage
│   ├── appearance/                  # Appearance data
│   │   └── [user_id]/               # User-specific appearance data
│   │       ├── uploads/             # Original uploaded files
│   │       └── generated/           # Generated images
│   │
│   ├── voice/                       # Voice data
│   │   └── [user_id]/               # User-specific voice data
│   │       ├── uploads/             # Original uploaded audio files
│   │       └── generated/           # Generated audio files
│   │
│   └── communication/               # Communication data
│       └── [user_id]/               # User-specific communication data
│           └── dialog_samples/      # Dialog sample files
│
├── models/                          # Trained models
│   ├── appearance/                  # Appearance models
│   │   └── [user_id]/               # User-specific appearance models
│   │       ├── model.safetensors    # LoRA model file
│   │       └── model_info.json      # Model metadata
│   │
│   ├── voice/                       # Voice models
│   │   └── [user_id]/               # User-specific voice models
│   │       ├── model.bin            # Voice model file
│   │       └── model_info.json      # Model metadata
│   │
│   └── communication/               # Communication models
│       └── [user_id]/               # User-specific communication models
│           ├── communication_style.txt # Communication style instructions
│           └── model_info.json      # Model metadata
│
├── data_handling/                   # Data handling module
│   ├── data_handler.py              # Core data handling functionality
│   ├── upload_handler.py            # Handles file uploads
│   ├── data_validator.py            # Validates uploaded data
│   ├── sample_data_generator.py     # Generates sample data
│   ├── data_api.py                  # API for data handling
│   └── upload_processor.py          # NEW: Processes uploaded files
│
├── model_training/                  # Model training pipelines
│   ├── appearance/                  # Appearance training
│   │   ├── appearance_trainer.py    # Trains appearance models
│   │   └── image_generator.py       # NEW: Generates avatar images
│   │
│   ├── voice/                       # Voice training
│   │   ├── voice_trainer.py         # Trains voice models
│   │   └── voice_synthesizer.py     # NEW: Synthesizes speech
│   │
│   ├── communication/               # Communication training
│   │   ├── communication_trainer.py # Trains communication models
│   │   └── grok_integration.py      # NEW: Integrates with Grok API
│   │
│   └── model_training_api.py        # API for model training
│
├── action_system/                   # Action system
│   ├── action_system.py             # Core action system functionality
│   ├── action_trigger.py            # Triggers actions based on input
│   ├── idle_animation.py            # Manages idle animations
│   └── action_api.py                # API for action system
│
├── integration/                     # Integration components
│   ├── avatar_controller.py         # UPDATED: Integrates all components
│   ├── web_interface.py             # Web interface for the platform
│   │
│   ├── static/                      # Static files for web interface
│   │   ├── css/                     # CSS files
│   │   └── js/                      # JavaScript files
│   │
│   └── templates/                   # HTML templates
│
├── compute_management/              # Compute resource management
│   ├── hardware_detector.py         # Detects hardware capabilities
│   ├── cloud_computing.py           # Manages cloud computing
│   └── resource_manager.py          # Manages compute resources
│
└── testing/                         # Testing components
    ├── unit_tests/                  # Unit tests
    ├── integration_tests/           # Integration tests
    └── sample_data/                 # Sample data for testing
```

## New and Updated Files

Here's where to place the newly implemented functional components:

1. **Grok API Integration**:
   - File: `model_training/communication/grok_integration.py`
   - Purpose: Connects to Grok API for natural language processing

2. **File Upload Processing**:
   - File: `data_handling/upload_processor.py`
   - Purpose: Processes and validates uploaded files

3. **Image Generation**:
   - File: `model_training/appearance/image_generator.py`
   - Purpose: Generates avatar images using LoRA models or image datasets

4. **Voice Synthesis**:
   - File: `model_training/voice/voice_synthesizer.py`
   - Purpose: Synthesizes speech using ElevenLabs or local methods

5. **Updated Main Application**:
   - File: `main.py` (in root directory)
   - Purpose: Entry point with enhanced configuration options

6. **Updated Avatar Controller**:
   - File: `integration/avatar_controller.py`
   - Purpose: Integrates all components with support for partial functionality

## Installation Steps

1. Create the directory structure as shown above
2. Place all files in their respective directories
3. Install required dependencies:
   ```
   pip install Flask>=3.0.0 Pillow>=10.0.0 numpy>=1.26.0 scipy>=1.11.0 psutil>=5.9.0 GPUtil>=1.4.0 requests
   ```
4. Run the platform:
   ```
   python main.py
   ```

## API Keys Configuration

You can configure API keys in three ways:

1. **Command-line arguments**:
   ```
   python main.py --grok-api-key "your_grok_key" --elevenlabs-api-key "your_elevenlabs_key" --stability-api-key "your_stability_key"
   ```

2. **Configuration file** (`config.json` in root directory):
   ```json
   {
     "grok_api_key": "your_grok_key",
     "elevenlabs_api_key": "your_elevenlabs_key",
     "stability_api_key": "your_stability_key"
   }
   ```

3. **Environment variables**:
   ```
   export GROK_API_KEY="your_grok_key"
   export ELEVENLABS_API_KEY="your_elevenlabs_key"
   export STABILITY_API_KEY="your_stability_key"
   python main.py
   ```

## Module Dependencies

Each module has specific dependencies:

1. **Appearance Module**:
   - Pillow (PIL) for image processing
   - Requests for API communication

2. **Voice Module**:
   - Requests for API communication
   - (Optional) gTTS for local text-to-speech

3. **Communication Module**:
   - Requests for API communication

4. **Core Platform**:
   - Flask for web interface
   - JSON for configuration
   - Logging for diagnostics

## Troubleshooting

If you encounter issues:

1. Check that all files are in the correct directories
2. Verify that all required dependencies are installed
3. Ensure API keys are correctly configured
4. Check the logs for specific error messages
5. Make sure the platform has appropriate permissions to read/write files

For encoding issues on Windows, make sure all files are saved with UTF-8 encoding.
