"""Compact dark desktop UI for the local face-tracking camera."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt, QSettings, QTimer, QSize
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QSlider, QVBoxLayout, QWidget,
)

from .camera import CameraScanner, CameraWorker
from .preview import CameraPreview

logger = logging.getLogger(__name__)


def _label(text: str, style: str = "") -> QLabel:
    item = QLabel(text)
    item.setObjectName(style)
    return item


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.settings = QSettings("ShetShetNakitaAko", "Camera")
        self.worker: CameraWorker | None = None
        self.scanner: CameraScanner | None = None
        self.devices: list[tuple[int, str]] = []
        self._last_error: str | None = None
        self._pending_restart = False
        self.frame_timer = QTimer(self)
        self.frame_timer.setInterval(33)
        self.frame_timer.timeout.connect(self._refresh_preview)
        self.setWindowTitle("SHET SHET NAKITA AKO")
        self.setMinimumSize(QSize(920, 620))
        self.resize(1180, 760)
        self._build_ui()
        self._restore_settings()
        self._apply_style()
        QTimer.singleShot(250, self.refresh_cameras)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        page = QVBoxLayout(root)
        page.setContentsMargins(28, 24, 28, 22)
        page.setSpacing(18)

        header = QHBoxLayout()
        brand = QVBoxLayout()
        title = _label("SHET SHET NAKITA AKO", "title")
        subtitle = _label("LOCAL FACE TRACKING STUDIO", "subtitle")
        brand.addWidget(title)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch(1)
        self.live_badge = _label("●  CAMERA OFF", "badge")
        header.addWidget(self.live_badge)
        page.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(18)
        self.preview = CameraPreview()
        content.addWidget(self.preview, 1)

        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        controls = QVBoxLayout(panel)
        controls.setContentsMargins(18, 18, 18, 18)
        controls.setSpacing(13)
        controls.addWidget(_label("CAMERA", "section"))
        camera_row = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.addItem("Looking for cameras…", None)
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setObjectName("iconButton")
        self.refresh_button.setToolTip("Scan for cameras")
        self.refresh_button.clicked.connect(self.refresh_cameras)
        camera_row.addWidget(self.camera_combo, 1)
        camera_row.addWidget(self.refresh_button)
        controls.addLayout(camera_row)
        self.start_button = QPushButton("Start camera")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.toggle_camera)
        controls.addWidget(self.start_button)

        controls.addSpacing(8)
        controls.addWidget(_label("TRACKING EFFECT", "section"))
        self.effect_check = QCheckBox("Show tracking effect")
        self.effect_check.setChecked(True)
        self.effect_check.toggled.connect(self._push_options)
        controls.addWidget(self.effect_check)
        controls.addWidget(_label("Filter style", "caption"))
        self.filter_style_combo = QComboBox()
        self.filter_style_combo.addItem("Luminous landmark dots", "dots")
        self.filter_style_combo.addItem("Face contour", "outline")
        self.filter_style_combo.currentIndexChanged.connect(self._push_options)
        controls.addWidget(self.filter_style_combo)
        self.mirror_check = QCheckBox("Mirror preview")
        self.mirror_check.setChecked(True)
        self.mirror_check.toggled.connect(self._push_options)
        controls.addWidget(self.mirror_check)

        controls.addWidget(_label("Outline colour", "caption"))
        self.color_combo = QComboBox()
        self.color_combo.addItem("Mint glow", "#68F7D5")
        self.color_combo.addItem("Electric pink", "#FF72C6")
        self.color_combo.addItem("Ice blue", "#76B9FF")
        self.color_combo.currentIndexChanged.connect(self._push_options)
        controls.addWidget(self.color_combo)

        controls.addWidget(_label("Line thickness", "caption"))
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 7)
        self.thickness_slider.setValue(3)
        self.thickness_slider.valueChanged.connect(self._push_options)
        controls.addWidget(self.thickness_slider)

        controls.addWidget(_label("Smoothing", "caption"))
        self.smoothing_slider = QSlider(Qt.Orientation.Horizontal)
        self.smoothing_slider.setRange(20, 95)
        self.smoothing_slider.setValue(55)
        self.smoothing_slider.valueChanged.connect(self._push_options)
        controls.addWidget(self.smoothing_slider)

        controls.addStretch(1)
        stats = QHBoxLayout()
        self.face_stat = _label("0 faces", "stat")
        self.fps_stat = _label("— FPS", "stat")
        stats.addWidget(self.face_stat)
        stats.addStretch(1)
        stats.addWidget(self.fps_stat)
        controls.addLayout(stats)
        control_scroll = QScrollArea()
        control_scroll.setObjectName("controlScroll")
        control_scroll.setFixedWidth(286)
        control_scroll.setWidgetResizable(True)
        control_scroll.setFrameShape(QFrame.Shape.NoFrame)
        control_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        control_scroll.setWidget(panel)
        content.addWidget(control_scroll)
        page.addLayout(content, 1)

        footer = QHBoxLayout()
        self.status_label = _label("Ready when you are.", "status")
        self.privacy_label = _label("●  ALL PROCESSING STAYS ON THIS PC", "privacy")
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.privacy_label)
        page.addLayout(footer)

        self.camera_combo.currentIndexChanged.connect(self._camera_selection_changed)

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QWidget#root { background: #111018; color: #f6f2ff; font-family: 'Segoe UI'; }
            QLabel#title { color: #f8f4ff; font-size: 23px; font-weight: 800; letter-spacing: 1px; }
            QLabel#subtitle { color: #8f8a9f; font-size: 10px; font-weight: 700; letter-spacing: 2px; }
            QLabel#badge { color: #9b96a9; background: #1c1a26; border: 1px solid #302c3b; border-radius: 14px; padding: 8px 13px; font-size: 10px; font-weight: 700; }
            QWidget#preview { color: #777286; background: #0b0a10; border: 1px solid #2d2938; border-radius: 18px; }
            QFrame#panel { background: #1b1923; border: 1px solid #302c3b; border-radius: 16px; }
            QScrollArea#controlScroll { background: transparent; border: 0; }
            QLabel#section { color: #8e899d; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
            QLabel#caption { color: #c8c2d4; font-size: 12px; font-weight: 600; }
            QLabel#stat { color: #68f7d5; font-size: 11px; font-weight: 700; }
            QLabel#status { color: #aaa4b6; font-size: 12px; }
            QLabel#privacy { color: #68cdb5; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
            QComboBox { color: #eee9f7; background: #25222f; border: 1px solid #373242; border-radius: 8px; padding: 9px; }
            QComboBox:disabled { color: #797486; }
            QComboBox QAbstractItemView { background: #25222f; color: #eee9f7; selection-background-color: #4a3c5e; }
            QPushButton { color: #eee9f7; background: #2a2734; border: 1px solid #393545; border-radius: 9px; padding: 9px 12px; font-weight: 700; }
            QPushButton:hover { background: #35303f; }
            QPushButton:disabled { color: #726d7e; background: #23212b; }
            QPushButton#primaryButton { color: #101018; background: #68f7d5; border: 0; min-height: 38px; font-size: 13px; }
            QPushButton#primaryButton:hover { background: #8effe3; }
            QPushButton#iconButton { font-size: 16px; padding: 5px; min-width: 32px; }
            QCheckBox { color: #d7d2e1; spacing: 8px; font-size: 12px; }
            QCheckBox::indicator { width: 15px; height: 15px; }
            QCheckBox::indicator:checked { background: #68f7d5; border: 1px solid #68f7d5; border-radius: 4px; }
            QCheckBox::indicator:unchecked { background: #25222f; border: 1px solid #514b5f; border-radius: 4px; }
            QSlider::groove:horizontal { height: 4px; background: #393545; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #68f7d5; border-radius: 2px; }
            QSlider::handle:horizontal { width: 13px; margin: -5px 0; background: #f8f4ff; border-radius: 6px; }
        """)

    def _restore_settings(self) -> None:
        self.mirror_check.setChecked(self.settings.value("mirror", True, type=bool))
        self.effect_check.setChecked(self.settings.value("effect", True, type=bool))
        style_index = self.filter_style_combo.findData(self.settings.value("filter_style", "dots"))
        if style_index >= 0:
            self.filter_style_combo.setCurrentIndex(style_index)
        self.thickness_slider.setValue(self.settings.value("thickness", 3, type=int))
        self.smoothing_slider.setValue(self.settings.value("smoothing", 55, type=int))
        color = self.settings.value("color", "#68F7D5")
        index = self.color_combo.findData(color)
        if index >= 0:
            self.color_combo.setCurrentIndex(index)

    def refresh_cameras(self) -> None:
        if self.scanner and self.scanner.isRunning():
            return
        self.refresh_button.setEnabled(False)
        self.status_label.setText("Scanning for cameras…")
        self.camera_combo.clear()
        self.camera_combo.addItem("Scanning…", None)
        self.scanner = CameraScanner(self)
        self.scanner.scan_complete.connect(self._cameras_found)
        self.scanner.scan_error.connect(lambda error: self.status_label.setText(f"Camera scan: {error}"))
        self.scanner.finished.connect(lambda: self.refresh_button.setEnabled(True))
        self.scanner.start()

    def _cameras_found(self, devices: list) -> None:
        self.devices = devices
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        if devices:
            for index, label in devices:
                self.camera_combo.addItem(label, index)
            self.camera_combo.setEnabled(True)
            self.status_label.setText(f"Found {len(devices)} camera{'s' if len(devices) != 1 else ''}.")
        else:
            self.camera_combo.addItem("No camera detected", None)
            self.camera_combo.setEnabled(False)
            self.status_label.setText("No camera found. Connect a webcam and scan again.")
        self.camera_combo.blockSignals(False)

    def _camera_selection_changed(self, _index: int) -> None:
        if self.worker and self.worker.isRunning():
            self._pending_restart = True
            self.stop_camera()

    def _options(self) -> dict[str, object]:
        stability = self.smoothing_slider.value() / 100
        return {
            "mirror": self.mirror_check.isChecked(),
            "effect": self.effect_check.isChecked(),
            "style": self.filter_style_combo.currentData(),
            "color": self.color_combo.currentData(),
            "thickness": self.thickness_slider.value(),
            "smoothing": max(0.05, 1.0 - stability * 0.82),
        }

    def _push_options(self, *_args) -> None:
        self.settings.setValue("mirror", self.mirror_check.isChecked())
        self.settings.setValue("effect", self.effect_check.isChecked())
        self.settings.setValue("filter_style", self.filter_style_combo.currentData())
        self.settings.setValue("color", self.color_combo.currentData())
        self.settings.setValue("thickness", self.thickness_slider.value())
        self.settings.setValue("smoothing", self.smoothing_slider.value())
        if self.worker and self.worker.isRunning():
            self.worker.set_options(self._options())

    def toggle_camera(self) -> None:
        if self.worker and self.worker.isRunning():
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        camera_index = self.camera_combo.currentData()
        if camera_index is None:
            self.status_label.setText("Choose a detected camera first.")
            return
        model_path = self.project_root / "models" / "face_landmarker.task"
        self._last_error = None
        self.worker = CameraWorker(int(camera_index), model_path, self._options())
        self.worker.status.connect(self._set_status)
        self.worker.failed.connect(self._show_error)
        self.worker.finished.connect(self._worker_finished)
        self.start_button.setText("Stop camera")
        self.refresh_button.setEnabled(False)
        self.live_badge.setText("●  STARTING")
        self.live_badge.setStyleSheet("color: #ffd16b; background: #292316; border-radius: 14px; padding: 8px 13px;")
        self.worker.start()
        self.frame_timer.start()

    def stop_camera(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.start_button.setEnabled(False)
            self.status_label.setText("Releasing camera…")
        else:
            self._worker_finished()

    def _show_frame(self, image, tracks, face_count: int, fps: float) -> None:
        self.preview.set_frame(
            image,
            tracks,
            effect_enabled=self.effect_check.isChecked(),
            style=str(self.filter_style_combo.currentData()),
            color=str(self.color_combo.currentData()),
            thickness=self.thickness_slider.value(),
        )
        self.face_stat.setText(f"{face_count} face{'s' if face_count != 1 else ''}")
        self.fps_stat.setText(f"{fps:.0f} FPS")
        self.live_badge.setText("●  CAMERA LIVE")
        self.live_badge.setStyleSheet("color: #68f7d5; background: #172a27; border-radius: 14px; padding: 8px 13px;")

    def _refresh_preview(self) -> None:
        if not self.worker:
            return
        latest = self.worker.latest_frame()
        if latest is not None:
            self._show_frame(*latest)

    def _set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _show_error(self, message: str) -> None:
        self._last_error = message
        logger.error("Camera error: %s", message)
        self.status_label.setText(message)
        self.live_badge.setText("●  CAMERA ISSUE")
        self.live_badge.setStyleSheet("color: #ff8298; background: #301b24; border-radius: 14px; padding: 8px 13px;")

    def _worker_finished(self) -> None:
        self.frame_timer.stop()
        self.start_button.setEnabled(True)
        self.start_button.setText("Start camera")
        self.refresh_button.setEnabled(True)
        self.camera_combo.setEnabled(bool(self.devices))
        if self._last_error:
            self.status_label.setText(self._last_error)
            self.live_badge.setText("●  CAMERA ISSUE")
            self.live_badge.setStyleSheet("color: #ff8298; background: #301b24; border-radius: 14px; padding: 8px 13px;")
        else:
            self.live_badge.setText("●  CAMERA OFF")
            self.live_badge.setStyleSheet("")
        self.face_stat.setText("0 faces")
        placeholder = (
            "CAMERA ISSUE\n\nCheck camera access and try again"
            if self._last_error
            else "CAMERA STANDBY\n\nPress Start camera to begin"
        )
        self.preview.clear_frame(placeholder)
        if self._pending_restart:
            self._pending_restart = False
            QTimer.singleShot(0, self.start_camera)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.status_label.setText("Waiting for camera to release before closing…")
            if not self.worker.wait(5000):
                event.ignore()
                QMessageBox.warning(self, "Camera is still stopping", "The camera worker has not stopped yet. Wait a moment and close the app again.")
                return
        if self.scanner and self.scanner.isRunning():
            self.scanner.wait(2500)
        self._push_options()
        event.accept()
