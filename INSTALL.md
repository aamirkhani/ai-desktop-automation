# Installation Guide

## Prerequisites

### System Requirements
- Ubuntu 20.04+ or compatible Linux distribution
- Python 3.8+
- Wayland or X11 desktop environment

### System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Add user to input group (required for UInput)
sudo usermod -a -G input $USER

# Reboot to apply group changes
sudo reboot
```

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-desktop-automation
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
# Or add to ~/.bashrc for persistence
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 5. Verify Installation
```bash
python3 -c "import evdev, uinput, pyautogui, openai; print('All dependencies installed successfully')"
```

## Quick Test

```bash
# Run basic test
python3 desktop_automator_verbose.py
```

## Troubleshooting

### Permission Issues
```bash
# Check if user is in input group
groups $USER

# If not in input group, add and reboot
sudo usermod -a -G input $USER
sudo reboot
```

### UInput Module Issues
```bash
# Install uinput module
sudo apt install python3-uinput -y

# Load uinput kernel module
sudo modprobe uinput

# Make permanent
echo 'uinput' | sudo tee -a /etc/modules
```

### API Key Issues
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
python3 -c "from openai import OpenAI; client = OpenAI(); print('API key valid')"
```
