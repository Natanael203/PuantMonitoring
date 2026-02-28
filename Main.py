import sys
import yaml
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QLabel, QProgressBar, QScrollArea, QTabWidget, QCheckBox)
from PySide6.QtCore import Qt
from Libs.DataWorker import WebDataWorker


class ModernUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSI Monitor - Auto Save")
        self.setMinimumSize(450, 600)
        self.setStyleSheet("QMainWindow { background-color: #121212; color: white; }")

        # --- CHARGEMENT INITIAL DU CONFIG.YAML ---
        self.config_path = "parameters/settings.yaml"
        self.selected_names = self.load_config()

        # 1. Création des Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #222; color: white; padding: 8px; } "
                                "QTabBar::tab:selected { background: #00D1FF; color: black; }")
        self.setCentralWidget(self.tabs)

        # Onglet DASHBOARD
        self.dash_scroll = QScrollArea()
        self.dash_container = QWidget()
        self.dash_layout = QVBoxLayout(self.dash_container)
        self.dash_layout.setAlignment(Qt.AlignTop)
        self.dash_scroll.setWidget(self.dash_container)
        self.dash_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.dash_scroll, "Dashboard")

        # Onglet SÉLECTION
        self.select_scroll = QScrollArea()
        self.select_container = QWidget()
        self.select_layout = QVBoxLayout(self.select_container)
        self.select_layout.setAlignment(Qt.AlignTop)
        self.select_scroll.setWidget(self.select_container)
        self.select_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.select_scroll, "⚙️ Sélection")

        # Stockage
        self.widgets = {}  # {nom: {'bar': QProgressBar, 'lbl': QLabel}}
        self.checkboxes = {}  # {nom: QCheckBox}

        # Lancement du Worker
        self.worker = WebDataWorker()
        self.worker.stats_signal.connect(self.update_ui)
        self.worker.start()

    def load_config(self):
        """Lit le fichier YAML au démarrage."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f)
                    return set(config.get("selected_sensors", []))
            except:
                return set()
        return set()

    def save_config(self):
        """Enregistre les capteurs sélectionnés dans le YAML."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump({"selected_sensors": list(self.selected_names)}, f)
        except Exception as e:
            print(f"Erreur sauvegarde : {e}")

    def update_ui(self, data):
        for item in data:
            name = item['name']
            val = item['value']
            unit = item['unit']

            # A. Création de la case à cocher (Onglet Sélection)
            if name not in self.checkboxes:
                cb = QCheckBox(f"{name} ({unit})")
                cb.setStyleSheet("color: #AAA; padding: 3px;")
                # Si le nom était déjà dans le YAML, on coche la case
                if name in self.selected_names:
                    cb.setChecked(True)

                cb.stateChanged.connect(lambda state, n=name: self.toggle_sensor(n, state))
                self.select_layout.addWidget(cb)
                self.checkboxes[name] = cb

            # B. Affichage sur le Dashboard si sélectionné
            if name in self.selected_names:
                if name not in self.widgets:
                    self.create_bar(name)

                self.widgets[name]['bar'].setValue(int(val))
                self.widgets[name]['bar'].setFormat(f"{val} {unit}")

            # C. Suppression si décoché
            elif name in self.widgets:
                self.remove_bar(name)

    def toggle_sensor(self, name, state):
        """Action déclenchée quand on clique sur une Checkbox."""
        if state == 2:  # Checkbox cochée
            self.selected_names.add(name)
        else:  # Checkbox décochée
            self.selected_names.discard(name)

        # On sauvegarde les nouveaux choix immédiatement
        self.save_config()

    def create_bar(self, name):
        lbl = QLabel(f"<b>{name}</b>")
        lbl.setStyleSheet("color: #00D1FF; margin-top: 8px;")
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setFixedHeight(22)
        bar.setStyleSheet("""
            QProgressBar { border: 1px solid #333; border-radius: 4px; text-align: center; color: white; background: #222; }
            QProgressBar::chunk { background-color: #00D1FF; }
        """)
        self.dash_layout.addWidget(lbl)
        self.dash_layout.addWidget(bar)
        self.widgets[name] = {'bar': bar, 'lbl': lbl}

    def remove_bar(self, name):
        w = self.widgets.pop(name)
        w['bar'].deleteLater()
        w['lbl'].deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUI()
    window.show()
    sys.exit(app.exec())