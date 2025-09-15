#!/usr/bin/env python3
"""
Cache Management Web Panel
Run this script to start the Flask web application
"""

import os
import sys

def main():
    print("🚀 Starting Cache Management Web Panel...")
    print("📱 Make sure your Android device is connected via ADB")
    print("🌐 The web interface will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Not running in a virtual environment")
    
    # Start the Flask application
    from app import app, socketio
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
