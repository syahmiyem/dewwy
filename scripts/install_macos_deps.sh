#!/bin/bash
# Install dependencies for Dewwy on macOS

echo "Installing required system dependencies..."
brew install portaudio

# For better compatibility with ARM Macs (M1/M2/M3)
brew install libsndfile

echo "Installing swig for pocketsphinx..."
brew install swig

# Pre-built versions instead of compiling from source
echo "Installing Python packages using pre-built wheels..."
pip install --prefer-binary pyaudio==0.2.11
pip install --prefer-binary numpy==1.21.6 
pip install --prefer-binary sounddevice==0.4.1
pip install --prefer-binary pyttsx3==2.9.0
pip install --prefer-binary webrtcvad==2.0.10

# Try installing pocketsphinx, but don't fail if it doesn't work
echo "Attempting to install pocketsphinx (optional)..."
pip install --prefer-binary pocketsphinx==0.1.15 || echo "Pocketsphinx installation skipped - will use fallback mode"

echo "Done installing system dependencies!"
