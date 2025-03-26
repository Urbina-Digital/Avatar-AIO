# AI Avatar Platform - User Guide

This guide provides detailed instructions for setting up and using the AI Avatar Platform.

## Table of Contents
1. [Directory Structure](#directory-structure)
2. [Installation](#installation)
3. [Running the Platform](#running-the-platform)
4. [Using the Platform](#using-the-platform)
5. [Using Existing Models](#using-existing-models)
6. [External Training Resources](#external-training-resources)
7. [Partial Module Functionality](#partial-module-functionality)
8. [Troubleshooting](#troubleshooting)

## Directory Structure

The AI Avatar Platform uses the following directory structure:

```
ai_avatar_platform/
├── action_system/
│   ├── action_api.py
│   ├── action_system.py
│   ├── action_trigger.py
│   └── idle_animation.py
├── compute_management/
│   ├── cloud_computing.py
│   ├── hardware_detector.py
│   └── resource_manager.py
├── data_handling/
│   ├── data_api.py
│   ├── data_handler.py
│   ├── data_validator.py
│   ├── sample_data_generator.py
│   └── upload_handler.py
├── design/
│   └── mockups/
│       ├── action_control_panel.html
│       ├── chatbox_interface.html
│       ├── ui_overview.md
│       ├── upload_configuration_panel.html
│       └── visual_display_window.html
├── docs/
│   ├── architecture.md
│   ├── security_and_data_handling.md
│   └── todo.md
├── integration/
│   ├── avatar_controller.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── main.js
│   ├── templates/
│   │   └── index.html
│   └── web_interface.py
├── model_training/
│   ├── appearance/
│   │   └── appearance_trainer.py
│   ├── communication/
│   │   └── communication_trainer.py
│   ├── model_training_api.py
│   └── voice/
│       └── voice_trainer.py
├── testing/
│   ├── integration_tests/
│   │   └── test_integration.py
│   ├── sample_data/
│   │   └── sample_data_generator.py
│   └── unit_tests/
│       └── test_components.py
├── data/
│   ├── appearance/
│   ├── communication/
│   └── voice/
├── models/
│   ├── appearance/
│   ├── communication/
│   └── voice/
└── main.py
```

## Installation

### Prerequisites

The AI Avatar Platform requires the following:

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone or Download the Repository

First, download all the files and ensure they are organized according to the directory structure above.

### Step 2: Create a Virtual Environment

```bash
# Navigate to the project directory
cd ai_avatar_platform

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

Create a `requirements.txt` file in the root directory with the following content:

```
Flask==2.0.1
Pillow==8.3.1
numpy==1.21.2
scipy==1.7.1
psutil==5.8.0
GPUtil==1.4.0
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Platform

### Step 1: Verify Directory Structure

Ensure all files are in their correct locations according to the directory structure.

### Step 2: Create Required Directories

The platform requires certain directories for data storage. Run the following commands to create them:

```bash
mkdir -p data/appearance data/voice data/communication
mkdir -p models/appearance models/voice models/communication
```

### Step 3: Start the Platform

Run the main application:

```bash
python main.py
```

By default, the web interface will be available at `http://localhost:5000`.

You can specify a different port if needed:

```bash
python main.py --port 8080
```

## Using the Platform

### Step 1: Access the Web Interface

Open your web browser and navigate to `http://localhost:5000` (or the port you specified).

### Step 2: Start a Session

1. Click the "Start Session" button in the top right corner.
2. The platform will analyze your hardware capabilities and determine if local processing is possible.

### Step 3: Upload Data

#### Appearance Data
1. In the "Upload Data" section, go to the "Appearance" tab.
2. Click "Choose Files" and select either:
   - A LoRA model file (`.safetensors` format)
   - Multiple image files (at least 10 recommended)
3. Click "Upload" to process the files.

#### Voice Data
1. Go to the "Voice" tab in the "Upload Data" section.
2. Click "Choose Files" and select audio samples (10-20 samples, at least 1 minute total).
3. Click "Upload" to process the files.

#### Communication Data
1. Go to the "Communication" tab in the "Upload Data" section.
2. Click "Choose Files" and select a text file containing dialog samples.
3. Click "Upload" to process the file.

### Step 4: Interact with Your Avatar

1. Type messages in the chatbox and press "Send" or click the microphone icon for voice input.
2. Use the action buttons to trigger specific avatar actions (e.g., wave, dance, etc.).
3. Toggle "Stealth Mode" if you want text-only responses (no audio).

## Using Existing Models

If you already have trained models for appearance, voice, or communication, you can use them directly with the platform without going through the training process.

### Model File Locations

Place your existing model files in the following directories:

1. **Appearance Models**:
   - Location: `models/appearance/<user_id>/`
   - Supported formats:
     - LoRA models (`.safetensors`)
     - Stable Diffusion checkpoints (`.ckpt`)
     - Custom model format (`.bin`)
   - Required files:
     - `model.bin` or `model.safetensors` (main model file)
     - `config.json` (optional configuration file)

2. **Voice Models**:
   - Location: `models/voice/<user_id>/`
   - Supported formats:
     - Tacotron/WaveNet models (`.pth`)
     - TTS models (`.bin`)
     - Custom voice model format (`.bin`)
   - Required files:
     - `model.bin` or `model.pth` (main model file)
     - `config.json` (optional configuration file)
     - `vocoder.bin` (optional vocoder model)

3. **Communication Models**:
   - Location: `models/communication/<user_id>/`
   - Supported formats:
     - Language model checkpoints (`.bin`, `.pt`, `.pth`)
     - GGML quantized models (`.ggml.q4_*.bin`)
     - Custom language model format (`.bin`)
   - Required files:
     - `model.bin` (main model file)
     - `config.json` (optional configuration file)
     - `tokenizer.json` (optional tokenizer configuration)

### Using Custom Model Directories

If you prefer to keep your models in a different location, you can specify the models directory when starting the platform:

```bash
python main.py --models-dir /path/to/your/models
```

### Model Detection

The platform will automatically detect and use existing models when you start a session. If a model is found for a specific module (appearance, voice, or communication), the platform will use it instead of training a new one.

## External Training Resources

If you prefer to train your models using external tools before importing them into the platform, here are some recommended resources:

### Appearance Model Training

1. **Stable Diffusion LoRA Training**:
   - [Kohya SS](https://github.com/bmaltais/kohya_ss) - GUI for training LoRA models
   - [Automatic1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) with LoRA training extension
   - [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with LoRA nodes

2. **Image Dataset Preparation**:
   - [Birme](https://www.birme.net/) - Batch image resizer
   - [DreamBooth Dataset Preparation Guide](https://github.com/JoePenna/Dreambooth-Stable-Diffusion/blob/main/README.md)

3. **Pre-trained Models**:
   - [Civitai](https://civitai.com/) - Community platform for sharing Stable Diffusion models
   - [Hugging Face](https://huggingface.co/models?pipeline_tag=text-to-image) - Text-to-image models

### Voice Model Training

1. **Voice Cloning Tools**:
   - [Tortoise TTS](https://github.com/neonbjb/tortoise-tts) - High-quality voice cloning
   - [Coqui TTS](https://github.com/coqui-ai/TTS) - Text-to-speech with voice cloning capabilities
   - [Real-Time Voice Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning) - SV2TTS implementation

2. **Audio Dataset Preparation**:
   - [Audacity](https://www.audacityteam.org/) - Audio recording and editing
   - [Audio Segmentation Tool](https://github.com/audiolabs/audio-segmentation-tool) - Split long recordings

3. **Pre-trained Models**:
   - [Hugging Face](https://huggingface.co/models?pipeline_tag=text-to-speech) - Text-to-speech models
   - [ElevenLabs](https://elevenlabs.io/) - Voice cloning service (commercial)

### Communication Model Training

1. **Language Model Fine-tuning**:
   - [LM Studio](https://lmstudio.ai/) - GUI for fine-tuning language models
   - [Hugging Face Transformers](https://github.com/huggingface/transformers) - Fine-tuning scripts
   - [LoRA for LLMs](https://github.com/microsoft/LoRA) - Efficient fine-tuning

2. **Text Dataset Preparation**:
   - [Alpaca Dataset Format](https://github.com/tatsu-lab/stanford_alpaca#data-release) - Standard format for instruction tuning
   - [OpenAI Fine-tuning Format](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset) - JSON format for conversations

3. **Pre-trained Models**:
   - [Hugging Face](https://huggingface.co/models?pipeline_tag=text-generation) - Language models
   - [TheBloke's Quantized Models](https://huggingface.co/TheBloke) - Optimized models for local use

## Partial Module Functionality

The AI Avatar Platform is designed to function even when some modules are missing or not fully operational. This graceful degradation ensures you can still use the available features.

### Appearance-Only Mode

If only the appearance module is available:
- The avatar can display visuals and perform actions
- No voice or intelligent responses will be available
- Pre-defined text responses will be used
- Actions can be triggered manually through the action buttons

To use appearance-only mode:
1. Place your appearance model in `models/appearance/<user_id>/`
2. Start the platform and create a session
3. Use the action buttons to control the avatar

### Voice-Only Mode

If only the voice module is available:
- The avatar can speak using the trained voice
- A default appearance will be used (or none at all)
- Pre-defined text responses will be used for communication
- Text-to-speech will work for any input text

To use voice-only mode:
1. Place your voice model in `models/voice/<user_id>/`
2. Start the platform and create a session
3. Type text in the chatbox to hear it spoken in the trained voice

### Communication-Only Mode

If only the communication module is available:
- The avatar can generate intelligent text responses
- No voice or visual appearance will be available
- The platform will function similar to a text-based chatbot

To use communication-only mode:
1. Place your communication model in `models/communication/<user_id>/`
2. Start the platform and create a session
3. Interact with the avatar through text in the chatbox

### Mixed Partial Modes

The platform supports any combination of available modules:
- Appearance + Voice: Visual avatar with speech but pre-defined responses
- Appearance + Communication: Visual avatar with intelligent responses but no voice
- Voice + Communication: Intelligent spoken responses but no visual avatar

### Enabling Partial Mode

Partial mode is automatically enabled when the platform detects that some modules are missing. You can also explicitly enable it:

```bash
python main.py --allow-partial-modules
```

## Troubleshooting

### Import Errors

If you encounter import errors, verify that:

1. All files are in the correct locations according to the directory structure.
2. You're running the platform from the root directory (`ai_avatar_platform/`).

### Module Not Found Errors

For any "Module not found" errors, ensure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

### Hardware Detection Issues

If the platform cannot detect your hardware properly:

1. Ensure you have the latest version of `psutil` and `GPUtil`.
2. Try running with the `--force-local` flag to use local processing regardless of hardware detection:

```bash
python main.py --force-local
```

Or use the `--force-cloud` flag to use cloud processing:

```bash
python main.py --force-cloud
```

### Web Interface Not Loading

If the web interface doesn't load:

1. Check that Flask is running correctly (look for messages in the terminal).
2. Verify that no other application is using the same port.
3. Try a different port:

```bash
python main.py --port 8080
```

### Model Loading Errors

If you're having trouble with existing models:

1. Check that the model files are in the correct location and have the expected names.
2. Verify that the model format is supported by the platform.
3. Check the logs for specific error messages about model loading.
4. Try running with the `--debug` flag for more detailed logging:

```bash
python main.py --debug
```

## Additional Notes

- This is a prototype version of the AI Avatar Platform.
- For demonstration purposes, the platform simulates model training and inference.
- In a production environment, you would need to implement actual model training using frameworks like TensorFlow or PyTorch.
- The cloud computing functionality is simulated and would need to be connected to actual cloud services in a production environment.
