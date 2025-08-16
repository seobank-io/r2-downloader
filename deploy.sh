#!/bin/bash

# R2 Download Solution - Quick Deployment Script
# This script sets up both the React frontend and Flask backend

echo "🚀 R2 Download Solution - Quick Setup"
echo "======================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Flask Backend
echo ""
echo "🐍 Setting up Flask Backend..."
cd r2-download-proxy

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install flask requests flask-cors

echo "✅ Flask backend setup complete"

# Setup React Frontend
echo ""
echo "⚛️  Setting up React Frontend..."
cd ../download-manager

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ React frontend setup complete"

# Create start scripts
echo ""
echo "📝 Creating start scripts..."

# Backend start script
cat > ../start-backend.sh << 'BACKEND_EOF'
#!/bin/bash
echo "🐍 Starting Flask Backend..."
cd r2-download-proxy
source venv/bin/activate
python src/main.py
BACKEND_EOF

# Frontend start script
cat > ../start-frontend.sh << 'FRONTEND_EOF'
#!/bin/bash
echo "⚛️  Starting React Frontend..."
cd download-manager
npm run dev --host
FRONTEND_EOF

# Make scripts executable
chmod +x ../start-backend.sh
chmod +x ../start-frontend.sh

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "To start the application:"
echo "1. Start Backend:  ./start-backend.sh"
echo "2. Start Frontend: ./start-frontend.sh"
echo "3. Open browser:   http://localhost:5173"
echo ""
echo "Test with your R2 URL:"
echo "https://pub-7f048232a615464dbd35c541bea50ced.r2.dev/Aetheric.zip"
echo ""
echo "📚 See README.md for detailed usage instructions"
