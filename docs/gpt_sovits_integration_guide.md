# Integrating GPT-SoVITS Voice Models with AI Avatar Platform

This guide explains how to integrate your trained GPT-SoVITS voice models into the AI Avatar Platform.

## Overview

GPT-SoVITS is a powerful voice synthesis system that combines GPT and SoVITS models to create high-quality, natural-sounding speech. The AI Avatar Platform now includes a dedicated integration module that makes it easy to use your trained GPT-SoVITS models for avatar voice synthesis.

## Prerequisites

1. Trained GPT-SoVITS model files:
   - GPT checkpoint file (e.g., `G_5.pth` or `G_10.pth`)
   - SoVITS checkpoint file (e.g., `sovits_4.pth` or `sovits_8.pth`)
   - Config file (optional, but recommended)

2. GPT-SoVITS installation (either the web UI or command-line version)

## Integration Steps

### 1. Install the Integration Module

The GPT-SoVITS integration module is now included in the AI Avatar Platform. Make sure you place the file in the correct location:

```
ai_avatar_platform/model_training/voice/gpt_sovits_integration.py
```

### 2. Import Your Trained Model

You can import your trained GPT-SoVITS model using the following code:

```python
from model_training.voice.gpt_sovits_integration import GPTSoVITSIntegration

# Initialize the integration module
gpt_sovits = GPTSoVITSIntegration(
    base_dir="/path/to/ai_avatar_platform",
    gpt_sovits_path="/path/to/GPT-SoVITS"  # Path to your GPT-SoVITS installation
)

# Import your trained model
result = gpt_sovits.import_model(
    user_id="your_user_id",
    gpt_checkpoint_path="/path/to/G_10.pth",  # Your GPT checkpoint
    sovits_checkpoint_path="/path/to/sovits_8.pth",  # Your SoVITS checkpoint
    config_path="/path/to/config.json",  # Optional
    model_name="My Voice Model"  # Optional
)

print(result["message"])
```

### 3. Update the Avatar Controller

To use your GPT-SoVITS model for voice synthesis, you need to update the avatar controller. Add the following code to `integration/avatar_controller.py`:

```python
# In the _load_components method
try:
    # Try to import GPT-SoVITS integration
    from model_training.voice.gpt_sovits_integration import GPTSoVITSIntegration
    self.gpt_sovits_module = GPTSoVITSIntegration(
        base_dir=self.base_dir,
        gpt_sovits_path="/path/to/GPT-SoVITS"  # Update with your path
    )
    self.component_status["gpt_sovits"] = True
except ImportError as e:
    logger.warning(f"Could not import GPT-SoVITS module: {e}")
```

Then modify the `process_input` method to use GPT-SoVITS for voice synthesis:

```python
# In the process_input method, replace or add to the voice synthesis section
if self.component_status["gpt_sovits"] and self.gpt_sovits_module:
    audio_path = self.gpt_sovits_module.synthesize_speech(
        self.user_id, 
        response["text"]
    )
    if audio_path:
        response["audio"] = str(audio_path)
elif self.component_status["voice"] and self.voice_module:
    # Fallback to regular voice synthesis
    audio_path = self.voice_module.synthesize_speech(self.user_id, response["text"])
    if audio_path:
        response["audio"] = str(audio_path)
```

### 4. Configure via Command Line

You can also configure the GPT-SoVITS path via command line when starting the platform:

```bash
python main.py --gpt-sovits-path "/path/to/GPT-SoVITS"
```

To do this, add the following to the argument parser in `main.py`:

```python
parser.add_argument('--gpt-sovits-path', type=str, help='Path to GPT-SoVITS installation')
```

And update the configuration handling:

```python
if args.gpt_sovits_path:
    config['gpt_sovits_path'] = args.gpt_sovits_path
```

## Using Reference Audio (Zero-shot Voice Cloning)

GPT-SoVITS supports zero-shot voice cloning using reference audio. To use this feature:

```python
audio_path = gpt_sovits.synthesize_speech(
    user_id="your_user_id",
    text="Text to synthesize",
    reference_audio="/path/to/reference.wav",
    prompt_text="Text of the reference audio",
    prompt_language="en",
    text_language="en"
)
```

## Troubleshooting

### Model Not Found

If you get a "Model not found" error, check that:
- You've imported the model correctly
- The user_id matches between import and synthesis
- The model files are in the correct location

### Synthesis Fails

If speech synthesis fails:
- Check that the GPT-SoVITS path is set correctly
- Ensure GPT-SoVITS is installed and working
- Try running inference directly with GPT-SoVITS to verify it works

### Web UI vs. Command Line

The integration module supports both the web UI and command-line versions of GPT-SoVITS:
- Web UI: Make sure the web UI is running on port 7860
- Command Line: Make sure the inference.py script is available

## Directory Structure

After importing your model, the files will be organized as follows:

```
ai_avatar_platform/
├── models/
│   └── voice/
│       └── your_user_id/
│           └── gpt_sovits/
│               ├── G_10.pth  # Your GPT checkpoint
│               ├── sovits_8.pth  # Your SoVITS checkpoint
│               ├── config.json  # Optional config file
│               ├── model_info.json  # Generated model info
│               └── gpt_sovits_model.flag  # Flag file
├── data/
│   └── voice/
│       └── your_user_id/
│           └── generated/
│               └── gpt_sovits_*.wav  # Generated audio files
```

## Advanced Configuration

For advanced users, you can modify the synthesis parameters in the `synthesize_speech` method:

```python
audio_path = gpt_sovits.synthesize_speech(
    user_id="your_user_id",
    text="Text to synthesize",
    output_path="/custom/output/path.wav",  # Custom output path
    reference_audio="/path/to/reference.wav",
    prompt_text="Text of the reference audio",
    prompt_language="en",
    text_language="en"
)
```

You can also list all available models:

```python
models = gpt_sovits.list_available_models()
for model in models:
    print(f"Model: {model['model_name']}")
```

## Conclusion

With this integration, you can now use your trained GPT-SoVITS voice models directly in the AI Avatar Platform. The platform will automatically use your custom voice for all avatar speech synthesis, creating a more personalized and natural-sounding experience.
