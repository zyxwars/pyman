import datetime

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtWebEngineWidgets

import utils


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


class RequestHistoryItem(qtw.QListWidgetItem):
    def __init__(self, method, url, body, headers, cookies, params, response, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method = method
        self.body = utils.python_to_json(body)
        self.headers = utils.python_to_json(headers)
        self.cookies = utils.python_to_json(cookies)
        self.params = utils.python_to_json(params)
        self.response = response

        self.widget = qtw.QWidget()
        self.widget.setObjectName('historyItem')
        layout = qtw.QVBoxLayout(self.widget)

        layout.addWidget(qtw.QLabel(self.response.url))
        layout.addWidget(qtw.QLabel(str(datetime.datetime.now())))

        self.setSizeHint(self.widget.sizeHint())
