
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QLabel, QProgressBar, QScrollArea, QTabWidget,
                               QCheckBox, QGroupBox, QMessageBox, QPushButton,
                               QColorDialog, QFileDialog, QSizePolicy,
                               QGridLayout, QFrame)
class GridDropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 80)
        self.setMaximumHeight(120)
        self.setStyleSheet(
            "border: 1px dashed rgba(255, 255, 255, 40); border-radius: 10px; background: rgba(255,255,255,5);")
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

    def dragEnterEvent(self, event):
        if self.layout.count() == 0:
            self.setStyleSheet("border: 2px solid #00D1FF; background: rgba(0, 209, 255, 20); border-radius: 10px;")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            "border: 1px dashed rgba(255, 255, 255, 40); border-radius: 10px; background: rgba(255,255,255,5);")

    def dropEvent(self, event):
        source = event.source()
        if source:
            self.layout.addWidget(source)
            source.show()
            self.setStyleSheet(
                "border: 1px solid rgba(255, 255, 255, 40); border-radius: 10px; background: transparent;")
            event.acceptProposedAction()


class SensorCard(QFrame):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.lbl = QLabel(name)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-weight: bold; border: none;")

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setFixedHeight(18)
        self.bar.setTextVisible(True)
        self.layout.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.lbl)
        self.layout.addWidget(self.bar)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.position().toPoint())

            self.hide()
            if drag.exec(Qt.MoveAction) == Qt.IgnoreAction:
                self.show()