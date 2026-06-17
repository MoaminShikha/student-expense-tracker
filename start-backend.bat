@echo off
set PYTHONPATH=%~dp0src
python -m uvicorn expense_tracker.app.api:app --host 127.0.0.1 --port 8000 --reload
