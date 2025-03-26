#!/usr/bin/env python3
"""
Setup Script for AI Avatar Platform

This script installs all required dependencies and verifies the environment.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def check_python_version():
    """Check if Python version is compatible."""
    print_header("Checking Python Version")
    
    major, minor, _ = platform.python_version_tuple()
    print(f"Detected Python {major}.{minor}")
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {platform.python_version()}")
        return False
    
    print("Python version check passed.")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    print_header("Setting Up Virtual Environment")
    
    venv_dir = Path("venv")
    
    if venv_dir.exists():
        print("Virtual environment already exists.")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print_header("Installing Dependencies")
    
    # Create requirements.txt if it doesn't exist
    requirements_path = Path("requirements.txt")
    
    if not requirements_path.exists():
        print("Creating requirements.txt file...")
        with open(requirements_path, "w") as f:
            f.write("""Flask==2.0.1
Pillow==8.3.1
numpy==1.21.2
scipy==1.7.1
psutil==5.8.0
GPUtil==1.4.0
""")
        print("requirements.txt created.")
    
    # Determine pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = [os.path.join("venv", "Scripts", "pip")]
    else:
        pip_cmd = [os.path.join("venv", "bin", "pip")]
    
    # Install dependencies
    try:
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def verify_directory_structure():
    """Verify and create the required directory structure."""
    print_header("Verifying Directory Structure")
    
    # Define required directories
    required_dirs = [
        "action_system",
        "compute_management",
        "data_handling",
        "design/mockups",
        "docs",
        "integration/static/css",
        "integration/static/js",
        "integration/templates",
        "model_training/appearance",
        "model_training/voice",
        "model_training/communication",
        "testing/integration_tests",
        "testing/sample_data",
        "testing/unit_tests",
        "data/appearance",
        "data/voice",
        "data/communication",
        "models/appearance",
        "models/voice",
        "models/communication"
    ]
    
    # Create directories if they don't exist
    for directory in required_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    print("Directory structure verified and created if needed.")
    return True

def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete")
    
    print("The AI Avatar Platform has been set up successfully!")
    print("\nNext Steps:")
    
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        python_cmd = "python"
    else:
        activate_cmd = "source venv/bin/activate"
        python_cmd = "python3"
    
    print(f"1. Activate the virtual environment:")
    print(f"   {activate_cmd}")
    print(f"2. Run the platform:")
    print(f"   {python_cmd} main.py")
    print(f"3. Open your browser and navigate to:")
    print(f"   http://localhost:5000")
    print("\nFor more detailed instructions, see docs/how_to_use.md")

def main():
    """Main function to set up the AI Avatar Platform."""
    print_header("AI Avatar Platform Setup")
    
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run setup steps
    if not check_python_version():
        return 1
    
    if not create_virtual_environment():
        return 1
    
    if not install_dependencies():
        return 1
    
    if not verify_directory_structure():
        return 1
    
    print_next_steps()
    return 0

if __name__ == "__main__":
    sys.exit(main())
