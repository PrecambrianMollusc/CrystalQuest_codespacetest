echo "🚀 SETUP.SH IS RUNNING!"

echo "📂 Running setup from: $(pwd)"

#!/bin/bash
set -e

echo "📂 Running setup from: $(pwd)"
echo "📄 Listing root contents:"
ls -la

echo "🔧 Updating system packages..."
sudo apt-get update
sudo apt-get install -y libosmesa6-dev libegl1-mesa-dev libgles2-mesa-dev

echo "🐍 Installing Python dependencies from root-level requirements.txt..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "✅ Setup complete!"
