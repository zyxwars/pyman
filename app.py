import re
import sys
import requests

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
        self.setupUi()

        # Load stylesheet after adding extra widgets
        self.setStyleSheet(utils.load_stylesheet('./styles/style.css'))

        # Signals
        self.sendButton.clicked.connect(self.send)

        self.addBodyButton.clicked.connect(self.add_body_item)
        self.addHeadersButton.clicked.connect(self.add_headers_item)
        self.addCookiesButton.clicked.connect(self.add_cookies_item)
        self.addParametersButton.clicked.connect(self.add_parameters_item)

        self.historyList.itemClicked.connect(
            self.display_request_from_history)

    def setupUi(self):
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

    def parse_request(self):
        method = self.requestMethod.currentText()

        url = self.requestUrl.text().strip()
        if not re.match(r'^https?:\/\/', url):
            url = f'{self.requestScheme.currentText().lower()}://{url}'

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

        return method, url, body, headers, cookies, params

    def request(self, method, url, body, headers, cookies, params):
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
        method, url, body, headers, cookies, params = self.parse_request()
        r = self.request(method, url, body, headers, cookies, params)

        self.clear_response_fields()

        # Show exception in response field
        if issubclass(type(r), Exception):
            self.display_response(type(r).__name__, body=str(r))
            return

        history_item = widgets.RequestHistoryItem(
            method, url, body, headers, cookies, params, r)
        self.historyList.addItem(history_item)
        self.historyList.setItemWidget(history_item, history_item.widget)

        self.display_response(r.status_code, r.elapsed.total_seconds(), len(
            r.content), r.text, dict(r.headers), dict(r.cookies))

    def display_response(self, status: str = '', time_in_seconds: int = 0, size_in_bytes: int = 0, body: str = '', headers: dict = {}, cookies: dict = {}):
        self.responseStatus.setText(f'Status: {status}')
        self.responseTime.setText(f'Time: {time_in_seconds * 1000:.0f} ms')
        self.responseSize.setText(f'Size: {size_in_bytes / 1024:.2f} kB')

        # Format html or json body
        if utils.is_json(body):
            self.responseBodyPretty.setPlainText(utils.format_json(body))
        else:
            response_html = BeautifulSoup(body, 'html.parser')
            self.responseBodyPretty.setPlainText(response_html.prettify())

        self.responseBodyRaw.setPlainText(body)
        self.responseBodyWebView.setHtml(body)

        self.responseHeaders.setPlainText(utils.python_to_json(headers))
        self.responseCookies.setPlainText(utils.python_to_json(cookies))

    def display_request_from_history(self, request_history_item):
        self.requestBody.setPlainText(request_history_item.body)
        self.requestHeaders.setPlainText(request_history_item.headers)
        self.requestCookies.setPlainText(request_history_item.cookies)
        self.requestParameters.setPlainText(request_history_item.params)

        r = request_history_item.response
        self.display_response(r.status_code, r.elapsed.total_seconds(), len(
            r.content), r.text, dict(r.headers), dict(r.cookies))

    def clear_request_fields(self):
        self.requestBody.setPlainText('')
        self.requestHeaders.setPlainText('')
        self.requestCookies.setPlainText('')
        self.requestParameters.setPlainText('')

    def clear_response_fields(self):
        self.responseBodyPretty.setPlainText('')
        self.responseBodyRaw.setPlainText('')
        self.responseBodyWebView.setHtml('')
        self.responseHeaders.setPlainText('')
        self.responseCookies.setPlainText('')


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    w = MainWidget()
    w.show()

    sys.exit(app.exec_())
