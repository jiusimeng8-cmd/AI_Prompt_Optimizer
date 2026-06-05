"""
macOS 风格自定义标题栏
包含红黄绿 traffic light 按钮和窗口拖动区域
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent


class TrafficLightButton(QPushButton):
    """macOS 风格的圆形按钮（红/黄/绿）"""
    
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.base_color = color
        self.hovered = False
        self.setFixedSize(12, 12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据颜色设置基础色和悬停色
        if self.base_color == "red":
            base = QColor("#FF5F57")
            hover = QColor("#FF453A")
        elif self.base_color == "yellow":
            base = QColor("#FFBD2E")
            hover = QColor("#FFD60A")
        else:  # green
            base = QColor("#28C840")
            hover = QColor("#32D74B")
        
        # 绘制圆形按钮
        color = hover if self.hovered else base
        painter.setBrush(color)
        painter.setPen(QPen(QColor(0, 0, 0, 30), 0.5))
        painter.drawEllipse(1, 1, 10, 10)
        
        # 悬停时绘制图标
        if self.hovered:
            painter.setPen(QPen(QColor(0, 0, 0, 160), 1.2))
            if self.base_color == "red":
                # × 符号
                painter.drawLine(4, 4, 8, 8)
                painter.drawLine(8, 4, 4, 8)
            elif self.base_color == "yellow":
                # - 符号
                painter.drawLine(4, 6, 8, 6)
            else:  # green
                # 全屏箭头（简化为 + 符号）
                painter.drawLine(6, 4, 6, 8)
                painter.drawLine(4, 6, 8, 6)


class CustomTitleBar(QWidget):
    """自定义标题栏 - macOS 风格"""
    
    # 信号
    closeClicked = pyqtSignal()
    minimizeClicked = pyqtSignal()
    maximizeClicked = pyqtSignal()
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._drag_pos = QPoint()
        self._is_dragging = False
        
        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)
        
        # Traffic light 按钮容器
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        
        self.close_btn = TrafficLightButton("red")
        self.minimize_btn = TrafficLightButton("yellow")
        self.maximize_btn = TrafficLightButton("green")
        
        self.close_btn.clicked.connect(self.closeClicked.emit)
        self.minimize_btn.clicked.connect(self.minimizeClicked.emit)
        self.maximize_btn.clicked.connect(self.maximizeClicked.emit)
        
        buttons_layout.addWidget(self.close_btn)
        buttons_layout.addWidget(self.minimize_btn)
        buttons_layout.addWidget(self.maximize_btn)
        buttons_widget.setFixedWidth(60)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1D1D1F;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        
        layout.addWidget(buttons_widget)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addSpacing(60)  # 右侧平衡空间
        
        self.setStyleSheet("""
            CustomTitleBar {
                background: #F5F5F7;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
    
    def set_title(self, title: str):
        """更新标题"""
        self.title_label.setText(title)
    
    def mousePressEvent(self, event: QMouseEvent):
        """开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """拖动窗口"""
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """结束拖动"""
        self._is_dragging = False
        event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击最大化/还原"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.maximizeClicked.emit()
            event.accept()
