#!/usr/bin/env python3
"""
Debug utility to print information about the Python environment and modules
This can help diagnose issues with imports and dependencies
"""

import sys
import os
import importlib
import platform
import pkgutil

def check_module(module_name):
    """Check if a module can be imported and show its version"""
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, '__version__', 'unknown')
        return f"✅ {module_name} (version: {version})"
    except ImportError:
        return f"❌ {module_name} (not found)"
    except Exception as e:
        return f"⚠️ {module_name} (error: {str(e)})"

def print_system_info():
    """Print system and Python information"""
    print("\n=== System Information ===")
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Path: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")

def print_path_info():
    """Print Python path information"""
    print("\n=== Python Path ===")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")

def check_key_modules():
    """Check important modules for the application"""
    print("\n=== Key Modules ===")
    modules = [
        "flask", "flask_socketio", "socketio", "eventlet", "gevent",
        "werkzeug", "jinja2", "arcade", "PIL", "numpy",
        "websocket", "engineio"
    ]
    for module in modules:
        print(check_module(module))

def check_project_structure():
    """Check if key project files exist"""
    print("\n=== Project Structure ===")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_files = [
        "web/app.py",
        "web/wsgi.py", 
        "web/templates/simulator.html",
        "web/static/js/simulator.js",
        "simulation/arcade_simulator.py"
    ]
    for file_path in key_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (not found)")

def main():
    """Main function to run all checks"""
    print("DEWWY DEBUG INFORMATION")
    print("======================")
    
    print_system_info()
    print_path_info()
    check_key_modules()
    check_project_structure()
    
    print("\nDebug info complete")

if __name__ == "__main__":
    main()
