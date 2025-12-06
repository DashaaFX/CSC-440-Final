@echo off
REM Bootstrap script to set up and run the app on Windows CMD

setlocal enableextensions

REM Create virtual environment if missing
if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Ensure instance directory exists for SQLite DB
if not exist instance (
  mkdir instance
)

REM Apply migrations
set FLASK_APP=app.py
flask db upgrade


REM Start the app
python app.py

endlocal