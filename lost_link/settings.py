import os
import json


class Settings:
    KEY_APP_ID = "APP_ID"
    KEY_LOCAL_PATHS = "LOCAL_PATHS"

    _SETTINGS_TEMPLATE: dict[str, str] = {
        KEY_APP_ID: "",
        KEY_LOCAL_PATHS: [

        ]
    }

    def __init__(self, path: str):
        self._settings: dict[str, str] = self._SETTINGS_TEMPLATE

        settings_exists = os.path.exists(path)

        if not settings_exists:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(self._SETTINGS_TEMPLATE, file, ensure_ascii=False, indent=4)
        else:
            with open(path, 'r', encoding='utf-8') as file:
                self._settings = json.load(file)

    def get(self, key: str, default=None):
        return self._settings.get(key, default)
