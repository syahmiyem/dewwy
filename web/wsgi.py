import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Import the Flask app
from web.app import app as application

# PythonAnywhere looks for 'application' in this file
if __name__ == '__main__':
    application.run()
