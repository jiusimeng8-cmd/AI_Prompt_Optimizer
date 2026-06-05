"""
浮动加载动画 - 简洁苹果风格
关键：不抢焦点，避免干扰 Ctrl+C
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPainterPath
import ctypes


class LoadingWindow(QWidget):
    """极简加载指示器 - 不抢焦点"""

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._phase = 0
        self._timer = None

    def _init_ui(self):
        """初始化 - 关键：设置不抢焦点"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setFixedSize(60, 24)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def showEvent(self, a0):
        print(f"[LoadingWindow] showEvent 被触发，启动定时器")
        super().showEvent(a0)
        if not self._timer:
            self._timer = QTimer()
            self._timer.timeout.connect(self._tick)
        self._timer.start(180)
        # 用 Win32 API 确保不抢焦点
        hwnd = int(self.winId())
        SWP_NOACTIVATE = 0x0010
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        ctypes.windll.user32.SetWindowPos(
            hwnd, -1, 0, 0, 0, 0,
            SWP_NOACTIVATE | SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )

    def hideEvent(self, a0):
        print(f"[LoadingWindow] hideEvent 被触发，停止定时器")
        super().hideEvent(a0)
        if self._timer:
            self._timer.stop()
        # 重置动画状态
        self._phase = 0

    def _tick(self):
        self._phase = (self._phase + 1) % 3
        self.update()

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景 - 简洁浅色胶囊
        path = QPainterPath()
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, QColor(245, 245, 245, 230))

        # 三个点 - 活跃点更亮更大
        cx, cy = self.width() / 2, self.height() / 2
        spacing = 10
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(3):
            x = cx + (i - 1) * spacing
            is_active = (i == self._phase)
            if is_active:
                painter.setBrush(QColor(255, 255, 255, 255))
                painter.drawEllipse(QPointF(x, cy), 3.5, 3.5)
            else:
                painter.setBrush(QColor(160, 160, 160, 180))
                painter.drawEllipse(QPointF(x, cy), 2.5, 2.5)

        painter.end()

    def move_to_bottom_center(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        margin = max(80, geo.height() // 10)
        self.move(
            geo.center().x() - self.width() // 2,
            geo.bottom() - self.height() - margin
        )
