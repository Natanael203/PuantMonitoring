import yaml
import os
import requests
import time
from PySide6.QtCore import QThread, Signal


class WebDataWorker(QThread):
    stats_signal = Signal(list)

    def __init__(self):
        super().__init__()
        self.keywords_path = "keywords.yaml"
        self.allowed_keywords = self.load_keywords()

    def load_keywords(self):
        """Charge les mots-clés depuis le fichier YAML."""
        if os.path.exists(self.keywords_path):
            try:
                with open(self.keywords_path, "r") as f:
                    config = yaml.safe_load(f)
                    return config.get("allowed_keywords", [])
            except:
                return ["CPU", "GPU", "Memory"]  # Valeurs par défaut en cas d'erreur
        return ["CPU", "GPU", "Memory"]

    def run(self):
        url = "http://127.0.0.1:8085/data.json"
        while True:
            # On recharge les keywords à chaque cycle pour pouvoir
            # modifier le YAML en direct sans relancer le script !
            self.allowed_keywords = self.load_keywords()

            try:
                response = requests.get(url, timeout=2)
                data = response.json()
                found = []
                self.parse_json(data, found)
                if found:
                    self.stats_signal.emit(found)
            except:
                pass
            time.sleep(1)

    def parse_json(self, node, stats_list):
        text = node.get('Text', '')
        val_str = node.get('Value', '')

        if val_str and any(key in text for key in self.allowed_keywords):
            try:
                clean_v = val_str.replace(',', '.')
                num = float(''.join(c for c in clean_v if c.isdigit() or c == '.'))
                stats_list.append({
                    'name': text,
                    'value': num,
                    'unit': val_str.split(' ')[-1]
                })
            except:
                pass

        children = node.get('Children', [])
        for child in children:
            self.parse_json(child, stats_list)