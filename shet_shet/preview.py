"""Aspect-safe camera preview with a separate, transparent landmark overlay."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from .landmarks import EYE_ANCHORS, EYE_CENTERS, FACE_DOTS, FACE_OVAL
from .tracking import FaceTrack


class CameraPreview(QWidget):
    """Paint a letterboxed frame and normalized landmarks in the same viewport."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("preview")
        self.setMinimumSize(620, 430)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self._image: QImage | None = None
        self._tracks: tuple[FaceTrack, ...] = ()
        self._effect_enabled = True
        self._style = "dots"
        self._color = "#68F7D5"
        self._thickness = 3
        self._placeholder = "CAMERA STANDBY\n\nConnect a camera, then press Start camera"

    def set_frame(
        self,
        image: QImage,
        tracks: tuple[FaceTrack, ...],
        *,
        effect_enabled: bool,
        style: str,
        color: str,
        thickness: int,
    ) -> None:
        self._image = image
        self._tracks = tracks
        self._effect_enabled = effect_enabled
        self._style = style
        self._color = color
        self._thickness = thickness
        self.update()

    def clear_frame(self, placeholder: str) -> None:
        self._image = None
        self._tracks = ()
        self._placeholder = placeholder
        self.update()

    def image_rect(self) -> QRectF:
        """Return the exact image rectangle used for both frame and landmarks."""
        bounds = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        if self._image is None or self._image.isNull() or bounds.isEmpty():
            return QRectF()
        scale = min(bounds.width() / self._image.width(), bounds.height() / self._image.height())
        width = self._image.width() * scale
        height = self._image.height() * scale
        return QRectF(
            bounds.x() + (bounds.width() - width) / 2,
            bounds.y() + (bounds.height() - height) / 2,
            width,
            height,
        )

    def map_landmark(self, point: tuple[float, float]) -> QPointF:
        rect = self.image_rect()
        return QPointF(rect.x() + point[0] * rect.width(), rect.y() + point[1] * rect.height())

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0b0a10"))
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 18, 18)
        painter.setClipPath(clip)

        if self._image is None or self._image.isNull():
            painter.setPen(QColor("#777286"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._placeholder)
        else:
            image_target = self.image_rect()
            painter.drawImage(image_target, self._image)
            if self._effect_enabled:
                for track in self._tracks:
                    painter.save()
                    opacity = max(0.0, 1.0 - track.misses / 6.0)
                    painter.setOpacity(opacity)
                    if self._style == "outline":
                        self._draw_outline(painter, track.shape.points, image_target)
                    else:
                        self._draw_dots(painter, track.shape.points, image_target)
                    painter.restore()

        painter.setClipping(False)
        painter.setPen(QPen(QColor("#2d2938"), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 18, 18)
        painter.end()

    def _draw_dots(self, painter: QPainter, points: tuple, rect: QRectF) -> None:
        valid = [index for index in FACE_DOTS if index < len(points)]
        if not valid:
            return
        scale = min(rect.width() / 640.0, rect.height() / 480.0)
        radius = max(1.8, min(3.5, 3.0 * scale))

        # Anchor a saturated but soft glow to each detected iris center.
        for index in EYE_CENTERS:
            if index >= len(points):
                continue
            center = self._map(points[index], rect)
            glow_radius = max(10.0, radius * 5.6)
            gradient = QRadialGradient(center, glow_radius)
            gradient.setColorAt(0.0, QColor(255, 0, 180, 158))
            gradient.setColorAt(0.28, QColor(255, 0, 180, 105))
            gradient.setColorAt(0.68, QColor(235, 0, 170, 36))
            gradient.setColorAt(1.0, QColor(235, 0, 170, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(QRectF(center.x() - glow_radius, center.y() - glow_radius,
                                       glow_radius * 2, glow_radius * 2))

        for index in valid:
            point = self._map(points[index], rect)
            important = index in EYE_ANCHORS
            if index in EYE_CENTERS:
                continue
            painter.setBrush(QColor(255, 255, 255, 230 if important else 190))
            painter.setPen(QPen(QColor(255, 255, 255, 125), 0.45))
            dot_radius = radius * (1.18 if important else 0.78)
            painter.drawEllipse(point, dot_radius, dot_radius)

        # Paint the iris cores last so nearby pearl points cannot obscure them.
        painter.setPen(Qt.PenStyle.NoPen)
        for index in EYE_CENTERS:
            if index >= len(points):
                continue
            point = self._map(points[index], rect)
            painter.setBrush(QColor(255, 0, 185, 225))
            painter.drawEllipse(point, radius * 1.25, radius * 1.25)
            painter.setBrush(QColor(255, 220, 248, 225))
            painter.drawEllipse(point, radius * 0.48, radius * 0.48)

    def _draw_outline(self, painter: QPainter, points: tuple, rect: QRectF) -> None:
        valid = [index for index in FACE_OVAL if index < len(points)]
        if len(valid) < 3:
            return
        path = QPainterPath()
        path.moveTo(self._map(points[valid[0]], rect))
        for index in valid[1:]:
            path.lineTo(self._map(points[index], rect))
        path.closeSubpath()
        try:
            color = QColor(self._color)
            if not color.isValid():
                color = QColor("#68F7D5")
        except (TypeError, ValueError):
            color = QColor("#68F7D5")
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 62), self._thickness + 7,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(path)
        painter.setPen(QPen(color, self._thickness, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(path)

    @staticmethod
    def _map(point: tuple[float, float], rect: QRectF) -> QPointF:
        return QPointF(rect.x() + point[0] * rect.width(), rect.y() + point[1] * rect.height())
