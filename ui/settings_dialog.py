"""
设置对话框 - 苹果风格
"""

import threading

from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QColor
from openai import OpenAI

from ui.apple_style import Colors, Spacing, Radius
from PyQt6.QtWidgets import QCheckBox
from core.autostart import AutoStartManager
from ui.custom_titlebar import CustomTitleBar


class HotkeyCaptureDialog(QDialog):
    """快捷键捕获对话框"""

    def __init__(self, current_modifiers: list, current_key: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("按下快捷键...")
        self.setFixedSize(420, 200)
        self.modifiers = current_modifiers.copy()
        self.key = current_key
        self._pressed_modifiers = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(20)

        self.label = QLabel(
            "请按下你想要的快捷键组合...\n\n"
            "当前: " + self._format_key(current_modifiers, current_key)
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setProperty("class", "secondary")
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.SM)

        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(self.clear_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, a0: QKeyEvent | None):
        if a0 is None:
            return

        key = a0.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Meta):
            self._pressed_modifiers.add("ctrl")
        elif key == Qt.Key.Key_Alt:
            self._pressed_modifiers.add("alt")
        elif key == Qt.Key.Key_Shift:
            self._pressed_modifiers.add("shift")
        elif self._pressed_modifiers:
            char = a0.text()
            if char and char.strip():
                self.modifiers = sorted(list(self._pressed_modifiers))
                self.key = char.lower()
                self.label.setText(
                    f"已捕获: {self._format_key(self.modifiers, self.key)}"
                )
                self.accept()
                return
        super().keyPressEvent(a0)

    def keyReleaseEvent(self, a0: QKeyEvent | None):
        if a0 is None:
            return

        key = a0.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Meta):
            self._pressed_modifiers.discard("ctrl")
        elif key == Qt.Key.Key_Alt:
            self._pressed_modifiers.discard("alt")
        elif key == Qt.Key.Key_Shift:
            self._pressed_modifiers.discard("shift")
        super().keyReleaseEvent(a0)

    def _on_clear(self):
        self.modifiers = []
        self.key = ""
        self.accept()

    @staticmethod
    def _format_key(modifiers, key):
        if not key and not modifiers:
            return "未设置"
        parts = modifiers + ([key.upper()] if key else [])
        return " + ".join(parts)


class SettingsDialog(QDialog):
    """设置对话框 - 苹果风格"""

    fetch_finished = pyqtSignal(list, str)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumSize(640, 540)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(20)

        tabs = QTabWidget()

        # === API 设置标签页 ===
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setSpacing(16)
        api_layout.setContentsMargins(24, 20, 24, 20)

        self.api_url = QLineEdit()
        self.api_url.setPlaceholderText("https://api.openai.com/v1")
        api_layout.addRow("Base URL", self.api_url)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-...")
        api_layout.addRow("API Key", self.api_key)

        # 模型选择行
        model_row = QHBoxLayout()
        model_row.setSpacing(Spacing.SM)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setMinimumWidth(250)
        self.model_combo.setPlaceholderText("选择或输入模型名称...")
        model_row.addWidget(self.model_combo, 1)

        self.btn_fetch_models = QPushButton("获取")
        self.btn_fetch_models.setFixedWidth(76)
        self.btn_fetch_models.setMinimumHeight(36)
        self.btn_fetch_models.clicked.connect(self._on_fetch_models)
        model_row.addWidget(self.btn_fetch_models)

        api_layout.addRow("模型", model_row)

        self.fetch_status = QLabel("")
        self.fetch_status.setProperty("class", "status")
        api_layout.addRow("", self.fetch_status)

        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 65536)
        self.max_tokens.setValue(4096)
        api_layout.addRow("Max Tokens", self.max_tokens)

        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setSingleStep(0.1)
        self.temperature.setValue(0.7)
        api_layout.addRow("Temperature", self.temperature)

        tabs.addTab(api_tab, "API 设置")

        # === 通用设置标签页 ===
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(24, 20, 24, 20)
        general_layout.setSpacing(16)
        
        self.autostart_checkbox = QCheckBox("开机自动启动")
        self.autostart_checkbox.setChecked(AutoStartManager.is_enabled())
        general_layout.addWidget(self.autostart_checkbox)
        
        general_layout.addStretch()
        tabs.addTab(general_tab, "通用")


        # 连接信号
        self.fetch_finished.connect(self._on_fetch_finished)

        # === 快捷键设置标签页 ===
        hotkey_tab = QWidget()
        hotkey_layout = QVBoxLayout(hotkey_tab)
        hotkey_layout.setSpacing(24)
        hotkey_layout.setContentsMargins(24, 20, 24, 20)

        info_label = QLabel(
            "设置全局快捷键：在任意软件的输入框中选中文本后，\n"
            "按下此快捷键将自动调用 AI 优化并替换原文本。"
        )
        info_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; line-height: 1.5;")
        hotkey_layout.addWidget(info_label)

        hk_form = QFormLayout()
        hk_form.setSpacing(Spacing.MD)

        self.hotkey_label = QLabel("Ctrl + Shift + O")
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_label.setProperty("class", "hotkey-display")
        hk_form.addRow("当前快捷键", self.hotkey_label)

        self.btn_capture = QPushButton("重新捕获快捷键")
        self.btn_capture.setMinimumHeight(40)
        self.btn_capture.clicked.connect(self._on_capture_hotkey)
        hk_form.addRow("", self.btn_capture)

        hotkey_layout.addLayout(hk_form)
        hotkey_layout.addStretch()

        tabs.addTab(hotkey_tab, "快捷键")

        layout.addWidget(tabs)

        # 确定/取消按钮
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setFixedWidth(100)
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("保存")
        self.btn_save.setFixedWidth(100)
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self._on_save)
        btn_box.addWidget(self.btn_save)

        layout.addLayout(btn_box)

    def _load_config(self):
        api_config = self.config_manager.get_api_config()
        self.api_url.setText(api_config.get("base_url", ""))
        self.api_key.setText(api_config.get("api_key", ""))

        saved_model = api_config.get("model", "gpt-4o-mini")
        self._saved_models = api_config.get("cached_models", [])
        self.model_combo.clear()
        if saved_model:
            self.model_combo.addItem(saved_model)
        for m in self._saved_models:
            if m != saved_model:
                self.model_combo.addItem(m)
        self.model_combo.setCurrentText(saved_model)

        self.max_tokens.setValue(api_config.get("max_tokens", 4096))
        self.temperature.setValue(api_config.get("temperature", 0.7))

        hotkey = self.config_manager.get_hotkey()
        self._current_modifiers = hotkey.get("modifiers", ["ctrl", "shift"])
        self._current_key = hotkey.get("key", "o")
        self._update_hotkey_label()

    def _update_hotkey_label(self):
        parts = self._current_modifiers + [self._current_key.upper()]
        self.hotkey_label.setText(" + ".join(parts))

    def _on_capture_hotkey(self):
        dialog = HotkeyCaptureDialog(
            self._current_modifiers,
            self._current_key,
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.modifiers and dialog.key:
                self._current_modifiers = dialog.modifiers
                self._current_key = dialog.key
                self._update_hotkey_label()
            else:
                QMessageBox.warning(self, "提示", "请按下包含修饰键(Ctrl/Alt/Shift/Win)的组合键")

    def _on_fetch_models(self):
        base_url = self.api_url.text().strip()
        api_key = self.api_key.text().strip()

        if not base_url or not api_key:
            QMessageBox.warning(self, "提示", "请先填写 API Base URL 和 API Key")
            return

        self.btn_fetch_models.setEnabled(False)
        self.btn_fetch_models.setText("...")
        self.fetch_status.setText("正在获取模型列表...")
        self.fetch_status.setStyleSheet(f"color: {Colors.ACCENT}; font-size: 12px;")

        def _fetch():
            try:
                client = OpenAI(base_url=base_url, api_key=api_key)
                models = client.models.list()
                model_ids = sorted(
                    [m.id for m in models],
                    key=lambda x: (not x.startswith("gpt"), x)
                )
                self.fetch_finished.emit(model_ids, "")
            except Exception as e:
                self.fetch_finished.emit([], str(e))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_fetch_finished(self, models: list, error: str):
        self.btn_fetch_models.setEnabled(True)
        self.btn_fetch_models.setText("获取")

        if error:
            self.fetch_status.setText(f"获取失败: {error}")
            self.fetch_status.setStyleSheet(f"color: {Colors.ERROR}; font-size: 12px;")
            return

        if not models:
            self.fetch_status.setText("未获取到模型")
            self.fetch_status.setStyleSheet(f"color: {Colors.ERROR}; font-size: 12px;")
            return

        current = self.model_combo.currentText()
        self.model_combo.clear()
        self.model_combo.addItems(models)
        if current and current in models:
            self.model_combo.setCurrentText(current)

        self._saved_models = models
        self.fetch_status.setText(f"已获取 {len(models)} 个模型")
        self.fetch_status.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 12px;")

    def _on_save(self):
        selected_model = self.model_combo.currentText().strip()
        self.config_manager.set_api_config("base_url", self.api_url.text().strip())
        self.config_manager.set_api_config("api_key", self.api_key.text().strip())
        self.config_manager.set_api_config("model", selected_model)
        self.config_manager.set_api_config("cached_models", self._saved_models)
        self.config_manager.set_api_config("max_tokens", self.max_tokens.value())
        self.config_manager.set_api_config("temperature", self.temperature.value())
        self.config_manager.set_hotkey(self._current_modifiers, self._current_key)
        # 保存开机自启设置
        if self.autostart_checkbox.isChecked():
            AutoStartManager.enable()
        else:
            AutoStartManager.disable()
        
        self.accept()
