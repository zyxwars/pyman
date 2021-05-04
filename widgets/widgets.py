from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtWebEngineWidgets


class ZoomableTextEdit(qtw.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fontSize = 15

    def wheelEvent(self, event):
        if not qtw.QApplication.keyboardModifiers() == qtc.Qt.ControlModifier:
            return super().wheelEvent(event)

        self.fontSize += int(event.angleDelta().y() / 120)

        if self.fontSize < 1:
            self.fontSize = 1

        self.setStyleSheet(f"""QWidget {{font-size: {self.fontSize}px}}""")
