"""
开机自启管理 - Windows注册表方式
"""

import sys
import winreg
from pathlib import Path


class AutoStartManager:
    """管理Windows开机自启"""
    
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "AIPromptOptimizer"
    
    @staticmethod
    def is_enabled() -> bool:
        """检查是否已启用开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REG_PATH,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, AutoStartManager.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    @staticmethod
    def enable():
        """启用开机自启"""
        try:
            exe_path = sys.executable
            if not exe_path.lower().endswith('.exe'):
                # 开发环境，使用pythonw启动
                exe_path = f'pythonw.exe "{Path(__file__).parent.parent / "main.py"}"'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REG_PATH,
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(
                key,
                AutoStartManager.APP_NAME,
                0,
                winreg.REG_SZ,
                f'"{exe_path}"'
            )
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"[AutoStart] 启用失败: {e}")
            return False
    
    @staticmethod
    def disable():
        """禁用开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                AutoStartManager.REG_PATH,
                0,
                winreg.KEY_WRITE
            )
            try:
                winreg.DeleteValue(key, AutoStartManager.APP_NAME)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"[AutoStart] 禁用失败: {e}")
            return False
