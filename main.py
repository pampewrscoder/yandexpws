import os
import sys
import math

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout

SCREEN_SIZE = [600, 500]


class ClickableLabel(QLabel):
    clicked = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked = None


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.image = ClickableLabel(self)
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Искать', self)
        self.reset_button = QPushButton('Сброс', self)
        self.address_label = QLabel(self)
        self.postcode_checkbox = QCheckBox('Добавить почтовый индекс', self)
        self.click_longitude = None
        self.click_latitude = None

        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.latitude = 37.530887
        self.longitude = 55.703118
        self.z = 12
        self.theme = 'light'
        self.marker = None
        self.postcode = None
        self.base_address = None
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
        control_layout.addWidget(self.postcode_checkbox)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.address_label)
        main_layout.addWidget(self.image)

        self.setLayout(main_layout)

        self.search_button.clicked.connect(self.search_object)
        self.search_input.returnPressed.connect(self.search_object)
        self.reset_button.clicked.connect(self.reset_marker)
        self.postcode_checkbox.stateChanged.connect(self.toggle_postcode)
        self.image.mousePressEvent = self.on_map_click

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
            geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            pos = geo_object['Point']['pos']
            self.base_address = geo_object['metaDataProperty']['GeocoderResponseMetaData']['text']
            try:
                self.postcode = geo_object['metaDataProperty']['GeocoderResponseMetaData']['Address']['postal_code']
            except (KeyError, TypeError):
                self.postcode = None

            address = self.base_address
            if self.postcode_checkbox.isChecked() and self.postcode:
                address = f"{address}, {self.postcode}"

            lon, lat = pos.split()
            self.longitude = float(lon)
            self.latitude = float(lat)
            self.z = 10
            self.marker = f'{self.longitude},{self.latitude},pm2rdm'
            self.address_label.setText(address)
            self.getImage()
            self.updateImage()
        except (KeyError, IndexError):
            print("Объект не найден")

    def toggle_postcode(self):
        if self.base_address and self.postcode:
            address = self.base_address
            if self.postcode_checkbox.isChecked():
                address = f"{address}, {self.postcode}"
            self.address_label.setText(address)

    def on_map_click(self, event):
        x = event.position().x()
        y = event.position().y()

        width = self.image.width()
        height = self.image.height()

        dx = (x - width / 2) / (width / 2)
        dy = (height / 2 - y) / (height / 2)

        n = 2 ** self.z
        lon_per_pixel = 360 / (256 * n)
        click_lon = self.longitude + dx * (128 * n) * lon_per_pixel

        lat_per_pixel = 180 / (128 * n)
        click_lat = self.latitude + dy * (128 * n) * lat_per_pixel

        if event.button() == Qt.MouseButton.LeftButton:
            self.click_longitude = click_lon
            self.click_latitude = click_lat
            self.reverse_geocode(self.click_longitude, self.click_latitude)
        elif event.button() == Qt.MouseButton.RightButton:
            self.search_organization(click_lon, click_lat)

    def reverse_geocode(self, lon, lat):
        geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'apikey': self.api_key,
            'geocode': f'{lon},{lat}',
            'format': 'json'
        }

        response = requests.get(url=geocoder_url, params=params)
        if not response or response.status_code != 200:
            print("Ошибка геокодирования")
            return

        data = response.json()
        try:
            geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            self.base_address = geo_object['metaDataProperty']['GeocoderResponseMetaData']['text']
            try:
                self.postcode = geo_object['metaDataProperty']['GeocoderResponseMetaData']['Address']['postal_code']
            except (KeyError, TypeError):
                self.postcode = None

            address = self.base_address
            if self.postcode_checkbox.isChecked() and self.postcode:
                address = f"{address}, {self.postcode}"

            self.marker = f'{lon},{lat},pm2rdm'
            self.address_label.setText(address)
            self.getImage()
            self.updateImage()
        except (KeyError, IndexError):
            print("Объект не найден")

    def search_organization(self, lon, lat):
        self.marker = None
        self.postcode = None
        self.base_address = None
        self.search_input.clear()
        self.address_label.clear()

        search_url = "https://search-maps.yandex.ru/v1/"
        params = {
            'apikey': self.api_key,
            'text': '',
            'll': f'{lon},{lat}',
            'spn': '0.005,0.005',
            'type': 'biz',
            'results': 1
        }

        response = requests.get(url=search_url, params=params)
        if not response or response.status_code != 200:
            print("Ошибка поиска организаций")
            return

        data = response.json()
        try:
            feature = data['features'][0]
            org_point = feature['geometry']['coordinates']
            org_lon, org_lat = org_point[0], org_point[1]

            distance = self.calculate_distance(lon, lat, org_lon, org_lat)

            if distance <= 50:
                self.base_address = feature['properties']['name']
                address_details = feature.get('properties', {}).get('description', '')
                if address_details:
                    self.base_address = f"{self.base_address}, {address_details}"

                try:
                    self.postcode = feature['properties']['CompanyMetaData'].get('address', {}).get('postal_code')
                except (KeyError, AttributeError):
                    self.postcode = None

                address = self.base_address
                if self.postcode_checkbox.isChecked() and self.postcode:
                    address = f"{address}, {self.postcode}"

                self.marker = f'{org_lon},{org_lat},pm2rdm'
                self.address_label.setText(address)
                self.getImage()
                self.updateImage()
        except (KeyError, IndexError):
            pass

    def calculate_distance(self, lon1, lat1, lon2, lat2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def reset_marker(self):
        self.marker = None
        self.postcode = None
        self.base_address = None
        self.click_longitude = None
        self.click_latitude = None
        self.search_input.clear()
        self.address_label.clear()
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
