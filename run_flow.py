#!/usr/bin/env python
"""
Runner script for CrewAI flows.
Run flows from the project root with proper Python path setup.

Usage:
    python run_flow.py <flow_name> [command]
    
Examples:
    python run_flow.py poem_flow
    python run_flow.py poem_flow kickoff
    python run_flow.py poem_flow plot
"""

import sys
import os
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
    if len(sys.argv) < 2:
        print("Usage: python run_flow.py <flow_name> [command]")
        print("\nAvailable flows:")
        flows_dir = src_path / "flows"
        if flows_dir.exists():
            for flow_dir in flows_dir.iterdir():
                if flow_dir.is_dir() and not flow_dir.name.startswith("_"):
                    print(f"  - {flow_dir.name}")
        sys.exit(1)
    
    flow_name = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "kickoff"
    
    # Import and run the flow
    try:
        flow_module = __import__(f"flows.{flow_name}.main", fromlist=[""])
        
        if hasattr(flow_module, command):
            func = getattr(flow_module, command)
            func()
        else:
            print(f"Error: Command '{command}' not found in {flow_name}")
            print(f"Available commands: {[name for name in dir(flow_module) if not name.startswith('_') and callable(getattr(flow_module, name))]}")
            sys.exit(1)
            
    except ModuleNotFoundError as e:
        print(f"Error: Flow '{flow_name}' not found")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running flow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
