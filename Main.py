import sys
import requests
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QProgressBar, QScrollArea
from PySide6.QtCore import QThread, Signal, Qt


class WebDataWorker(QThread):
    stats_signal = Signal(list)

    def run(self):
        url = "http://127.0.0.1:8085/data.json"
        while True:
            try:
                response = requests.get(url, timeout=2)
                data = response.json()
                extracted_stats = []
                self.parse_json(data, extracted_stats)

                if extracted_stats:
                    # Envoi des données vers l'interface
                    self.stats_signal.emit(extracted_stats)
                else:
                    print(" Données reçues mais aucun capteur correspondant trouvé.")
            except Exception as e:
                print(f" Erreur de connexion au serveur LHM : {e}")
            time.sleep(1)

    def parse_json(self, node, stats_list):
        text = node.get('Text', '')
        sensor_type = node.get('SensorType', '')
        value_str = node.get('Value', '')

        important_keywords = ['CPU Total', 'CPU Package', 'Memory', 'GPU Core', 'Charge Level']

        if value_str and any(key in text for key in important_keywords):
            try:
                # Nettoyage de la valeur (ex: "69,0 °C" -> 69.0)
                clean_val = value_str.replace(',', '.')
                clean_val = ''.join(c for c in clean_val if c.isdigit() or c == '.')
                val_float = float(clean_val)

                stats_list.append({
                    'name': text,
                    'value': val_float,
                    'type': sensor_type,
                    'unit': value_str.split(' ')[-1]
                })
            except:
                pass

        for child in node.get('Children', []):
            self.parse_json(child, stats_list)


class ModernUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSI Monitor - Live")
        self.setMinimumSize(400, 500)
        self.setStyleSheet("QMainWindow { background-color: #121212; }")

        # Configuration de l'affichage
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        self.setCentralWidget(self.scroll)

        self.widgets = {}

        self.worker = WebDataWorker()
        self.worker.stats_signal.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, data):
        for item in data:
            name = item['name']
            val = item['value']
            unit = item['unit']

            if name not in self.widgets:
                lbl = QLabel(f"<b>{name}</b>")
                lbl.setStyleSheet("color: #00D1FF; font-size: 13px; margin-top: 10px;")
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setFixedHeight(25)
                bar.setStyleSheet("""
                    QProgressBar { border: 1px solid #333; border-radius: 5px; text-align: center; color: white; background: #222; }
                    QProgressBar::chunk { background-color: #00D1FF; border-radius: 4px; }
                """)
                self.layout.addWidget(lbl)
                self.layout.addWidget(bar)
                self.widgets[name] = bar

            # Mise à jour
            self.widgets[name].setValue(int(val))
            self.widgets[name].setFormat(f"{val} {unit}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUI()
    window.show()
    sys.exit(app.exec())