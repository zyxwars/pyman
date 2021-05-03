import re
import sys
import json
import requests
from requests.exceptions import RequestException
from requests.structures import CaseInsensitiveDict

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtWebEngineWidgets
from PyQt5 import uic
from PyQt5 import QtWebEngineWidgets
from bs4 import BeautifulSoup

import utils

# https://608ef5940294cd001765e06b.mockapi.io/api/users


class MainWidget(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/app.ui', self)
        # Web view not available in qt designer
        self.response_web_view = QtWebEngineWidgets.QWebEngineView()
        self.responseBodyWebLayout.addWidget(self.response_web_view)

        # Signals
        self.sendButton.clicked.connect(self.send)

        self.addBodyButton.clicked.connect(self.add_body_item)
        self.addHeadersButton.clicked.connect(self.add_headers_item)
        self.addCookiesButton.clicked.connect(self.add_cookies_item)
        self.addArgumentsButton.clicked.connect(self.add_arguments_item)

    def add_body_item(self):
        key = self.bodyKey.text()
        value = self.bodyValue.text()
        current_json = self.requestBody.toPlainText()
        self.requestBody.setPlainText(
            utils.add_item_to_json(current_json, key, value))

    def add_headers_item(self):
        key = self.headersKey.text()
        value = self.headersValue.text()
        current_json = self.requestHeaders.toPlainText()
        self.requestHeaders.setPlainText(
            utils.add_item_to_json(current_json, key, value))

    def add_cookies_item(self):
        key = self.cookiesKey.text()
        value = self.cookiesValue.text()
        current_json = self.requestCookies.toPlainText()
        self.requestCookies.setPlainText(
            utils.add_item_to_json(current_json, key, value))

    def add_arguments_item(self):
        key = self.argumentsKey.text()
        value = self.argumentsValue.text()
        current_json = self.requestArguments.toPlainText()
        self.requestArguments.setPlainText(
            utils.add_item_to_json(current_json, key, value))

        url = self.requestUrl.text()
        try:
            url = url[:url.rindex('/')]
        except ValueError:
            pass

        params = utils.json_to_python(self.requestArguments.toPlainText())
        params_list = []
        for key, value in params.items():
            params_list.append(f'{key}={value}')

        self.requestUrl.setText(f'{url}/?{"&".join(params_list)}')

    def reset_request(self):
        self.requestBody.setPlainText('')
        self.requestHeaders.setPlainText('')
        self.requestCookies.setPlainText('')
        self.requestArguments.setPlainText('')

    def parse_request(self):
        body = self.requestBody.toPlainText()
        body = utils.json_to_python(body)

        headers = self.requestHeaders.toPlainText()
        if not utils.is_json(headers):
            # Show default headers in the requestHeaders field
            self.requestHeaders.setPlainText(utils.python_to_json(
                dict(requests.Session().headers)))
        headers = utils.json_to_python(headers)

        cookies = self.requestCookies.toPlainText()
        cookies = utils.json_to_python(cookies)

        params = self.requestArguments.toPlainText()
        params = utils.json_to_python(params)

        return body, headers, cookies, params

    def send(self):
        method = self.requestMethod.currentText()
        url = self.requestUrl.text()
        body, headers, cookies, params = self.parse_request()

        if method == "POST":
            r = requests.post(url, json=body, headers=headers,
                              cookies=cookies, params=params)
        elif method == "PUT":
            r = requests.put(url, json=body, headers=headers,
                             cookies=cookies, params=params)
        elif method == "DELETE":
            r = requests.delete(url, json=body, headers=headers,
                                cookies=cookies, params=params)
        # Catch impossible errors
        else:
            r = requests.get(url, json=body, headers=headers,
                             cookies=cookies, params=params)

        self.responseStatus.setText(f'Status: {r.status_code}')
        self.responseTime.setText(
            f'Time: {r.elapsed.total_seconds() * 1000:.0f} ms')
        self.responseSize.setText(f'Size: {len(r.content) / 1024:.2f} kB')

        # Format html or json body
        if re.match(r'^{.*}$|^\[.*\]$', r.text):
            self.responseBodyPretty.setPlainText(
                utils.format_json(r.text))
        else:
            response_html = BeautifulSoup(r.text, 'html.parser')
            self.responseBodyPretty.setPlainText(response_html.prettify())

        self.responseBodyRaw.setPlainText(r.text)
        self.response_web_view.setHtml(r.text)

        # headers and cookies return Case insensitive dict
        self.responseHeaders.setPlainText(
            utils.python_to_json(dict(r.headers)))
        self.responseCookies.setPlainText(
            utils.python_to_json(dict(r.cookies)))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    w = MainWidget()
    w.show()

    sys.exit(app.exec_())
