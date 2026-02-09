import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.uic.Compiler.qtproxies import QtCore

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QLabel(self)

        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.latitude = 37.530887
        self.longitude = 55.703118
        self.z = 12
        self.theme = 'light'

        self.getImage()
        self.initUI()
        self.updateImage()

    def getImage(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        params = {
            'apikey': self.api_key,
            'll': f'{self.latitude},{self.longitude}',
            'z': self.z,
            'theme': self.theme
        }
        response = requests.get(url=server_address, params=params)

        if not response:
            print("Ошибка выполнения запроса")
            print(response.text)
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

    def updateImage(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            if self.z < 21:
                self.z += 1
            else:
                self.z = 21
            self.getImage()
            self.updateImage()
        if event.key() == Qt.Key.Key_PageDown:
            if self.z > 0:
                self.z -= 1
            else:
                self.z = 0
            self.getImage()
            self.updateImage()

        if event.key() == Qt.Key.Key_Up:
            if self.longitude < 90:
                self.longitude += 0.1
            else:
                self.longitude = 90
            self.getImage()
            self.updateImage()
        if event.key() == Qt.Key.Key_Down:
            if self.longitude > -90:
                self.longitude -= 0.1
            else:
                self.longitude = -90
            self.getImage()
            self.updateImage()

        if event.key() == Qt.Key.Key_Left:
            if self.latitude > -180:
                self.latitude -= 0.1
            else:
                self.latitude = -180
            self.getImage()
            self.updateImage()
        if event.key() == Qt.Key.Key_Right:
            if self.latitude < 180:
                self.latitude += 0.1
            else:
                self.latitude = 180
            self.getImage()
            self.updateImage()

        if event.key() == Qt.Key.Key_R:
            pass

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
