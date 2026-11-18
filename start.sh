#!/bin/bash
# ============================================================
# Personal AI Agent System — Launcher
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   🤖 Personal AI Agent System — Starting     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
  echo "⚠️  No .env file found. Creating from template..."
  cp .env.example .env
  echo "   → Edit .env and add your OPENAI_API_KEY"
  echo ""
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q -r requirements.txt

echo ""
echo "🚀 Starting Backend API Server on http://localhost:8765 ..."
echo "   Press Ctrl+C to stop the server"
echo ""

# Start Flask Backend
python3 app.py
