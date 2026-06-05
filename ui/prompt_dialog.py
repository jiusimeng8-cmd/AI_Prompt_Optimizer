"""
提示词管理对话框 - 苹果风格
"""

from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QTextEdit, QPushButton, QLabel, QLineEdit,
    QMessageBox, QSplitter,
    QWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt

from ui.apple_style import Colors, Spacing, Radius
from ui.custom_titlebar import CustomTitleBar


class PromptManageDialog(QDialog):
    """提示词管理对话框 - 苹果风格"""

    def __init__(self, prompt_manager, config_manager, parent=None):
        super().__init__(parent)
        self.prompt_manager = prompt_manager
        self.config_manager = config_manager
        self._current_id = None
        self._modified = False

        self._init_ui()
        self._load_prompts()

    def _init_ui(self):
        self.setWindowTitle("提示词管理")
        self.setMinimumSize(920, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(20)

        # 左右分割布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        list_label = QLabel("提示词列表")
        list_label.setProperty("class", "secondary")
        left_layout.addWidget(list_label)

        self.prompt_list = QListWidget()
        self.prompt_list.currentRowChanged.connect(self._on_list_selection)
        left_layout.addWidget(self.prompt_list)

        list_btns = QHBoxLayout()
        list_btns.setSpacing(10)

        self.btn_add = QPushButton("+ 新增")
        self.btn_add.setMinimumHeight(36)
        self.btn_add.clicked.connect(self._on_add)
        list_btns.addWidget(self.btn_add)

        self.btn_delete = QPushButton("删除")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.setProperty("class", "danger")
        self.btn_delete.clicked.connect(self._on_delete)
        list_btns.addWidget(self.btn_delete)
        left_layout.addLayout(list_btns)

        splitter.addWidget(left_widget)

        # 右侧编辑区
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        name_label = QLabel("名称")
        name_label.setProperty("class", "secondary")
        right_layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("给提示词起个名字...")
        self.name_edit.textChanged.connect(self._mark_modified)
        right_layout.addWidget(self.name_edit)

        content_label = QLabel("内容 (B)")
        content_label.setProperty("class", "secondary")
        right_layout.addWidget(content_label)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText(
            "在此输入提示词模板...\n\n"
            "说明: 流程是 B + A → 大模型 → C\n"
            "A = 用户输入的内容\n"
            "B = 此处填写的提示词\n"
            "C = AI 优化后的输出"
        )
        self.content_edit.textChanged.connect(self._mark_modified)
        right_layout.addWidget(self.content_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_save_prompt = QPushButton("保存")
        self.btn_save_prompt.clicked.connect(self._on_save_prompt)
        self.btn_save_prompt.setFixedWidth(100)
        self.btn_save_prompt.setMinimumHeight(40)
        self.btn_save_prompt.setProperty("class", "primary")
        btn_row.addWidget(self.btn_save_prompt)
        right_layout.addLayout(btn_row)

        splitter.addWidget(right_widget)
        splitter.setSizes([260, 640])

        layout.addWidget(splitter)

        # 关闭按钮
        close_row = QHBoxLayout()
        close_row.addStretch()
        self.btn_close = QPushButton("关闭")
        self.btn_close.setFixedWidth(100)
        self.btn_close.setMinimumHeight(40)
        self.btn_close.clicked.connect(self._on_close)
        close_row.addWidget(self.btn_close)
        layout.addLayout(close_row)

    def _load_prompts(self):
        self.prompt_list.blockSignals(True)
        self.prompt_list.clear()
        prompts = self.prompt_manager.get_all()
        for p in prompts:
            item = QListWidgetItem(p["name"])
            item.setData(Qt.ItemDataRole.UserRole, p["id"])
            self.prompt_list.addItem(item)

        if self.prompt_list.count() > 0:
            self.prompt_list.setCurrentRow(0)
        self.prompt_list.blockSignals(False)

    def _on_list_selection(self, row):
        if row < 0:
            self._clear_editor()
            return

        item = self.prompt_list.item(row)
        if item is None:
            self._clear_editor()
            return

        prompt_id = item.data(Qt.ItemDataRole.UserRole)
        prompt = self.prompt_manager.get_by_id(prompt_id)

        if prompt:
            self._current_id = prompt_id
            self.name_edit.blockSignals(True)
            self.content_edit.blockSignals(True)
            self.name_edit.setText(prompt["name"])
            self.content_edit.setPlainText(prompt["content"])
            self.name_edit.blockSignals(False)
            self.content_edit.blockSignals(False)
            self._modified = False

    def _clear_editor(self):
        self._current_id = None
        self.name_edit.clear()
        self.content_edit.clear()
        self._modified = False

    def _on_add(self):
        name = "新提示词"
        content = "请对以下文本进行优化，直接输出结果："
        pid = self.prompt_manager.add(name, content)
        self._load_prompts()
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == pid:
                self.prompt_list.setCurrentRow(i)
                break

    def _on_delete(self):
        if self._current_id is None:
            return

        if self._current_id == "default":
            QMessageBox.warning(self, "提示", "默认提示词不可删除")
            return

        prompt = self.prompt_manager.get_by_id(self._current_id)
        if not prompt:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除提示词 \"{prompt['name']}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.prompt_manager.delete(self._current_id)
            self._load_prompts()

    def _on_save_prompt(self):
        if self._current_id is None:
            return

        name = self.name_edit.text().strip()
        content = self.content_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "提示", "请输入提示词名称")
            return
        if not content:
            QMessageBox.warning(self, "提示", "请输入提示词内容")
            return

        self.prompt_manager.update(self._current_id, name, content)
        self._modified = False

        current_row = self.prompt_list.currentRow()
        item = self.prompt_list.item(current_row)
        if item:
            item.setText(name)

        QMessageBox.information(self, "提示", "保存成功")

    def _mark_modified(self):
        self._modified = True

    def _on_close(self):
        if self._modified:
            reply = QMessageBox.question(
                self, "未保存的更改",
                "有未保存的更改，确定关闭吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.accept()
