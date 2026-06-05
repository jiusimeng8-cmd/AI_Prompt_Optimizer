"""
主窗口 - 苹果风格极简界面
"""

import pyperclip

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QLabel,
    QSystemTrayIcon, QMenu, QStatusBar,
    QMessageBox, QApplication, QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QColor, QIcon

from core.hotkey_listener import HotkeyListener
from core.resources import resource_path
from ui.settings_dialog import SettingsDialog
from ui.prompt_dialog import PromptManageDialog
from ui.apple_style import Colors, Spacing, Radius, create_card_shadow
from ui.custom_titlebar import CustomTitleBar


class MainWindow(QMainWindow):
    status_signal = pyqtSignal(str)
    optimize_result = pyqtSignal(str)
    optimize_error = pyqtSignal(str)
    optimize_stream = pyqtSignal(str)
    processing_start_signal = pyqtSignal()
    processing_end_signal = pyqtSignal()

    def __init__(self, config_manager, api_client, prompt_manager):
        super().__init__()
        self.config_manager = config_manager
        self.api_client = api_client
        self.prompt_manager = prompt_manager
        self.hotkey_listener = HotkeyListener(config_manager, api_client, prompt_manager)
        self.tray_icon = None
        self.app_icon = QIcon(str(resource_path("icon.ico")))

        self._init_ui()
        self._init_tray()
        self._init_hotkey()
        self._connect_signals()

        # 延迟启动全局快捷键，避免与 Qt 事件循环初始化冲突
        self._start_hotkey_if_configured()

    def _init_ui(self):
        """初始化界面 - 苹果风格无边框窗口"""
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setMinimumSize(840, 680)
        self.resize(920, 760)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        # 主容器（带圆角和阴影）
        central = QWidget()
        central.setObjectName("mainContainer")
        central.setStyleSheet("""
            QWidget#mainContainer {
                background: #F5F5F7;
                border-radius: 10px;
            }
        """)
        self.setCentralWidget(central)
        
        # 添加窗口阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        central.setGraphicsEffect(shadow)
        
        # 主布局
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        self.title_bar = CustomTitleBar("AI Prompt Optimizer")
        self.title_bar.closeClicked.connect(self.close)
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        self.title_bar.maximizeClicked.connect(self._toggle_maximize)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 20, 40, 28)
        content_layout.setSpacing(20)
        main_layout.addWidget(content_widget)

        # --- 提示词选择行 ---
        prompt_row = QHBoxLayout()
        prompt_row.setSpacing(12)

        prompt_label = QLabel("提示词")
        prompt_label.setProperty("class", "secondary-lg")
        prompt_row.addWidget(prompt_label)

        self.prompt_combo = QComboBox()
        self.prompt_combo.setMinimumWidth(280)
        self.prompt_combo.setMinimumHeight(36)
        self._refresh_prompt_combo()
        prompt_row.addWidget(self.prompt_combo, 1)

        self.btn_manage_prompts = QPushButton("管理")
        self.btn_manage_prompts.setFixedWidth(80)
        self.btn_manage_prompts.setMinimumHeight(36)
        prompt_row.addWidget(self.btn_manage_prompts)

        content_layout.addLayout(prompt_row)
        content_layout.addSpacing(8)

        # --- 分隔线 ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setProperty("class", "separator")
        content_layout.addWidget(separator)
        content_layout.addSpacing(8)

        # --- 输入区域 ---
        input_label = QLabel("输入")
        input_label.setProperty("class", "secondary")
        content_layout.addWidget(input_label)
        content_layout.addSpacing(4)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在此输入要处理的文本...")
        self.input_text.setAcceptRichText(False)
        self.input_text.setMinimumHeight(160)
        self.input_text.setGraphicsEffect(create_card_shadow(opacity=0.04, radius=8, y_offset=1))
        content_layout.addWidget(self.input_text, 4)

        # --- 输出区域 ---
        out_header = QHBoxLayout()
        out_header.setSpacing(8)

        out_label = QLabel("输出")
        out_label.setProperty("class", "secondary")
        out_header.addWidget(out_label)
        out_header.addStretch()

        self.btn_copy = QPushButton("复制")
        self.btn_copy.setFixedWidth(80)
        self.btn_copy.setMinimumHeight(32)
        out_header.addWidget(self.btn_copy)
        content_layout.addLayout(out_header)
        content_layout.addSpacing(4)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("AI 优化结果将显示在这里...")
        self.output_text.setMinimumHeight(180)
        self.output_text.setGraphicsEffect(create_card_shadow(opacity=0.04, radius=8, y_offset=1))
        content_layout.addWidget(self.output_text, 5)

        # --- 操作按钮行 ---
        content_layout.addSpacing(4)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_optimize = QPushButton("发送优化")
        self.btn_optimize.setMinimumHeight(48)
        self.btn_optimize.setProperty("class", "primary")
        btn_layout.addWidget(self.btn_optimize, 1)

        self.btn_settings = QPushButton("设置")
        self.btn_settings.setFixedWidth(90)
        self.btn_settings.setMinimumHeight(40)
        btn_layout.addWidget(self.btn_settings)

        self.btn_hotkey_toggle = QPushButton("启动快捷键")
        self.btn_hotkey_toggle.setFixedWidth(130)
        self.btn_hotkey_toggle.setMinimumHeight(40)
        btn_layout.addWidget(self.btn_hotkey_toggle)

        content_layout.addLayout(btn_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")



    def _toggle_maximize(self):
        """切换最大化/还原"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _init_tray(self):
        """初始化系统托盘"""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            if not self.app_icon.isNull():
                self.tray_icon.setIcon(self.app_icon)
            self.tray_icon.setToolTip("AI Prompt Optimizer")

            tray_menu = QMenu()
            show_action = QAction("显示主窗口", self)
            show_action.triggered.connect(self.show_and_focus)
            tray_menu.addAction(show_action)

            quit_action = QAction("退出", self)
            quit_action.triggered.connect(self.quit_app)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.show()
        except Exception as e:
            print(f"Tray icon init failed: {e}")
            self.tray_icon = None

    def _init_hotkey(self):
        """初始化快捷键监听"""
        self.hotkey_listener.set_status_callback(
            lambda msg: self.status_signal.emit(msg)
        )
        self.hotkey_listener.set_processing_callbacks(
            lambda: self.processing_start_signal.emit(),
            lambda: self.processing_end_signal.emit()
        )

    def _connect_signals(self):
        """连接信号"""
        self.btn_optimize.clicked.connect(self._on_optimize)
        self.btn_copy.clicked.connect(self._on_copy)
        self.btn_settings.clicked.connect(self._on_settings)
        self.btn_manage_prompts.clicked.connect(self._on_manage_prompts)
        self.btn_hotkey_toggle.clicked.connect(self._on_toggle_hotkey)
        self.prompt_combo.currentIndexChanged.connect(self._on_prompt_changed)
        self.status_signal.connect(self._on_status_update)
        self.optimize_result.connect(self._on_optimize_result)
        self.optimize_error.connect(self._on_optimize_error)
        self.optimize_stream.connect(self._on_optimize_stream)
        self.processing_start_signal.connect(self._on_processing_start)
        self.processing_end_signal.connect(self._on_processing_end)

    def _on_status_update(self, message):
        """状态更新"""
        self.status_bar.showMessage(message)

    def _start_hotkey_if_configured(self):
        """如果 API Key 已配置，延迟启动快捷键避免与 Qt 事件循环冲突"""
        api_key = self.config_manager.get_api_config().get("api_key", "")
        if api_key:
            QTimer.singleShot(1000, self._delayed_start_hotkey)
        else:
            self.btn_hotkey_toggle.setText("启动快捷键")
            self.status_bar.showMessage("请先配置 API Key")

    def _delayed_start_hotkey(self):
        """延迟启动快捷键"""
        try:
            self.hotkey_listener.start()
            self.btn_hotkey_toggle.setText("停止快捷键")
            self.status_bar.showMessage("全局快捷键已启动")
        except Exception as e:
            self.status_bar.showMessage(f"快捷键启动失败: {e}")

    # ========== 槽函数 ==========

    def _on_optimize(self):
        """发送优化请求"""
        user_input = self.input_text.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "提示", "请输入要处理的文本")
            return

        # 获取当前提示词
        prompt_id = self.config_manager.get_active_prompt_id()
        prompt = self.prompt_manager.get_by_id(prompt_id)
        if not prompt:
            QMessageBox.warning(self, "提示", "未找到激活的提示词")
            return

        self.btn_optimize.setEnabled(False)
        self.btn_optimize.setText("处理中...")
        self.output_text.clear()
        self.status_bar.showMessage(f"正在调用 AI（提示词: {prompt['name']}）...")

        def on_success(text):
            self.optimize_result.emit(text.strip())

        def on_error(error):
            self.optimize_error.emit(error)

        def on_stream(delta):
            self.optimize_stream.emit(delta)

        self.api_client.call(
            user_input=user_input,
            prompt_template=prompt["content"],
            on_success=on_success,
            on_error=on_error,
            on_stream=on_stream,
        )

    def _on_optimize_result(self, text):
        """优化完成回调（线程安全）"""
        self.output_text.setPlainText(text)
        pyperclip.copy(text)
        self.btn_optimize.setEnabled(True)
        self.btn_optimize.setText("发送优化")
        self.status_bar.showMessage("完成！结果已复制到剪切板")

    def _on_optimize_error(self, error):
        """优化错误回调（线程安全）"""
        self.output_text.setPlainText(f"[错误] {error}")
        self.btn_optimize.setEnabled(True)
        self.btn_optimize.setText("发送优化")
        self.status_bar.showMessage(f"错误: {error}")

    def _on_optimize_stream(self, delta):
        """流式输出回调（线程安全）"""
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(delta)
        self.output_text.setTextCursor(cursor)

    def _on_copy(self):
        """复制输出内容"""
        text = self.output_text.toPlainText().strip()
        if text:
            pyperclip.copy(text)
            self.status_bar.showMessage("已复制到剪切板")
        else:
            QMessageBox.information(self, "提示", "输出区域为空")

    def _on_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            # 设置更新后重启快捷键监听
            self.hotkey_listener.restart()
            self._start_hotkey_if_configured()

    def _on_manage_prompts(self):
        """打开提示词管理对话框"""
        dialog = PromptManageDialog(self.prompt_manager, self.config_manager, self)
        if dialog.exec() == PromptManageDialog.DialogCode.Accepted:
            self._refresh_prompt_combo()
            self.status_bar.showMessage("提示词已更新")

    def _on_toggle_hotkey(self):
        """切换快捷键状态"""
        if self.hotkey_listener._running:
            self.hotkey_listener.stop()
            self.btn_hotkey_toggle.setText("启动快捷键")
        else:
            api_key = self.config_manager.get_api_config().get("api_key", "")
            if not api_key:
                QMessageBox.warning(self, "提示", "请先在设置中配置 API Key")
                return
            self.hotkey_listener.start()
            self.btn_hotkey_toggle.setText("停止快捷键")

    def _on_prompt_changed(self, index):
        """提示词下拉框切换"""
        if index >= 0:
            prompt_ids = self.prompt_manager.get_ids()
            if index < len(prompt_ids):
                self.config_manager.set_active_prompt_id(prompt_ids[index])
                self.status_bar.showMessage(f"已切换提示词: {self.prompt_combo.currentText()}")

    def _on_tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_focus()

    def _refresh_prompt_combo(self):
        """刷新提示词下拉框"""
        self.prompt_combo.blockSignals(True)
        self.prompt_combo.clear()
        prompts = self.prompt_manager.get_all()
        active_id = self.config_manager.get_active_prompt_id()

        active_index = 0
        for i, p in enumerate(prompts):
            self.prompt_combo.addItem(p["name"])
            if p["id"] == active_id:
                active_index = i

        self.prompt_combo.setCurrentIndex(active_index)
        self.prompt_combo.blockSignals(False)

    def show_and_focus(self):
        """显示并聚焦主窗口"""
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_processing_start(self):
        """快捷键模式处理开始。"""
        print("[MainWindow] 快捷键处理开始（无浮动加载动画）")

    def _on_processing_end(self):
        """快捷键模式处理结束。"""
        print("[MainWindow] 快捷键处理结束（无浮动加载动画）")

    def quit_app(self):
        """退出应用"""
        self.hotkey_listener.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, a0: QCloseEvent | None):
        """关闭窗口时隐藏到托盘"""
        if a0 is not None:
            a0.ignore()
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage(
                "AI Prompt Optimizer",
                "程序已最小化到系统托盘，右键图标可退出",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
