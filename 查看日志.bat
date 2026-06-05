@echo off
echo ============================================
echo   AI Prompt Optimizer - 调试日志查看器
echo ============================================
echo.
echo 说明：
echo 1. 请保持这个窗口打开
echo 2. 然后按 Shift+Alt+X 触发快捷键
echo 3. 观察下方输出的时间戳日志
echo.
echo ============================================
echo.

start /B AI_Prompt_Optimizer.exe

timeout /t 3 /nobreak >nul
echo 程序已启动，等待快捷键触发...
echo.
pause
