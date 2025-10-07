#!/bin/bash
set -e

echo "🚀 SETUP.SH IS RUNNING!"
echo "📂 Running setup from: $(pwd)"

# Optional: verify requirements.txt exists
if [ ! -f requirements.txt ]; then
  echo "❌ ERROR: requirements.txt not found!"
  exit 1
fi

# Install system packages
sudo apt-get update
sudo apt-get install -y libosmesa6-dev libegl1-mesa-dev libgles2-mesa-dev

# Install Python packages
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "✅ Setup complete!"

