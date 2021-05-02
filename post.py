import requests


from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtm
from PyQt5 import uic

import utils


class PostWidget(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('./ui/post.ui', self)

        self.url = 'https://608ef5940294cd001765e06b.mockapi.io/api/users'

        self.postButton.clicked.connect(self.post_request)

    def post_request(self):
        headers = utils.json_string_to_python(self.headersEdit.toPlainText())
        content = utils.json_string_to_python(self.contentEdit.toPlainText())

        response = requests.post(self.url, json=content, headers=headers)
        self.responseEdit.setPlainText(utils.format_json_string(response.text))


if __name__ == '__main__':
    app = qtw.QApplication([])

    w = PostWidget()
    w.show()

    app.exec_()
