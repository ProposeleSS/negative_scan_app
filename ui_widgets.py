import numpy as np
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor

class InteractiveCanvas(QLabel):
    cropChanged = pyqtSignal(str, int)
    cropReleased = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1a1a1a; border: 2px dashed #333333; border-radius: 8px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMouseTracking(True)

        self.crop_t, self.crop_b, self.crop_l, self.crop_r = 0, 0, 0, 0
        self.active_edge = None
        self.is_dragging = False
        self.hide_overlay_lines = False  # NEW: Tracks zoomed crop commitment states
        self.pixmap_rect = QRect()

    def update_crop_metrics(self, t, b, l, r):
        self.crop_t, self.crop_b, self.crop_l, self.crop_r = t, b, l, r
        self.update()

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap)
        if pixmap and not pixmap.isNull():
            w, h = pixmap.width(), pixmap.height()
            x = (self.width() - w) // 2
            y = (self.height() - h) // 2
            self.pixmap_rect = QRect(x, y, w, h)

    def mouseMoveEvent(self, event):
        # Disable manual drag selection if crop viewing mode is committed and locked
        if self.pixmap_rect.isNull() or not self.pixmap() or self.hide_overlay_lines:
            return

        pos = event.position().toPoint()
        margin = 15

        x_left = self.pixmap_rect.left() + int(self.pixmap_rect.width() * (self.crop_l / 100.0))
        x_right = self.pixmap_rect.right() - int(self.pixmap_rect.width() * (self.crop_r / 100.0))
        y_top = self.pixmap_rect.top() + int(self.pixmap_rect.height() * (self.crop_t / 100.0))
        y_bottom = self.pixmap_rect.bottom() - int(self.pixmap_rect.height() * (self.crop_b / 100.0))

        if not self.is_dragging:
            if abs(pos.x() - x_left) < margin and y_top <= pos.y() <= y_bottom:
                self.active_edge = "left"
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif abs(pos.x() - x_right) < margin and y_top <= pos.y() <= y_bottom:
                self.active_edge = "right"
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif abs(pos.y() - y_top) < margin and x_left <= pos.x() <= x_right:
                self.active_edge = "top"
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            elif abs(pos.y() - y_bottom) < margin and x_left <= pos.x() <= x_right:
                self.active_edge = "bottom"
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            else:
                self.active_edge = None
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            if self.active_edge == "left":
                pct = int(((pos.x() - self.pixmap_rect.left()) / self.pixmap_rect.width()) * 100)
                self.cropChanged.emit("left", max(0, min(pct, 45)))
            elif self.active_edge == "right":
                pct = int(((self.pixmap_rect.right() - pos.x()) / self.pixmap_rect.width()) * 100)
                self.cropChanged.emit("right", max(0, min(pct, 45)))
            elif self.active_edge == "top":
                pct = int(((pos.y() - self.pixmap_rect.top()) / self.pixmap_rect.height()) * 100)
                self.cropChanged.emit("top", max(0, min(pct, 45)))
            elif self.active_edge == "bottom":
                pct = int(((self.pixmap_rect.bottom() - pos.y()) / self.pixmap_rect.height()) * 100)
                self.cropChanged.emit("bottom", max(0, min(pct, 45)))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.active_edge and not self.hide_overlay_lines:
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.cropReleased.emit()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap_rect.isNull() or not self.pixmap() or self.hide_overlay_lines:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        x_left = self.pixmap_rect.left() + int(self.pixmap_rect.width() * (self.crop_l / 100.0))
        x_right = self.pixmap_rect.right() - int(self.pixmap_rect.width() * (self.crop_r / 100.0))
        y_top = self.pixmap_rect.top() + int(self.pixmap_rect.height() * (self.crop_t / 100.0))
        y_bottom = self.pixmap_rect.bottom() - int(self.pixmap_rect.height() * (self.crop_b / 100.0))

        painter.setBrush(QBrush(QColor(0, 0, 0, 140)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.pixmap_rect.left(), self.pixmap_rect.top(), self.pixmap_rect.width(), y_top - self.pixmap_rect.top())
        painter.drawRect(self.pixmap_rect.left(), y_bottom, self.pixmap_rect.width(), self.pixmap_rect.bottom() - y_bottom)
        painter.drawRect(self.pixmap_rect.left(), y_top, x_left - self.pixmap_rect.left(), y_bottom - y_top)
        painter.drawRect(x_right, y_top, self.pixmap_rect.right() - x_right, y_bottom - y_top)

        painter.setPen(QPen(QColor(255, 140, 0, 200), 2, Qt.PenStyle.SolidLine))
        painter.drawRect(x_left, y_top, x_right - x_left, y_bottom - y_top)


class HistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(280, 110)
        self.hist_data = None

    def update_data(self, hist_data):
        self.hist_data = hist_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(15, 15, 15)))
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if self.hist_data is None:
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "[ Waiting for image data ]")
            return

        r_hist, g_hist, b_hist = self.hist_data
        w, h = self.width(), self.height()

        def draw_channel_curve(hist, color):
            if hist is None or len(hist) == 0: return
            max_val = np.max(hist) if np.max(hist) > 0 else 1
            painter.setPen(QPen(color, 1.5))
            points = []
            for i in range(256):
                x = int((i / 255.0) * (w - 2)) + 1
                y = h - int((hist[i] / max_val) * (h - 5)) - 2
                points.append(QPoint(x, y))
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i+1])

        draw_channel_curve(b_hist, QColor(0, 122, 255, 180))
        draw_channel_curve(g_hist, QColor(46, 125, 50, 180))
        draw_channel_curve(r_hist, QColor(211, 47, 47, 180))