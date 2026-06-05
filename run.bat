@echo off
chcp 65001 >nul
echo ============================================
echo    AI Prompt Optimizer - 启动脚本
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查依赖
echo [1/2] 检查依赖...
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 启动
echo [2/2] 启动程序...
python main.py

pause
