import os
import sys

import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.latitude = 37.530887
        self.longitude = 55.703118
        self.z = 12

        self.getImage()
        self.initUI()

    def getImage(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        params = {
            'apikey': self.api_key,
            'll': f'{self.latitude},{self.longitude}',
            'z': self.z
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

        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
