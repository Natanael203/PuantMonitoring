import sys
import yaml
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QLabel, QProgressBar, QScrollArea, QTabWidget,
                               QCheckBox, QGroupBox, QMessageBox, QPushButton, QColorDialog)
from PySide6.QtCore import Qt
from Libs.DataWorker import WebDataWorker

VERSION = "0.0.4_Dev"


class ModernUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PuantMonitor {VERSION}")
        self.setMinimumSize(500, 750)

        # --- CONFIGURATION DES CHEMINS ---
        self.config_path = "parameters/settings.yaml"
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur Système", f"Impossible de créer le dossier de configuration :\n{e}")

        self.colors = {
            "background": "#000000",
            "group_title": "#00D1FF",
            "progress_fill": "#e5e5e5",
            "sensor_text": "#6d6d6d",
            "pb_background": "#222222",
            "pb_text": "#ffffff"
        }
        self.selected_names = set()

        self.load_config()

        # --- STRUCTURE ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dash_scroll = self.setup_scroll_area("dash_container")
        self.dash_layout = self.dash_scroll.widget().layout()
        self.tabs.addTab(self.dash_scroll, "Dashboard")

        self.select_scroll = self.setup_scroll_area("select_container")
        self.select_layout = self.select_scroll.widget().layout()
        self.tabs.addTab(self.select_scroll, "Selection")

        self.style_scroll = self.setup_scroll_area("style_container")
        self.style_layout = self.style_scroll.widget().layout()
        self.add_style_section()
        self.tabs.addTab(self.style_scroll, "Style")

        self.groups = {}
        self.widgets = {}
        self.checkboxes = {}

        self.apply_theme()

        # --- INITIALISATION DU WORKER ---
        try:
            self.worker = WebDataWorker()
            self.worker.stats_signal.connect(self.update_ui)
            self.worker.start()
        except Exception as e:
            QMessageBox.warning(self, "Erreur de Connexion",
                                f"Le Worker de données n'a pas pu démarrer.\n"
                                f"Vérifiez que le serveur MSI est actif.\n\nDétails : {e}")

    def setup_scroll_area(self, obj_name):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setObjectName(obj_name)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(container)
        return scroll

    def add_style_section(self):
        lbl = QLabel("Choose color")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: white;")
        self.style_layout.addWidget(lbl)

        colors_to_edit = [
            ("Background", "background"),
            ("Group Title", "group_title"),
            ("Sensor Names", "sensor_text"),
            ("--- Progress Bars  ---", None),
            ("Filling Color", "progress_fill"),
            ("Background Color", "pb_background"),
            ("Value", "pb_text")
        ]

        for label, key in colors_to_edit:
            if key is None:
                self.style_layout.addWidget(QLabel(f"\n{label}"))
                continue
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.pick_color(k))
            self.style_layout.addWidget(btn)

    def pick_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colors[key] = color.name()
            self.save_config()
            self.apply_theme()

    def apply_theme(self):
        c = self.colors
        full_style = f"""
            QMainWindow, QTabWidget::pane, QScrollArea, QScrollArea > QWidget,
            #dash_container, #select_container, #style_container {{
                background-color: {c['background']};
                border: none;
            }}
            QTabBar::tab {{
                background-color: #222222;
                color: #AAAAAA;
                padding: 10px;
                min-width: 110px;
                border: 1px solid #333;
            }}
            QTabBar::tab:selected {{
                background-color: #d0d0d0;
                color: black;
                font-weight: bold;
            }}
            QGroupBox {{ 
                border: 2px solid #333; 
                border-radius: 8px; 
                margin-top: 20px; 
                font-weight: bold; 
                color: {c['group_title']};
                padding-top: 15px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
            QLabel {{ color: {c['sensor_text']}; background: transparent; }}
            QCheckBox {{ color: {c['sensor_text']}; background: transparent; }}
            QPushButton {{ 
                background-color: #333; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
            }}
        """
        self.setStyleSheet(full_style)

        for name, w in self.widgets.items():
            w['lbl'].setStyleSheet(f"color: {c['sensor_text']}; font-weight: bold;")
            w['bar'].setStyleSheet(f"""
                QProgressBar {{ 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                    text-align: center; 
                    color: {c['pb_text']}; 
                    background-color: {c['pb_background']}; 
                }}
                QProgressBar::chunk {{ background-color: {c['progress_fill']}; }}
            """)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    self.selected_names = set(config.get("selected_sensors", []))
                    if "colors" in config:
                        self.colors.update(config["colors"])
            except Exception as e:
                QMessageBox.warning(self, "Erreur de Configuration",
                                    f"Impossible de lire le fichier de config.\n"
                                    f"Le fichier est peut-être corrompu.\n\nErreur : {e}")

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                yaml.dump({"selected_sensors": list(self.selected_names), "colors": self.colors}, f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Sauvegarde",
                                 f"Impossible d'enregistrer vos paramètres :\n{e}")

    def get_category_info(self, name):
        n = name.lower()
        if "cpu" in n: return "CPU"
        if "gpu" in n or "nvidia" in n: return "GPU"
        if "memory" in n or "ram" in n: return "RAM"
        if "fan" in n: return "VENTILATION"
        return "Other"

    def update_ui(self, data):
        # Sécurité : Si data est vide ou mal formé
        if not data:
            return

        for item in data:
            try:
                name, val, unit = item['name'], item['value'], item['unit']

                if name not in self.checkboxes:
                    cb = QCheckBox(f"{name} ({unit})")
                    if name in self.selected_names: cb.setChecked(True)
                    cb.stateChanged.connect(lambda state, n=name: self.toggle_sensor(n, state))
                    self.select_layout.addWidget(cb)
                    self.checkboxes[name] = cb

                if name in self.selected_names:
                    if name not in self.widgets: self.create_bar(name)
                    # Sécurité conversion en entier pour la barre
                    try:
                        self.widgets[name]['bar'].setValue(int(float(val)))
                        self.widgets[name]['bar'].setFormat(f"{val} {unit}")
                    except:
                        pass
                elif name in self.widgets:
                    self.remove_bar(name)
            except KeyError as e:
                print(f"Donnée manquante dans le flux : {e}")

    def toggle_sensor(self, name, state):
        if state == 2:
            self.selected_names.add(name)
        else:
            self.selected_names.discard(name)
        self.save_config()

    def create_bar(self, name):
        cat_name = self.get_category_info(name)
        if cat_name not in self.groups:
            group = QGroupBox(cat_name)
            layout = QVBoxLayout(group)
            self.dash_layout.addWidget(group)
            self.groups[cat_name] = (group, layout)

        target_layout = self.groups[cat_name][1]
        lbl = QLabel(name)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setFixedHeight(22)
        target_layout.addWidget(lbl)
        target_layout.addWidget(bar)
        self.widgets[name] = {'bar': bar, 'lbl': lbl, 'cat': cat_name}
        self.apply_theme()

    def remove_bar(self, name):
        if name in self.widgets:
            info = self.widgets.pop(name)
            info['bar'].deleteLater()
            info['lbl'].deleteLater()
            cat = info['cat']
            if cat in self.groups:
                layout = self.groups[cat][1]
                if layout.count() == 0:
                    group_box = self.groups.pop(cat)[0]
                    group_box.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUI()
    window.show()
    sys.exit(app.exec())