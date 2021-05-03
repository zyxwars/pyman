import requests
from requests.exceptions import RequestException


from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import uic

import utils


class MainWidget(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi()

    def setupUi(self):
        self.setObjectName('Form')
        layout = qtw.QGridLayout(self)

        requestWidget = qtw.QWidget()
        self.requestButton = qtw.QPushButton('POST')

        contentWidget = qtw.QWidget()
        contentLayout = qtw.QGridLayout(contentWidget)
        self.contentTypeCombo = qtw.QComboBox()
        self.contentTypeCombo.addItem('application/json')
        self.contentTypeCombo.addItem('application/x-www-form-urlencoded')
        self.contentTypeCombo.addItem('multipart/form-data')
        self.contentEdit = qtw.QPlainTextEdit()
        contentLayout.addWidget(self.contentTypeCombo)
        contentLayout.addWidget(self.contentEdit)

        headersWidget = qtw.QWidget()
        headersLayout = qtw.QGridLayout(headersWidget)
        self.headersEdit = qtw.QPlainTextEdit()
        headersLayout.addWidget(self.headersEdit)

        cookiesWidget = qtw.QWidget()
        cookiesLayout = qtw.QGridLayout(cookiesWidget)
        self.cookiesEdit = qtw.QPlainTextEdit()
        cookiesLayout.addWidget(self.cookiesEdit)

        requestTab = qtw.QTabWidget()
        requestTab.addTab(contentWidget, 'Content')
        requestTab.addTab(headersWidget, 'Headers')
        requestTab.addTab(cookiesWidget, 'Cookies')

        requestLayout = qtw.QGridLayout(requestWidget)
        requestLayout.addWidget(qtw.QLabel('Request'), 0, 0)
        requestLayout.addWidget(self.requestButton, 0, 1)
        requestLayout.addWidget(requestTab, 1, 0, 1, 2)

        responseWidget = qtw.QWidget()
        self.responseEdit = qtw.QPlainTextEdit()

        responseLayout = qtw.QGridLayout(responseWidget)
        responseLayout.addWidget(qtw.QLabel('Response'))
        responseLayout.addWidget(self.responseEdit)

        splitter = qtw.QSplitter(qtc.Qt.Vertical)
        splitter.addWidget(requestWidget)
        splitter.addWidget(responseWidget)
        layout.addWidget(splitter)


if __name__ == '__main__':
    app = qtw.QApplication([])

    w = MainWidget()
    w.show()

    app.exec_()
