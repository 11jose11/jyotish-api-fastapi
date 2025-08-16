#!/usr/bin/env python3
"""Quick start script for Jyotiṣa API development."""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the Jyotiṣa API server."""
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your configuration:")
        print("cp env.example .env")
        print("Then edit .env with your Google Maps API key and other settings.")
        print()
    
    # Set default port
    port = int(os.getenv("PORT", 8080))
    
    print("🚀 Starting Jyotiṣa API...")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health/healthz")
    print()
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
