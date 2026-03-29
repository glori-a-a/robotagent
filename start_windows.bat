@echo off
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"
set "PYTHONPATH=%ROOT%"

echo Starting Robot Agent services from %ROOT%

start "reject" cmd /k "cd /d %ROOT%\train && set PYTHONPATH=%ROOT% && python reject_infer.py"
timeout /t 5

start "intent" cmd /k "cd /d %ROOT%\train && set PYTHONPATH=%ROOT% && python intent_infer.py"
timeout /t 5

start "nlu" cmd /k "cd /d %ROOT%\function_call && set PYTHONPATH=%ROOT% && python chatnlu_infer.py"
timeout /t 5

start "main" cmd /k "cd /d %ROOT% && set PYTHONPATH=%ROOT% && python start.py"
timeout /t 5

echo All services started.
echo Run from project folder: python dialog.py
