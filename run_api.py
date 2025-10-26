#!/usr/bin/env python
"""
API server runner for CrewAI flows.
Starts the FastAPI server with proper Python path setup and environment loading.

Usage:
    python run_api.py [--host HOST] [--port PORT] [--reload]
    
Examples:
    python run_api.py
    python run_api.py --host 0.0.0.0 --port 8000
    python run_api.py --reload  # Enable auto-reload for development
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
env_file = project_root / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✓ Loaded environment variables from {env_file}")
    except ImportError:
        print("⚠ Warning: python-dotenv not installed. Run: pip install python-dotenv")
        print("   .env file will not be loaded automatically.")
else:
    print(f"⚠ Warning: .env file not found at {env_file}")


def main():
    """Run the FastAPI server."""
    parser = argparse.ArgumentParser(description="Run the CrewAI Flow API server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    try:
        import uvicorn
    except ImportError:
        print("❌ Error: uvicorn is not installed.")
        print("   Install it with: pip install uvicorn")
        sys.exit(1)
    
    print(f"\n🚀 Starting CrewAI Flow API server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print(f"\n📖 API Documentation will be available at:")
    print(f"   http://{args.host}:{args.port}/docs")
    print(f"   http://{args.host}:{args.port}/redoc")
    print()
    
    # Run the server
    uvicorn.run(
        "api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
