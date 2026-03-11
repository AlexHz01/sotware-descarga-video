import os
import json

class ConfigManager:
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "theme": "Dark",
        "color_theme": "blue",
        "download_path": os.path.expanduser("~\\Downloads"),
        "last_quality": "1080p",
        "last_format": "MP4"
    }

    @staticmethod
    def load_config():
        if os.path.exists(ConfigManager.CONFIG_FILE):
            try:
                with open(ConfigManager.CONFIG_FILE, "r") as f:
                    return {**ConfigManager.DEFAULT_CONFIG, **json.load(f)}
            except:
                return ConfigManager.DEFAULT_CONFIG
        return ConfigManager.DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(ConfigManager.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
