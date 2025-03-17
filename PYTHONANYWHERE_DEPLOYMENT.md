# Step-by-Step Guide to Deploy Dewwy on PythonAnywhere

This guide walks you through deploying your Dewwy pet robot web demo on PythonAnywhere.

## Setup

### 1. Sign Up for PythonAnywhere

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. Sign up for a free account (or log in if you already have one)

### 2. Upload Your Project Files

#### Using Git (Recommended)

1. From the PythonAnywhere dashboard, click on **Consoles** and open a new **Bash** console
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/dewwy.git
   ```
3. If your repository is private, you'll need to set up SSH keys or enter your credentials

#### Manual Upload (Alternative)

1. From the PythonAnywhere dashboard, click on **Files**
2. Create a new directory called `dewwy`
3. Navigate into the directory
4. Upload the key files/folders:
   - `/web/` directory (all contents)
   - `/simulation/virtual_sensors.py`
   - `/simulation/virtual_motors.py`
   - `/raspberry_pi/behavior/` directory
   - Other required Python modules

### 3. Create a Virtual Environment

1. In the Bash console, run:
   ```bash
   cd dewwy
   python3 -m venv venv
   source venv/bin/activate
   pip install -r web/requirements.txt
   ```

### 4. Set Up a Web App

1. Go to the **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose your domain (e.g., `yourusername.pythonanywhere.com`)
4. Select **Manual configuration**
5. Choose **Python 3.8** (or newer if available)

### 5. Configure the Web App

1. In the **Code** section of your web app configuration:
   - Set **Source code** to `/home/yourusername/dewwy`
   - Set **Working directory** to `/home/yourusername/dewwy`
   - Set **WSGI configuration file** path (it should be auto-filled)

2. Click on the WSGI configuration file link to edit it:
   - Delete all the sample code
   - Add this code:
   ```python
   import sys
   import os

   # Add your project directory to the path
   path = '/home/yourusername/dewwy'
   if path not in sys.path:
       sys.path.append(path)

   # Import the Flask application object
   from web.wsgi import application
   ```

3. In the **Virtualenv** section:
   - Enter the path to your virtual environment: `/home/yourusername/dewwy/venv`

### 6. Set Up Static Files

1. In the **Static files** section, add:
   - URL: `/static/`
   - Directory: `/home/yourusername/dewwy/web/static/`

### 7. Database Setup (If Needed)

1. If your app needs a persistent database, you can keep the SQLite file in your project directory
2. Make sure the path in your Flask app is absolute rather than relative

### 8. Restart Your Web App

1. Click the **Reload** button for your web app
2. Your app should now be live at `yourusername.pythonanywhere.com`

### 9. Troubleshooting

If your app doesn't work:
1. Check the **Error logs** section on your Web tab
2. Common issues:
   - Missing dependencies: Install them with pip
   - Path issues: Ensure all import paths are correct
   - Permission issues: Check file permissions

## Updating Your Application

To update your app after making changes:

### If Using Git

1. Open a Bash console
2. Navigate to your project: `cd dewwy`
3. Pull the changes: `git pull`
4. Reload your web app from the Web tab

### If Manually Uploading

1. Upload new files using the Files section
2. Reload your web app from the Web tab

## Free Account Limitations

Be aware of the PythonAnywhere free tier limitations:
- CPU and bandwidth restrictions
- Your app may sleep after periods of inactivity
- Limited number of web apps
