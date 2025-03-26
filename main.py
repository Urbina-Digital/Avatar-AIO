import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main_app')

def create_directories(base_dir):
    """Create necessary directories for the platform."""
    # Data directories
    data_dirs = [
        os.path.join(base_dir, 'data', 'appearance'),
        os.path.join(base_dir, 'data', 'voice'),
        os.path.join(base_dir, 'data', 'communication')
    ]
    
    # Models directories
    model_dirs = [
        os.path.join(base_dir, 'models', 'appearance'),
        os.path.join(base_dir, 'models', 'voice'),
        os.path.join(base_dir, 'models', 'communication')
    ]
    
    # Static and template directories
    web_dirs = [
        os.path.join(base_dir, 'integration', 'static', 'css'),
        os.path.join(base_dir, 'integration', 'static', 'js'),
        os.path.join(base_dir, 'integration', 'templates')
    ]
    
    # Create all directories
    for directory in data_dirs + model_dirs + web_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")

def load_config(base_dir):
    """Load configuration from config.json if it exists."""
    config_path = os.path.join(base_dir, 'config.json')
    config = {
        "port": 5000,
        "host": "0.0.0.0",
        "debug": False,
        "user_id": "default",
        "grok_api_key": "grok_api_key",
        "elevenlabs_api_key": "elevenlabs_api_key",
        "stability_api_key": "stability_api_key",
        "force_local": False,
        "force_cloud": False
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    return config

def save_config(base_dir, config):
    """Save configuration to config.json."""
    config_path = os.path.join(base_dir, 'config.json')
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

def main():
    """Main entry point for the AI Avatar Platform."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='AI Avatar Platform')
    parser.add_argument('--port', type=int, help='Port to run the web server on')
    parser.add_argument('--host', type=str, help='Host to run the web server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--user-id', type=str, help='User ID for the avatar')
    parser.add_argument('--grok-api-key', type=str, help='API key for Grok')
    parser.add_argument('--elevenlabs-api-key', type=str, help='API key for ElevenLabs')
    parser.add_argument('--stability-api-key', type=str, help='API key for Stability AI')
    parser.add_argument('--force-local', action='store_true', help='Force local processing')
    parser.add_argument('--force-cloud', action='store_true', help='Force cloud processing')
    parser.add_argument('--gpt-sovits-path', type=str, help='Path to GPT-SoVITS installation')
    args = parser.parse_args()
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create necessary directories
    create_directories(base_dir)
    
    # Load configuration
    config = load_config(base_dir)
    
    # Update configuration with command-line arguments
    if args.port:
        config['port'] = args.port
    if args.host:
        config['host'] = args.host
    if args.debug:
        config['debug'] = args.debug
    if args.user_id:
        config['user_id'] = args.user_id
    if args.grok_api_key:
        config['grok_api_key'] = args.grok_api_key
    if args.elevenlabs_api_key:
        config['elevenlabs_api_key'] = args.elevenlabs_api_key
    if args.stability_api_key:
        config['stability_api_key'] = args.stability_api_key
    if args.force_local:
        config['force_local'] = True
    if args.force_cloud:
        config['force_cloud'] = True
    
    # Save updated configuration
    save_config(base_dir, config)
    
    # Start the platform
    logger.info("Starting AI Avatar Platform")
    logger.info(f"Base directory: {base_dir}")
    logger.info(f"Data directory: {os.path.join(base_dir, 'data')}")
    logger.info(f"Models directory: {os.path.join(base_dir, 'models')}")
    
    # Import components
    try:
        # Add the base directory to the Python path
        sys.path.insert(0, base_dir)
        
        # Import the avatar controller
        from integration.avatar_controller import AvatarController
        
        # Import the web interface
        from integration.web_interface import WebInterface
        
        # Create avatar controller
        avatar_controller = AvatarController(
            base_dir=base_dir,
            user_id=config['user_id'],
            grok_api_key=config['grok_api_key'],
            elevenlabs_api_key=config['elevenlabs_api_key'],
            stability_api_key=config['stability_api_key'],
            force_local=config['force_local'],
            force_cloud=config['force_cloud']
        )
        
        # Create web interface
        web_interface = WebInterface(
            avatar_controller=avatar_controller,
            base_dir=base_dir,
            port=config['port'],
            host=config['host'],
            debug=config['debug']
        )
        
        # Start web server
        logger.info(f"Starting web server on port {config['port']}")
        web_interface.run()
    
    except ImportError as e:
        logger.error(f"Error importing components: {e}")
        logger.error("Make sure all required modules are installed")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error starting platform: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
