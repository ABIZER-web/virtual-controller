"""Realistic animated vector steering wheel widget using QPainter."""
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QRadialGradient, QLinearGradient,
    QFont, QPainterPath, QPolygonF
)
from PySide6.QtCore import Qt, QPointF, QRectF
from ui.styles import COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE

class SteeringWheelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self._angle: float = 0.0          # Current rotation angle in degrees
        self._normalized: float = 0.0     # -1.0 to 1.0

    def set_angle(self, angle_degrees: float, normalized: float = 0.0):
        self._angle = angle_degrees
        self._normalized = normalized
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        width = self.width()
        height = self.height()
        side = min(width, height)
        radius = side * 0.44

        # Center coordinates
        cx = width / 2.0
        cy = height / 2.0

        # Draw outer background glow and angle gauge ring
        self._draw_gauge_arc(painter, cx, cy, radius + 12)

        # Save state for wheel rotation
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)

        # 1. Draw outer rim (Dark perforated leather / textured rubber)
        self._draw_outer_rim(painter, radius)

        # 2. Draw 12 o'clock racing stripe (Electric Blue)
        self._draw_center_stripe(painter, radius)

        # 3. Draw spokes (Left, Right, Bottom sport 3-spoke design)
        self._draw_spokes(painter, radius)

        # 4. Draw central hub with brushed aluminum bezel and horn button
        self._draw_hub(painter, radius * 0.38)

        painter.restore()

        # Draw digital readout below the hub
        self._draw_readout(painter, cx, cy + radius * 0.65)

    def _draw_gauge_arc(self, painter: QPainter, cx: float, cy: float, r: float):
        """Draws background subtle graduation arc for steering angle."""
        painter.save()
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)

        # Track arc background
        pen_bg = QPen(QColor(30, 42, 60, 160), 4)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 45 * 16, 270 * 16)

        # Active angle arc
        span = int(-self._normalized * 135.0 * 16)
        if abs(span) > 10:
            color = QColor(COLOR_ACCENT_ORANGE) if abs(self._normalized) > 0.8 else QColor(COLOR_ACCENT_BLUE)
            pen_active = QPen(color, 6)
            pen_active.setCapStyle(Qt.RoundCap)
            painter.setPen(pen_active)
            painter.drawArc(rect, 90 * 16, span)

        painter.restore()

    def _draw_outer_rim(self, painter: QPainter, r: float):
        rim_thickness = r * 0.18

        # Outer rim shadow/glow
        radial_grad = QRadialGradient(QPointF(0, 0), r)
        radial_grad.setColorAt(0.70, QColor(25, 27, 32))
        radial_grad.setColorAt(0.90, QColor(14, 16, 20))
        radial_grad.setColorAt(1.00, QColor(8, 10, 12))

        pen_rim = QPen(QBrush(radial_grad), rim_thickness)
        pen_rim.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_rim)
        painter.drawEllipse(QPointF(0, 0), r - rim_thickness / 2, r - rim_thickness / 2)

        # Inner stitch highlight
        pen_stitch = QPen(QColor(40, 52, 70), 2)
        painter.setPen(pen_stitch)
        painter.drawEllipse(QPointF(0, 0), r - rim_thickness + 2, r - rim_thickness + 2)

        # Outer edge highlight
        pen_edge = QPen(QColor(60, 75, 95, 120), 1.5)
        painter.setPen(pen_edge)
        painter.drawEllipse(QPointF(0, 0), r - 2, r - 2)

    def _draw_center_stripe(self, painter: QPainter, r: float):
        """Draws the electric blue 12 o'clock racing orientation stripe."""
        rim_thickness = r * 0.18
        stripe_width = r * 0.08
        stripe_height = rim_thickness * 1.05

        rect = QRectF(-stripe_width / 2.0, -r, stripe_width, stripe_height)
        painter.fillRect(rect, QColor(COLOR_ACCENT_BLUE))

        # Thin highlight on stripe
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.drawLine(QPointF(0, -r), QPointF(0, -r + stripe_height))

    def _draw_spokes(self, painter: QPainter, r: float):
        """Draws 3 sports spokes (Left, Right, Bottom)."""
        hub_r = r * 0.38
        spoke_thick = r * 0.12

        # Brushed metal gradient
        grad = QLinearGradient(-r, 0, r, 0)
        grad.setColorAt(0.0, QColor(55, 65, 80))
        grad.setColorAt(0.5, QColor(85, 100, 120))
        grad.setColorAt(1.0, QColor(55, 65, 80))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(30, 38, 48), 2))

        # Left Spoke
        path_left = QPainterPath()
        path_left.moveTo(-hub_r, -spoke_thick * 0.5)
        path_left.lineTo(-r * 0.85, -spoke_thick * 0.7)
        path_left.lineTo(-r * 0.85, spoke_thick * 0.7)
        path_left.lineTo(-hub_r, spoke_thick * 0.5)
        path_left.closeSubpath()
        painter.drawPath(path_left)

        # Right Spoke
        path_right = QPainterPath()
        path_right.moveTo(hub_r, -spoke_thick * 0.5)
        path_right.lineTo(r * 0.85, -spoke_thick * 0.7)
        path_right.lineTo(r * 0.85, spoke_thick * 0.7)
        path_right.lineTo(hub_r, spoke_thick * 0.5)
        path_right.closeSubpath()
        painter.drawPath(path_right)

        # Bottom Spoke (Slightly narrower sport spoke)
        path_bottom = QPainterPath()
        path_bottom.moveTo(-spoke_thick * 0.45, hub_r)
        path_bottom.lineTo(-spoke_thick * 0.35, r * 0.85)
        path_bottom.lineTo(spoke_thick * 0.35, r * 0.85)
        path_bottom.lineTo(spoke_thick * 0.45, hub_r)
        path_bottom.closeSubpath()
        painter.drawPath(path_bottom)

        # Cutout racing slots on spokes
        painter.setBrush(QBrush(QColor(14, 18, 25)))
        painter.setPen(QPen(QColor(40, 50, 65), 1))
        # Left slot
        painter.drawRoundedRect(QRectF(-r * 0.72, -spoke_thick * 0.25, r * 0.22, spoke_thick * 0.5), 3, 3)
        # Right slot
        painter.drawRoundedRect(QRectF(r * 0.50, -spoke_thick * 0.25, r * 0.22, spoke_thick * 0.5), 3, 3)
        # Bottom slot
        painter.drawRoundedRect(QRectF(-spoke_thick * 0.2, hub_r * 1.3, spoke_thick * 0.4, r * 0.22), 3, 3)

    def _draw_hub(self, painter: QPainter, hub_r: float):
        """Draws center hub with motorsport emblem and metallic ring."""
        # Metallic outer ring
        hub_grad = QRadialGradient(QPointF(0, 0), hub_r)
        hub_grad.setColorAt(0.0, QColor(40, 48, 60))
        hub_grad.setColorAt(0.7, QColor(25, 30, 40))
        hub_grad.setColorAt(0.9, QColor(70, 85, 110))
        hub_grad.setColorAt(1.0, QColor(15, 20, 26))

        painter.setBrush(QBrush(hub_grad))
        painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 2))
        painter.drawEllipse(QPointF(0, 0), hub_r, hub_r)

        # Carbon-look center badge
        badge_r = hub_r * 0.65
        badge_grad = QRadialGradient(QPointF(0, 0), badge_r)
        badge_grad.setColorAt(0.0, QColor(20, 25, 35))
        badge_grad.setColorAt(1.0, QColor(10, 12, 16))
        painter.setBrush(QBrush(badge_grad))
        painter.setPen(QPen(QColor(50, 65, 85), 1.5))
        painter.drawEllipse(QPointF(0, 0), badge_r, badge_r)

        # Virtual Drive motorsport logo emblem in center
        painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 2))
        painter.setFont(QFont("Arial", int(badge_r * 0.35), QFont.Bold))
        painter.drawText(QRectF(-badge_r, -badge_r, badge_r * 2, badge_r * 2), Qt.AlignCenter, "VD")

    def _draw_readout(self, painter: QPainter, cx: float, cy: float):
        """Draws clean digital readout below the hub."""
        painter.save()
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(font)

        deg_str = f"{int(self._angle):+d}°"
        pct_str = f"{int(self._normalized * 100):+d}%"

        # Background badge for text
        w = 110
        h = 28
        rect = QRectF(cx - w / 2, cy - h / 2, w, h)
        painter.setBrush(QBrush(QColor(16, 22, 32, 220)))
        painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 1.5))
        painter.drawRoundedRect(rect, 6, 6)

        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(rect, Qt.AlignCenter, f"{deg_str} | {pct_str}")
        painter.restore()

