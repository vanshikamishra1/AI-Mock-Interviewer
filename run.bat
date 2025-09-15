@echo off
title AI Excel Mock Interviewer Setup

REM Activate virtual environment if exists
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo "No virtual environment found, creating one..."
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
)

REM Start FastAPI backend
start cmd /k "echo Starting backend... & uvicorn main:app --reload --port 8000"

REM Give backend some time to start
timeout /t 5

REM Start Streamlit frontend
start cmd /k "echo Starting Streamlit frontend... & streamlit run app.py"
