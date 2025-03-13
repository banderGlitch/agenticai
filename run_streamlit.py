import os
import subprocess
import sys

def run_streamlit():
    """
    Run the Streamlit app
    """
    print("Starting SDLC Agents Streamlit App...")
    
    # Check if Streamlit is installed
    try:
        import streamlit
        print("Streamlit is installed.")
    except ImportError:
        print("Streamlit is not installed. Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run the Streamlit app using the Python module approach
    print("Running Streamlit app...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.run(cmd)

if __name__ == "__main__":
    run_streamlit() 