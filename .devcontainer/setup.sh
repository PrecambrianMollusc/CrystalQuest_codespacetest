#!/bin/bash
set -e

echo "🔧 Updating system packages..."
sudo apt-get update

echo "📦 Installing Mesa and EGL libraries..."
sudo apt-get install -y libosmesa6-dev
sudo apt-get install -y libegl1-mesa-dev libgles2-mesa-dev

echo "🐍 Upgrading pip and installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r /workspaces/EliteDangrous_IGAU_CrystalQuest/requirements.txt

echo "✅ Setup complete!"