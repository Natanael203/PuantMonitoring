import sys
import yaml
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QLabel, QProgressBar, QScrollArea, QTabWidget,
                               QCheckBox, QGroupBox, QMessageBox, QPushButton,
                               QColorDialog, QFileDialog, QSizePolicy,
                               QGridLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QPixmap
from Libs.DataWorker import WebDataWorker
from Libs.Widget import GridDropZone, SensorCard

VERSION = "0.0.5"


class ModernUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PuantMonitor {VERSION}")
        self.setMinimumSize(500, 750)

        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()
        self.movie = None
        self.bg_ratio = None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(base_dir, "parameters", "settings.yaml")

        self.colors = {
            "background": "#000000",
            "group_title": "#00D1FF",
            "progress_fill": "#e5e5e5",
            "sensor_text": "#6d6d6d",
            "pb_background": "#222222",
            "pb_text": "#ffffff",
            "bg_path": ""
        }
        self.selected_names = set()
        self.load_config()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dash_scroll = self.setup_scroll_area("dash_container", is_grid=True)
        self.dash_grid = self.dash_scroll.widget().layout()
        self.tabs.addTab(self.dash_scroll, "Dashboard")

        self.select_scroll = self.setup_scroll_area("select_container")
        self.select_layout = self.select_scroll.widget().layout()
        self.tabs.addTab(self.select_scroll, "Selection")

        self.style_scroll = self.setup_scroll_area("style_container")
        self.style_layout = self.style_scroll.widget().layout()
        self.add_style_section()
        self.tabs.addTab(self.style_scroll, "Style")

        self.widgets = {}
        self.checkboxes = {}
        self.drop_zones = []

        # Création de la grille (10x2)
        self.create_grid_system(10, 3)

        self.apply_theme()

        if self.colors.get("bg_path"):
            self.update_background(self.colors["bg_path"])

        try:
            self.worker = WebDataWorker()
            self.worker.stats_signal.connect(self.update_ui)
            self.worker.start()
        except Exception as e:
            print(f"Worker Error: {e}")

    def create_grid_system(self, rows, cols):
        for r in range(rows):
            for c in range(cols):
                zone = GridDropZone()
                self.dash_grid.addWidget(zone, r, c)
                self.drop_zones.append(zone)

    def setup_scroll_area(self, obj_name, is_grid=False):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        container = QWidget()
        container.setObjectName(obj_name)
        layout = QGridLayout(container) if is_grid else QVBoxLayout(container)
        layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(container)
        return scroll

    def add_style_section(self):
        """Retour de la section Style complète comme avant"""
        self.style_layout.addWidget(QLabel("<b>Couleurs de l'interface</b>"))

        colors_to_edit = [
            ("Animated Background", "background"),
            ("Group Title", "group_title"),
            ("Sensors Names", "sensor_text"),
            ("Progress Bar filling", "progress_fill"),
            ("Progresss Bar Background", "pb_background"),
            ("Progress Bar Value", "pb_text")
        ]

        for label, key in colors_to_edit:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, k=key: self.pick_color(k))
            self.style_layout.addWidget(btn)

        self.style_layout.addWidget(QLabel("<br><b>BackGround(Image or GIF)</b>"))

        btn_bg = QPushButton("Select an image / GIF")
        btn_bg.clicked.connect(self.pick_background)
        self.style_layout.addWidget(btn_bg)

        btn_reset = QPushButton("Reset Background")
        btn_reset.clicked.connect(self.reset_background)
        self.style_layout.addWidget(btn_reset)

    def pick_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colors[key] = color.name()
            self.save_config()
            self.apply_theme()

    def pick_background(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selet Background", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if file_path:
            self.colors["bg_path"] = file_path
            self.save_config()
            self.update_background(file_path)

    def reset_background(self):
        self.colors["bg_path"] = ""
        self.bg_ratio = None
        self.setMinimumSize(500, 750)
        if self.movie: self.movie.stop()
        self.bg_label.setPixmap(QPixmap())
        self.save_config()
        self.apply_theme()

    def update_background(self, path):
        if not os.path.exists(path): return
        if self.movie: self.movie.stop()

        if path.lower().endswith(".gif"):
            self.movie = QMovie(path)
            self.bg_label.setMovie(self.movie)
            self.movie.start()
            self.movie.jumpToFrame(0)
            size = self.movie.currentPixmap().size()
        else:
            pixmap = QPixmap(path)
            self.bg_label.setPixmap(pixmap)
            size = pixmap.size()

        if size.height() > 0:
            self.bg_ratio = size.width() / size.height()
            self.setMinimumSize(100, 100)
            self.resize(self.width(), int(self.width() / self.bg_ratio))
        self.apply_theme()

    def apply_theme(self):
        c = self.colors
        bg_main = "transparent" if c.get("bg_path") else c['background']

        full_style = f"""
            QMainWindow, QTabWidget::pane, QScrollArea, QScrollArea > QWidget,
            #dash_container, #select_container, #style_container {{
                background-color: {bg_main};
                border: none;
            }}
            GridDropZone {{
                background-color: rgba(255, 255, 255, 15);
                border: 1px dashed {c['group_title']}; 
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background-color: #222222; color: #AAAAAA; padding: 10px;
            }}
            QTabBar::tab:selected {{
                background-color: {c['group_title']}; color: black; font-weight: bold;
            }}
            QLabel, QCheckBox {{ 
                color: {c['sensor_text']}; 
                background: transparent; 
            }}
            QPushButton {{ background-color: #333; color: white; border-radius: 5px; padding: 8px; }}
        """
        self.setStyleSheet(full_style)
        for card in self.widgets.values():
            self.apply_card_style(card)

    def apply_card_style(self, card):
        c = self.colors
        card.lbl.setStyleSheet(f"color: {c['sensor_text']}; border: none; font-weight: bold;")
        card.bar.setStyleSheet(f"""
            QProgressBar {{ 
                border: 1px solid #444; 
                border-radius: 4px; 
                text-align: center; 
                color: {c['pb_text']}; 
                background-color: {c['pb_background']}; 
            }}
            QProgressBar::chunk {{ background-color: {c['progress_fill']}; }}
        """)

    def update_ui(self, data):
        if not data: return
        for item in data:
            name, val, unit = item['name'], item['value'], item['unit']
            if name not in self.checkboxes:
                cb = QCheckBox(f"{name} ({unit})")
                cb.setChecked(name in self.selected_names)
                cb.stateChanged.connect(lambda state, n=name: self.toggle_sensor(n, state))
                self.select_layout.addWidget(cb)
                self.checkboxes[name] = cb

            if name in self.selected_names:
                if name not in self.widgets:
                    self.create_sensor_card(name)
                card = self.widgets[name]
                try:
                    v = int(float(val))
                    card.bar.setValue(v)
                    card.bar.setFormat(f"{val} {unit}")
                except:
                    pass
            elif name in self.widgets:
                self.remove_sensor_card(name)

    def create_sensor_card(self, name):
        card = SensorCard(name)
        card.bar.setFixedWidth(250)  # Taille demandée
        for zone in self.drop_zones:
            if zone.layout.count() == 0:
                zone.layout.addWidget(card)
                self.widgets[name] = card
                self.apply_card_style(card)
                break

    def remove_sensor_card(self, name):
        if name in self.widgets:
            card = self.widgets.pop(name)
            card.setParent(None)
            card.deleteLater()

    def toggle_sensor(self, name, state):
        if state == 2:
            self.selected_names.add(name)
        else:
            self.selected_names.discard(name)
        self.save_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    self.selected_names = set(config.get("selected_sensors", []))
                    if "colors" in config: self.colors.update(config["colors"])
            except:
                pass

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                yaml.dump({"selected_sensors": list(self.selected_names), "colors": self.colors}, f)
        except:
            pass

    def resizeEvent(self, event):
        if self.bg_ratio:
            curr_w = self.width()
            curr_h = self.height()
            target_h = int(curr_w / self.bg_ratio)
            if abs(target_h - curr_h) > 5:
                self.resize(curr_w, target_h)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUI()
    window.show()
    sys.exit(app.exec())