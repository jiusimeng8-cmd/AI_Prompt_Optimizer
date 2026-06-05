# AI Prompt Optimizer

一款 Windows 桌面工具，通过大模型 API（兼容 OpenAI 格式）优化文字并自动复制到剪切板。

## 功能概述

1. **文本优化**：输入文本（A）+ 自定义提示词模板（B）→ 调用大模型 API → 输出优化结果（C）→ 自动复制到剪切板
2. **多提示词支持**：可创建、编辑、保存多个提示词模板，主界面快速切换
3. **全局快捷键替换**：在任意软件的输入框中选中文本，按下快捷键，自动调用 AI 优化并替换原文本
4. **快捷键自定义**：快捷键可自由配置
5. **智能模型获取**：填写 API 地址和 Key 后，一键获取可用模型列表

## 核心流程

```
B（提示词模板）+ "请你只输出最后的提示词内容且输出至「」中" + A（用户输入）
       ↓
  大模型 API
       ↓
  截取「」中的内容 → C（最终输出）
       ↓
  自动复制到剪切板
```

## 项目结构

```
├── main.py                    # 程序入口
├── requirements.txt           # Python 依赖
├── run.bat                    # 开发环境启动脚本
├── build.bat                  # 打包脚本
├── build.spec                 # PyInstaller 打包配置
│
├── core/                      # 核心业务模块
│   ├── config_manager.py      # 配置管理（API设置、快捷键、持久化JSON）
│   ├── api_client.py          # OpenAI兼容API调用客户端
│   ├── prompt_manager.py      # 提示词模板管理（CRUD）
│   └── hotkey_listener.py     # 全局快捷键监听与文本替换
│
└── ui/                        # 用户界面模块
    ├── main_window.py         # 主窗口（输入/输出/操作按钮/系统托盘）
    ├── settings_dialog.py     # 设置对话框（API配置+快捷键捕获）
    └── prompt_dialog.py       # 提示词管理对话框
```

## 环境要求

- Windows 10/11
- Python 3.10+
- 可访问的大模型 API（兼容 OpenAI 格式，需含 `/v1`）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行

```bash
python main.py
```

或双击 `run.bat`（会自动检查并安装依赖）。

### 3. 配置

1. 点击「设置」→「API 设置」
2. 填写 API Base URL（需含 `/v1`，如 `https://api.openai.com/v1`）
3. 填写 API Key
4. 点击「获取模型列表」选择模型
5. 点击确定保存

### 4. 使用

- **主面板模式**：选择提示词 → 输入文本 → 点击「发送优化」→ 结果自动复制到剪切板
- **快捷键模式**：在任意软件的输入框中选中文本 → 按下快捷键（默认 Ctrl+Shift+O）→ 自动优化并替换

## 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| PyQt6 | ≥6.6.0 | 桌面GUI框架 |
| pyperclip | ≥1.9.0 | 剪切板操作 |
| keyboard | ≥0.13.5 | 全局热键监听 |
| pywin32 | ≥306 | Windows API调用 |
| httpx | ≥0.27.0 | OpenAI兼容HTTP API调用 |
| uiautomation | ≥2.0.29 | Windows UI Automation 选区读取 |

## 打包为 EXE

```bash
pyinstaller build.spec
# 或直接运行 build.bat
```

输出文件在 `dist/AI_Prompt_Optimizer.exe`。

## 数据存储

所有用户数据存储在 `%USERPROFILE%\.ai_prompt_optimizer\` 目录下：

- `config.json` - API配置、快捷键设置、激活的提示词ID
- `prompts.json` - 所有提示词模板

## 注意事项

- API Base URL 必须以 `/v1` 结尾
- 快捷键使用 `keyboard` 库（非 pynput），避免与 PyQt6 冲突
- 关闭窗口会最小化到系统托盘，右键托盘图标可退出
- 快捷键替换功能需要管理员权限才能在某些应用中生效

## 当前版本补充

- 支持系统托盘图标、窗口图标和开机自启。
- 全局快捷键选区读取优先使用 Windows UI Automation / Accessibility。
- 剪贴板 fallback 只对白名单普通软件启用，避免 VS Code、Cursor、OpenCode、浏览器、终端等程序在无选区时复制当前行/当前块并误触发 API。
- 设置页包含「API 设置」「通用」「快捷键」三个标签，点击「保存」后写入 API、模型、快捷键和开机自启配置。
- v1.0.1 体积优化版移除 OpenAI SDK，改用 httpx 直连 OpenAI-compatible API，并裁剪未使用的 Qt 可选组件；单文件 EXE 从约 49 MB 降至约 23 MB，未使用 UPX，降低安全软件误报风险。

## 开源许可

本项目基于 MIT License 开源。应用图标来自 Microsoft Fluent Emoji，遵循 MIT License。
