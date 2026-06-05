@echo off
chcp 65001 >nul
echo ============================================
echo    AI Prompt Optimizer - 打包脚本
echo ============================================
echo.

echo [1/2] 安装 PyInstaller...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [2/2] 开始打包...
pyinstaller build.spec --noconfirm

echo.
echo ============================================
echo 打包完成！
echo 输出目录: dist\AI_Prompt_Optimizer.exe
echo ============================================
pause
