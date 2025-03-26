   ╔──────────────────────╗
   ╣        AI AVATAR        ╣
   ╣             AIO             ╣
   ╣        PLATFORM         ╣
   ╣          2025           ╣
   ╚──────────────────────╝
               by Urbina Digital

# AI Avatar Platform (Avatar_AIO)

## Overview

The **AI Avatar Platform (Avatar_AIO)** is an all-in-one system designed to create personalized, interactive AI avatars. Users can customize their avatar’s appearance, voice, and communication style using local or cloud-based processing. This project delivers a modular, extensible platform for avatar creation and real-time interaction, emphasizing privacy, flexibility, and user control.

### Goals
- Build avatars with unique visuals, synthesized voices, and natural language responses.
- Support local processing for privacy, with optional cloud integration for scalability.
- Offer a modular architecture that functions even with partial components (e.g., appearance-only or voice-only modes).
- Act as a prototype for future expansion into a production-ready system.

### Current Status
This is a **prototype** version. Core functionality is implemented with simulated model training and inference. Actual training requires external tools (e.g., Stable Diffusion, Tacotron), and cloud features are conceptual. The platform supports:
- File uploads for appearance, voice, and communication data.
- Web-based UI for interaction.
- Partial module operation (e.g., using pre-trained models).
- Local resource detection and basic action triggers.

## Features

- **Modular Design**: Separate modules for appearance, voice, and communication, with graceful degradation if components are missing.
- **User Interface**: Responsive web interface with visual display, chatbox, upload panel, and action controls.
- **Data Handling**: Secure local storage of user data, with optional cloud processing.
- **Customization**: Supports LoRA models, audio samples, and text dialogs for personalization.
- **Actions**: Predefined avatar animations (e.g., wave, dance) triggered via UI.

## Directory Structure

    ai_avatar_platform/
    ├── main.py                   # Entry point
    ├── data/                     # User data
    │   ├── appearance/           # Appearance data
    │   ├── voice/                # Voice data
    │   └── communication/        # Communication data
    ├── models/                   # Trained models
    │   ├── appearance/           # Appearance models
    │   ├── voice/                # Voice models
    │   └── communication/        # Communication models
    ├── data_handling/            # Upload and preprocessing logic
    ├── model_training/           # Training pipelines (simulated)
    ├── action_system/            # Avatar actions and triggers
    ├── integration/              # Web UI and controller
    ├── compute_management/       # Resource detection
    ├── docs/                     # Documentation
    └── testing/                  # Tests

See [directory_structure.md](docs/directory_structure.md) for details.

## Installation

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (recommended)

### Steps
1. **Clone the Repository**:

        git clone https://github.com/Urbina-Digital/Avatar_AIO.git
        cd Avatar_AIO

2. **Set Up Virtual Environment**:

        python -m venv venv
        # Windows:
        venv\Scripts\activate
        # macOS/Linux:
        source venv/bin/activate

3. **Install Dependencies**:

        pip install Flask>=3.0.0 Pillow>=10.0.0 numpy>=1.26.0 scipy>=1.11.0 psutil>=5.9.0 GPUtil>=1.4.0 requests

4. **Create Data/Model Directories**:

        mkdir -p data/appearance data/voice data/communication
        mkdir -p models/appearance models/voice models/communication

## Running the Platform

1. **Start the Application**:

        python main.py

   - Access the web interface at `http://localhost:5000`.
   - Optional: Use `--port 8080` for a different port.

2. **Configuration** (optional):
   - Via command line:

        python main.py --grok-api-key "your_key" --elevenlabs-api-key "your_key"

   - Via `config.json` in the root:

        {
          "grok_api_key": "your_key",
          "elevenlabs_api_key": "your_key"
        }

## Security and Data Handling

- **Local Storage**: User data (images, audio, text) is stored locally under `data/` by default, organized by user ID.
- **Privacy**: No data is shared between users; optional cloud processing uses HTTPS with TLS/SSL.
- **Control**: Users can delete their data anytime; temporary files are auto-cleaned.
- **Security**: Input validation, secure file uploads, and minimal dependencies reduce risks.

See [security_and_data_handling.md](docs/security_and_data_handling.md) for more.

## Current Functionality

### Avatar Creation
- **Appearance**: Upload LoRA models (`.safetensors`) or image datasets; generates visuals (simulated).
- **Voice**: Upload audio samples (10-20, ~1 min total); synthesizes speech (simulated).
- **Communication**: Upload text dialogs; generates responses via Grok API (requires key).

### Interaction
- **Chatbox**: Text or audio input with avatar responses (text-only in stealth mode).
- **Actions**: Trigger animations (e.g., jump, wave) via the action panel.
- **Partial Modes**: Use only available modules (e.g., appearance-only with static visuals).

### Limitations
- Model training is simulated; use external tools for actual training (see [User Guide](#external-training-resources)).
- Cloud features are placeholders; local processing is prioritized.
- UI is basic but functional.

## Using the Platform

### Quick Start
1. Run `python main.py`.
2. Open `http://localhost:5000` in your browser.
3. Upload data via the "Upload & Configuration" panel.
4. Interact via the chatbox or action buttons.

### Using Pre-trained Models
Place models in:
- `models/appearance/<user_id>/` (e.g., `model.safetensors`)
- `models/voice/<user_id>/` (e.g., `model.bin`)
- `models/communication/<user_id>/` (e.g., `model.bin`)
Start the platform, and it will detect them automatically.

### External Training Resources
- **Appearance**: [Kohya SS](https://github.com/bmaltais/kohya_ss), [Civitai](https://civitai.com/)
- **Voice**: [Tortoise TTS](https://github.com/neonbjb/tortoise-tts), [ElevenLabs](https://elevenlabs.io/)
- **Communication**: [LM Studio](https://lmstudio.ai/), [Hugging Face](https://huggingface.co/)

See [user_guide.md](docs/user_guide.md) for details.

## UI Overview

- **Visual Display**: 2D/3D avatar view with zoom and rotation.
- **Chatbox**: Text/audio input with history and stealth mode.
- **Upload Panel**: Drag-and-drop for datasets and settings.
- **Action Panel**: Buttons for expressions, movements, and interactions.

Responsive design adapts to desktop, tablet, and mobile. See [ui_design.md](docs/ui_design.md) for mockups.

## Contributing

This is an open prototype—feel free to fork, experiment, and submit PRs! Focus areas:
- Real model training integration.
- Cloud computing implementation.
- UI enhancements.

## Troubleshooting

- **Import Errors**: Check file placement and run from the root directory.
- **Web Issues**: Ensure Flask is running; try a different port (`--port 8080`).
- **Debugging**: Use `--debug` for detailed logs.

See [user_guide.md](docs/user_guide.md#troubleshooting) for more.

## License

CC0-1.0 - Public Domain. Use it however you like!

---

Built by Urbina Digital, 2025.