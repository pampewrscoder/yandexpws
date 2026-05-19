import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

SCREEN_SIZE = [600, 500]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QLabel(self)
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Искать', self)
        self.reset_button = QPushButton('Сброс', self)

        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.latitude = 37.530887
        self.longitude = 55.703118
        self.z = 12
        self.theme = 'light'
        self.marker = None
        self.search_input.clear()

        self.getImage()
        self.initUI()
        self.updateImage()

    def getImage(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        params = {
            'apikey': self.api_key,
            'll': f'{self.longitude},{self.latitude}',
            'z': self.z,
            'theme': self.theme
        }
        if self.marker:
            params['pt'] = self.marker

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

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.search_input)
        control_layout.addWidget(self.search_button)
        control_layout.addWidget(self.reset_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.image)

        self.setLayout(main_layout)

        self.search_button.clicked.connect(self.search_object)
        self.search_input.returnPressed.connect(self.search_object)
        self.reset_button.clicked.connect(self.reset_marker)

    def search_object(self):
        query = self.search_input.text().strip()
        if not query:
            return

        geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'apikey': self.api_key,
            'geocode': query,
            'format': 'json'
        }

        response = requests.get(url=geocoder_url, params=params)
        if not response or response.status_code != 200:
            print("Ошибка геокодирования")
            return

        data = response.json()
        try:
            pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            lon, lat = pos.split()
            self.longitude = float(lon)
            self.latitude = float(lat)
            self.z = 10
            self.marker = f'{self.longitude},{self.latitude},pm2rdm'
            self.getImage()
            self.updateImage()
        except (KeyError, IndexError):
            print("Объект не найден")

    def reset_marker(self):
        self.marker = None
        self.search_input.clear()
        self.getImage()
        self.updateImage()

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
            if self.latitude < 85:
                self.latitude += 0.1
            else:
                self.latitude = 85
            self.getImage()
            self.updateImage()
        if event.key() == Qt.Key.Key_Down:
            if self.latitude > -85:
                self.latitude -= 0.1
            else:
                self.latitude = -85
            self.getImage()
            self.updateImage()

        if event.key() == Qt.Key.Key_Left:
            if self.longitude > -180:
                self.longitude -= 0.1
            else:
                self.longitude = -180
            self.getImage()
            self.updateImage()
        if event.key() == Qt.Key.Key_Right:
            if self.longitude < 180:
                self.longitude += 0.1
            else:
                self.longitude = 180
            self.getImage()
            self.updateImage()

        if event.key() == Qt.Key.Key_R:
            if self.theme == 'light':
                self.theme = 'dark'
            else:
                self.theme = 'light'
            self.getImage()
            self.updateImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
