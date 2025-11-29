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
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 The web interface will be available at: http://localhost:{port}")
    
    # Check if running in production mode
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    if not debug_mode:
        print("🔒 Running in production mode")
    else:
        print("⏹️  Press Ctrl+C to stop the server")
    
    print("-" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Not running in a virtual environment")
    
    # Start the Flask application
    from app import app, socketio
    
    # For production mode, allow unsafe werkzeug (required by Flask-SocketIO)
    # Note: For true production, consider using gunicorn with gevent workers
    if not debug_mode:
        socketio.run(app, debug=False, host='0.0.0.0', port=port, 
                    allow_unsafe_werkzeug=True)
    else:
        # Development mode - use Werkzeug with debug
        socketio.run(app, debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
