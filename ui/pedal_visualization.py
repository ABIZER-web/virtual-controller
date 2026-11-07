"""Realistic animated racing pedal widget (Accelerator & Brake) using QPainter."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QLinearGradient, QFont, QRadialGradient
)
from PySide6.QtCore import Qt, QRectF, QPointF
from ui.styles import COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE

class SinglePedalWidget(QWidget):
    """Draws a single realistic sports racing pedal with 3D mechanical perspective and travel."""
    def __init__(self, pedal_name: str, is_brake: bool = False, parent=None):
        super().__init__(parent)
        self.pedal_name = pedal_name
        self.is_brake = is_brake
        self.percentage: float = 0.0
        self.setMinimumSize(110, 190)

    def set_percentage(self, pct: float):
        self.percentage = max(0.0, min(100.0, pct))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        accent_color = QColor(COLOR_ACCENT_RED) if self.is_brake else QColor(COLOR_ACCENT_GREEN)

        # 1. Base mounting plate
        base_rect = QRectF(w * 0.1, h * 0.05, w * 0.8, h * 0.88)
        painter.setBrush(QBrush(QColor(16, 22, 32)))
        painter.setPen(QPen(QColor(34, 48, 68), 1.5))
        painter.drawRoundedRect(base_rect, 8, 8)

        # 2. Travel gauge track on side
        track_w = 6
        track_x = w * 0.84
        track_top = h * 0.12
        track_h = h * 0.72
        painter.setBrush(QBrush(QColor(22, 30, 42)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(track_x, track_top, track_w, track_h), 3, 3)

        # Active fill on travel gauge (fills upward from bottom)
        fill_h = (self.percentage / 100.0) * track_h
        if fill_h > 0:
            fill_rect = QRectF(track_x, track_top + (track_h - fill_h), track_w, fill_h)
            painter.setBrush(QBrush(accent_color))
            painter.drawRoundedRect(fill_rect, 3, 3)

        # 3. Mechanical pedal face plate
        # Travel displacement: as percentage increases, pedal presses in (moves down and tilts slightly)
        travel_offset = (self.percentage / 100.0) * (h * 0.18)

        pedal_w = w * 0.58 if self.is_brake else w * 0.48
        pedal_h = h * 0.62
        pedal_x = (w * 0.45) - (pedal_w / 2.0)
        pedal_y = (h * 0.15) + travel_offset

        # Pedal shadow
        shadow_rect = QRectF(pedal_x + 4, pedal_y + 4, pedal_w, pedal_h)
        painter.setBrush(QBrush(QColor(8, 10, 14, 160)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect, 8, 8)

        # Brushed aluminum pedal face
        pedal_grad = QLinearGradient(pedal_x, pedal_y, pedal_x + pedal_w, pedal_y + pedal_h)
        if self.percentage > 5.0:
            pedal_grad.setColorAt(0.0, QColor(70, 85, 105))
            pedal_grad.setColorAt(0.5, QColor(95, 115, 140))
            pedal_grad.setColorAt(1.0, QColor(60, 75, 95))
        else:
            pedal_grad.setColorAt(0.0, QColor(45, 55, 70))
            pedal_grad.setColorAt(0.5, QColor(65, 80, 100))
            pedal_grad.setColorAt(1.0, QColor(40, 50, 65))

        painter.setBrush(QBrush(pedal_grad))
        border_pen = QPen(accent_color if self.percentage > 5.0 else QColor(60, 75, 95), 2 if self.percentage > 5.0 else 1.5)
        painter.setPen(border_pen)
        pedal_rect = QRectF(pedal_x, pedal_y, pedal_w, pedal_h)
        painter.drawRoundedRect(pedal_rect, 8, 8)

        # Sport grip studs / slots on pedal face
        painter.setBrush(QBrush(QColor(12, 16, 22)))
        painter.setPen(Qt.NoPen)
        num_rows = 5
        row_step = pedal_h / (num_rows + 1)
        for r in range(1, num_rows + 1):
            sy = pedal_y + r * row_step
            # Left stud
            painter.drawEllipse(QPointF(pedal_x + pedal_w * 0.3, sy), 3.5, 3.5)
            # Right stud
            painter.drawEllipse(QPointF(pedal_x + pedal_w * 0.7, sy), 3.5, 3.5)

        # 4. Text readout at bottom of base
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        text_rect = QRectF(w * 0.1, h * 0.80, w * 0.8, h * 0.15)
        pct_text = f"{int(self.percentage)}%"
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.pedal_name}\n{pct_text}")


class DualPedalsWidget(QFrame):
    """Combines Accelerator and Brake pedals into a dual pedal deck."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PanelCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        self.brake_pedal = SinglePedalWidget("BRAKE", is_brake=True)
        self.accel_pedal = SinglePedalWidget("THROTTLE", is_brake=False)

        layout.addWidget(self.brake_pedal)
        layout.addWidget(self.accel_pedal)

    def update_pedals(self, accel_pct: float, brake_pct: float):
        self.accel_pedal.set_percentage(accel_pct)
        self.brake_pedal.set_percentage(brake_pct)

