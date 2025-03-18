import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Import the Flask app and SocketIO
from web.app import app, socketio

# Create a WSGI application wrapper
# Different versions of Flask-SocketIO use different attribute names
try:
    application = socketio.wsgi_app
except AttributeError:
    try:
        # Fall back to alternative attribute names that might exist
        application = socketio.app
    except AttributeError:
        # Last resort - use the Flask app directly
        application = app

if __name__ == '__main__':
    application.run()
