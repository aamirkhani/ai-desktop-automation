# Contributing to AI Desktop Automation

## Development Setup

### Prerequisites
- Ubuntu 20.04+ or compatible Linux distribution
- Python 3.8+
- Git configured with Gerrit

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd ai-desktop-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Add user to input group
sudo usermod -a -G input $USER
sudo reboot
```

## Code Style

### Python Code Standards
- Follow PEP 8 style guide
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Formatting
```bash
# Format code
black *.py

# Check style
flake8 *.py

# Type checking
mypy *.py
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test
python test_uinput_controller.py
```

### Adding Tests
- Add tests for new features
- Ensure existing tests pass
- Test on both Wayland and X11

## Submitting Changes

### Commit Guidelines
- Use conventional commit format
- Include clear description
- Reference issue numbers if applicable

### Example Commit Messages
```
feat: add support for custom key mappings
fix: resolve special character typing issue
docs: update installation instructions
test: add unit tests for UInput controller
```

### Gerrit Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: your feature description"

# Push to Gerrit for review
git push origin HEAD:refs/for/main
```

## Security Guidelines

### API Key Management
- Never commit API keys to repository
- Use environment variables for sensitive data
- Add API key files to .gitignore

### Input Security
- Validate all user inputs
- Sanitize file paths
- Use secure defaults

## Documentation

### Code Documentation
- Add docstrings to all functions
- Include parameter and return type information
- Provide usage examples

### README Updates
- Update README.md for new features
- Include installation steps
- Add troubleshooting information

## Issue Reporting

### Bug Reports
Include:
- Operating system and version
- Python version
- Desktop environment (Wayland/X11)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

### Feature Requests
Include:
- Use case description
- Proposed implementation approach
- Potential impact on existing functionality
