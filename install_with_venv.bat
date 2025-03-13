@echo off
echo This script requires Python 3.10 to be installed on your system.
echo.

echo Creating a new virtual environment...
python -m venv venv
echo.

echo Activating the environment...
call venv\Scripts\activate
echo.

echo Installing required packages...
pip install --upgrade pip
pip install langchain-core>=0.1.0
pip install langchain-community>=0.0.10
pip install python-dotenv==1.0.0
pip install groq==0.4.1
pip install pydantic==1.10.8
pip install networkx==3.1
pip install matplotlib==3.7.2
pip install streamlit==1.24.0
pip install streamlit-agraph==0.0.42
pip install watchdog==3.0.0
pip install pillow==9.5.0
pip install langgraph==0.0.19
echo.

echo Environment setup complete!
echo.
echo To activate this environment, run: venv\Scripts\activate
echo To run the Streamlit app, run: streamlit run app.py 