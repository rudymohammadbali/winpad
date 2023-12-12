import os
import json

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
FILE_NAME = f'{CURRENT_PATH}\\settings.json'


class SettingsHandler:
    def __init__(self):
        self.filename = FILE_NAME
        self.default_settings = {
            "theme": "system",
            "family": "consolas",
            "style": "normal",
            "size": "11",
            "word_wrap": "word"
        }

    def save_settings(self, new_settings):
        # Load current settings
        settings = self.load_settings()

        # Update settings with new values
        settings.update(new_settings)

        # Save updated settings
        with open(self.filename, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open(self.filename, 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = self.default_settings
        return settings
