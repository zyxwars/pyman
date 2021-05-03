import sys
import json
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
        uic.loadUi('./ui/app.ui', self)

        self.reset_request()

        # Signals
        self.sendButton.clicked.connect(self.send)
        self.requestContentType.currentTextChanged.connect(
            self.add_content_type_header)

    @qtc.pyqtSlot(str)
    def add_content_type_header(self, content_type):
        request_headers = self.requestHeaders.toPlainText()
        headers = utils.json_string_to_python(request_headers)
        headers['content-type'] = content_type
        self.requestHeaders.setPlainText(json.dumps(headers, indent=4))

    def reset_request(self):
        self.requestBody.setPlainText('')
        self.requestHeaders.setPlainText('')

    def parse_body(self):
        body = self.requestBody.toPlainText()
        return utils.json_string_to_python(body)

    def parse_headers(self):
        headers = self.requestHeaders.toPlainText()
        return utils.json_string_to_python(headers)

    def parse_cookies(self):
        pass

    def send(self):
        method = self.requestMethod.currentText()
        url = self.requestUrl.text()

        if method == "GET":
            r = requests.get(url, json=self.parse_body(),
                             headers=self.parse_headers())
        elif method == "POST":
            r = requests.post(url, json=self.parse_body(),
                              headers=self.parse_headers())
        elif method == "PUT":
            r = requests.put(url, json=self.parse_body(),
                             headers=self.parse_headers())
        elif method == "DELETE":
            r = requests.delete(url, json=self.parse_body(),
                                headers=self.parse_headers())

        self.responseBody.setPlainText(r.text)
        # headers and cookies return Case insensitive dict
        self.responseHeaders.setPlainText(
            json.dumps(dict(r.headers), indent=4))
        self.responseCookies.setPlainText(
            json.dumps(dict(r.cookies), indent=4))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    w = MainWidget()
    w.show()

    sys.exit(app.exec_())
