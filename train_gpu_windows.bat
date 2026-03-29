@echo off
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"
set "PYTHONPATH=%ROOT%"

echo === 训练拒识模型 (GPU) ===
python train/run.py --model bert --data reject --device cuda --gpu 0
if errorlevel 1 exit /b 1

echo === 训练意图模型 (GPU) ===
python train/run.py --model bert --data intent --device cuda --gpu 0
if errorlevel 1 exit /b 1

echo === 训练完成 ===
pause
