import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Import the Flask app and SocketIO
from web.app import app, socketio

# PythonAnywhere uses WSGI - we need to provide the application
application = socketio.wsgi_app

if __name__ == '__main__':
    application.run()
