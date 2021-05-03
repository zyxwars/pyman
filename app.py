import re
import sys
import json
import requests
from requests.exceptions import RequestException


from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtWebEngineWidgets
from PyQt5 import uic
from PyQt5 import QtWebEngineWidgets
from bs4 import BeautifulSoup

import utils


class MainWidget(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/app.ui', self)
        # Web view not available in qt designer
        self.response_web_view = QtWebEngineWidgets.QWebEngineView()
        self.responseBodyWebLayout.addWidget(self.response_web_view)

        self.reset_request()

        # Signals
        self.sendButton.clicked.connect(self.send)

    def reset_request(self):
        self.requestBody.setPlainText('')
        self.requestHeaders.setPlainText('')

    def parse_body(self):
        body = self.requestBody.toPlainText()
        if not utils.is_json(body):
            return {}
        return utils.json_string_to_python(body)

    def parse_headers(self):
        headers = self.requestHeaders.toPlainText()
        if not utils.is_json(headers):
            return {}
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

        self.responseStatus.setText(f'Status: {r.status_code}')
        self.responseTime.setText(
            f'Time: {r.elapsed.total_seconds() * 1000:.0f} ms')
        self.responseSize.setText(f'Size: {len(r.content) / 1024:.2f} kB')

        # Format html or json body
        if re.match(r'^{.*}$|^\[.*\]$', r.text):
            self.responseBodyPretty.setPlainText(
                utils.format_json_string(r.text))
        else:
            response_html = BeautifulSoup(r.text, 'html.parser')
            self.responseBodyPretty.setPlainText(response_html.prettify())

        self.responseBodyRaw.setPlainText(r.text)
        self.response_web_view.setHtml(r.text)

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
