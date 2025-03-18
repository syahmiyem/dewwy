#!/bin/bash
# Install dependencies for Dewwy on macOS

echo "Installing required system dependencies..."
brew install portaudio

# For better compatibility with ARM Macs (M1/M2/M3)
brew install libsndfile

echo "Installing swig for pocketsphinx..."
brew install swig

echo "Done installing system dependencies!"
