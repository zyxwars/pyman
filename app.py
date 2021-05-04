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
from bs4 import BeautifulSoup

import utils
from widgets import widgets


class MainWidget(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/app.ui', self)
        self.setWindowTitle('Pyman')

        self.requestBody = widgets.ZoomableTextEdit()
        self.requestBody.setObjectName('requestBody')
        self.requestBodyLayout.addWidget(self.requestBody, 1, 0, 2, 5)
        self.requestHeaders = widgets.ZoomableTextEdit()
        self.requestHeaders.setObjectName('requestHeaders')
        self.requestHeadersLayout.addWidget(self.requestHeaders, 1, 0, 2, 5)
        self.requestCookies = widgets.ZoomableTextEdit()
        self.requestCookies.setObjectName('requestCookies')
        self.requestCookiesLayout.addWidget(self.requestCookies, 1, 0, 2, 5)
        self.requestParameters = widgets.ZoomableTextEdit()
        self.requestParameters.setObjectName('requestParameters')
        self.requestParametersLayout.addWidget(
            self.requestParameters, 1, 0, 2, 5)

        self.responseBodyPretty = widgets.ZoomableTextEdit()
        self.responseBodyPrettyLayout.addWidget(self.responseBodyPretty)
        self.responseBodyRaw = widgets.ZoomableTextEdit()
        self.responseBodyRawLayout.addWidget(self.responseBodyRaw)
        self.responseHeaders = widgets.ZoomableTextEdit()
        self.responseHeadersLayout.addWidget(self.responseHeaders)
        self.responseCookies = widgets.ZoomableTextEdit()
        self.responseCookiesLayout.addWidget(self.responseCookies)

        # Web view not available in qt designer
        self.responseBodyWebView = QtWebEngineWidgets.QWebEngineView()
        self.responseBodyWebLayout.addWidget(self.responseBodyWebView)

        # Load stylesheet after adding extra widgets
        self.setStyleSheet(utils.load_stylesheet('./styles/style.css'))

        # Signals
        self.sendButton.clicked.connect(self.send)

        self.addBodyButton.clicked.connect(self.add_body_item)
        self.addHeadersButton.clicked.connect(self.add_headers_item)
        self.addCookiesButton.clicked.connect(self.add_cookies_item)
        self.addParametersButton.clicked.connect(self.add_parameters_item)

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

    def add_parameters_item(self):
        key = self.parametersKey.text()
        value = self.parametersValue.text()
        current_json = self.requestParameters.toPlainText()
        self.requestParameters.setPlainText(
            utils.add_item_to_json(current_json, key, value))

        url = self.requestUrl.text()
        try:
            url = url[:url.rindex('/')]
        except ValueError:
            pass

        params = utils.json_to_python(self.requestParameters.toPlainText())
        params_list = []
        for key, value in params.items():
            params_list.append(f'{key}={value}')

        self.requestUrl.setText(f'{url}/?{"&".join(params_list)}')

    def reset_request(self):
        self.requestBody.setPlainText('')
        self.requestHeaders.setPlainText('')
        self.requestCookies.setPlainText('')
        self.requestParameters.setPlainText('')

    def reset_response(self):
        self.responseBodyPretty.setPlainText('')
        self.responseBodyRaw.setPlainText('')
        self.responseBodyWebView.setHtml('')
        self.responseHeaders.setPlainText('')
        self.responseCookies.setPlainText('')

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

        params = self.requestParameters.toPlainText()
        params = utils.json_to_python(params)

        return body, headers, cookies, params

    def request(self, method, url, body, headers, cookies, params):
        if not re.match(r'^https?:\/\/', url):
            url = f'{self.requestScheme.currentText().lower()}://{url}'

        try:
            if method == "POST":
                r = requests.post(url, json=body, headers=headers,
                                  cookies=cookies, params=params)
            elif method == "PUT":
                r = requests.put(url, json=body, headers=headers,
                                 cookies=cookies, params=params)
            elif method == "DELETE":
                r = requests.delete(url, json=body, headers=headers,
                                    cookies=cookies, params=params)
            # Make get request default in case something fails
            else:
                r = requests.get(url, json=body, headers=headers,
                                 cookies=cookies, params=params)
        except Exception as e:
            return e

        return r

    def send(self):
        method = self.requestMethod.currentText()
        url = self.requestUrl.text()
        body, headers, cookies, params = self.parse_request()

        self.reset_response()
        response = self.request(method, url, body, headers, cookies, params)

        # Show exception in response field
        if issubclass(type(response), Exception):
            self.responseStatus.setText(f'Status: {type(response).__name__}')
            self.responseBodyPretty.setPlainText(str(response))
            self.responseBodyRaw.setPlainText(str(response))
            return

        self.responseStatus.setText(f'Status: {response.status_code}')
        self.responseTime.setText(
            f'Time: {response.elapsed.total_seconds() * 1000:.0f} ms')
        self.responseSize.setText(
            f'Size: {len(response.content) / 1024:.2f} kB')

        # Format html or json body
        if re.match(r'^{.*}$|^\[.*\]$', response.text):
            self.responseBodyPretty.setPlainText(
                utils.format_json(response.text))
        else:
            response_html = BeautifulSoup(response.text, 'html.parser')
            self.responseBodyPretty.setPlainText(response_html.prettify())

        self.responseBodyRaw.setPlainText(response.text)
        self.responseBodyWebView.setHtml(response.text)

        # headers and cookies return Case insensitive dict
        self.responseHeaders.setPlainText(
            utils.python_to_json(dict(response.headers)))
        self.responseCookies.setPlainText(
            utils.python_to_json(dict(response.cookies)))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    w = MainWidget()
    w.show()

    sys.exit(app.exec_())
